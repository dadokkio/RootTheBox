#!/usr/bin/env python3
"""
CTF Challenge Spawner
Avvia container Docker effimeri per ogni giocatore e fa da reverse proxy.
Nessun numero di porta esposto nei URL: accesso tramite token UUID.
"""

import logging
import os
import re
import threading
import time
import uuid
from typing import Optional

import docker
import requests as http_requests
from flask import Flask, Response, jsonify, make_response, redirect, render_template_string, request
from werkzeug.exceptions import NotFound

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

docker_client = docker.from_env()

# ---------------------------------------------------------------------------
# Configurazione challenge: nome → immagine Docker
# ---------------------------------------------------------------------------
CHALLENGE_IMAGES: dict[str, str] = {
    "sqli": os.environ.get("SQLI_IMAGE", "ctf-sqli:latest"),
    # aggiungi altri: "xss": "ctf-xss:latest", ...
}

INSTANCE_TTL = int(os.environ.get("INSTANCE_TTL", 3600))   # secondi
CLEANUP_INTERVAL = 60                                        # secondi tra i cleanup
CTF_NETWORK = os.environ.get("CTF_NETWORK", "ctf-challenges")
CONTAINER_PORT = 80                                          # porta interna del container
MAX_TOTAL_INSTANCES = int(os.environ.get("MAX_TOTAL_INSTANCES", 20))

# ---------------------------------------------------------------------------
# Registry in-memory: instance_id → {container_id, ip, user_key, challenge, ...}
# ---------------------------------------------------------------------------
registry: dict[str, dict] = {}
registry_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Helpers Docker
# ---------------------------------------------------------------------------

def ensure_network() -> None:
    try:
        docker_client.networks.get(CTF_NETWORK)
    except docker.errors.NotFound:
        docker_client.networks.create(CTF_NETWORK, driver="bridge", internal=True)
        logger.info("Rete %s creata", CTF_NETWORK)


def get_container_ip(container, network_name: str) -> Optional[str]:
    container.reload()
    return (
        container.attrs["NetworkSettings"]["Networks"]
        .get(network_name, {})
        .get("IPAddress")
    )


def start_container(challenge: str) -> tuple[str, str]:
    """Avvia un container per la sfida e restituisce (container_id, ip)."""
    ensure_network()
    image = CHALLENGE_IMAGES[challenge]
    container = docker_client.containers.run(
        image,
        detach=True,
        network=CTF_NETWORK,
        mem_limit=os.environ.get("CONTAINER_MEM", "128m"),
        cpu_quota=int(os.environ.get("CONTAINER_CPU_QUOTA", "50000")),
        read_only=False,
        remove=True,
        labels={"ctf.spawner": "true", "ctf.challenge": challenge},
    )
    ip = get_container_ip(container, CTF_NETWORK)
    if not ip:
        container.stop(timeout=3)
        raise RuntimeError("Impossibile ottenere IP del container")
    logger.info("Container %s avviato per %s @ %s", container.short_id, challenge, ip)
    return container.id, ip


def stop_container(container_id: str) -> None:
    try:
        c = docker_client.containers.get(container_id)
        c.stop(timeout=5)
    except docker.errors.NotFound:
        pass
    except Exception as exc:
        logger.warning("Errore stop container %s: %s", container_id[:12], exc)


# ---------------------------------------------------------------------------
# Cleanup in background
# ---------------------------------------------------------------------------

def _cleanup_loop() -> None:
    while True:
        time.sleep(CLEANUP_INTERVAL)
        now = time.time()
        with registry_lock:
            expired = [
                iid
                for iid, info in registry.items()
                if now - info["created_at"] > info["ttl"]
            ]
        for iid in expired:
            _destroy_instance(iid)
            logger.info("Istanza %s scaduta e rimossa", iid[:8])


def _destroy_instance(instance_id: str) -> None:
    with registry_lock:
        info = registry.pop(instance_id, None)
    if info:
        stop_container(info["container_id"])


def _startup_cleanup() -> None:
    """All'avvio ferma tutti i container sfida orfani (registry era in-memory)."""
    try:
        orphans = docker_client.containers.list(filters={"label": "ctf.spawner=true"})
        for c in orphans:
            c.stop(timeout=5)
            logger.info("Container orfano %s fermato all'avvio", c.short_id)
    except Exception as exc:
        logger.warning("Errore cleanup avvio: %s", exc)

_startup_cleanup()

cleanup_thread = threading.Thread(target=_cleanup_loop, daemon=True)
cleanup_thread.start()


# ---------------------------------------------------------------------------
# Identificazione utente (usa cookie RTB session_id se presente, altrimenti IP)
# ---------------------------------------------------------------------------

def get_player_id() -> tuple[str, bool]:
    """
    Restituisce (player_id, is_new).
    Priorità: parametro URL 'pid' > cookie ctf_player_id > nuovo UUID.
    Il pid nell'URL è il meccanismo primario: garantisce coerenza anche
    quando i cookie di iframe vengono bloccati dai browser moderni.
    """
    pid = request.args.get("pid", "") or request.cookies.get("ctf_player_id", "")
    if pid and re.match(r'^[0-9a-f-]{36}$', pid):
        return pid, False
    return str(uuid.uuid4()), True


def set_player_cookie(response, player_id: str):
    response.set_cookie(
        "ctf_player_id",
        player_id,
        max_age=30 * 24 * 3600,
        httponly=True,
        samesite="Lax",
        secure=True,
    )
    return response


def get_user_key() -> str:
    pid, _ = get_player_id()
    return f"player:{pid}"


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@app.route("/api/spawn")
def api_spawn():
    challenge = request.args.get("challenge", "").strip()
    if challenge not in CHALLENGE_IMAGES:
        return jsonify({"error": f"Sfida sconosciuta: {challenge}"}), 400

    user_key = get_user_key()

    # Restituisce l'istanza esistente se ancora valida
    with registry_lock:
        for iid, info in registry.items():
            if info["user_key"] == user_key and info["challenge"] == challenge:
                remaining = int(info["ttl"] - (time.time() - info["created_at"]))
                return jsonify({
                    "instance_id": iid,
                    "url": f"/instance/{iid}/",
                    "ttl_remaining": remaining,
                    "existing": True,
                })

    # Cap globale
    with registry_lock:
        if len(registry) >= MAX_TOTAL_INSTANCES:
            return jsonify({"error": "Limite massimo di istanze raggiunto, riprova più tardi"}), 503

    # Avvia nuovo container
    try:
        container_id, ip = start_container(challenge)
    except Exception as exc:
        logger.error("Errore avvio container: %s", exc)
        return jsonify({"error": "Impossibile avviare l'istanza, riprova"}), 503

    instance_id = str(uuid.uuid4())
    with registry_lock:
        registry[instance_id] = {
            "container_id": container_id,
            "ip": ip,
            "user_key": user_key,
            "challenge": challenge,
            "created_at": time.time(),
            "ttl": INSTANCE_TTL,
        }

    logger.info("Istanza %s creata per %s (%s)", instance_id[:8], user_key, challenge)
    return jsonify({
        "instance_id": instance_id,
        "url": f"/instance/{instance_id}/",
        "ttl_remaining": INSTANCE_TTL,
        "existing": False,
    })


@app.route("/spawn-redirect")
def spawn_redirect():
    """Spawna il container e redirige direttamente all'istanza (apre in nuova scheda)."""
    challenge = request.args.get("challenge", "").strip()
    if challenge not in CHALLENGE_IMAGES:
        return f"Sfida '{challenge}' non trovata.", 400

    user_key = get_user_key()

    with registry_lock:
        for iid, info in registry.items():
            if info["user_key"] == user_key and info["challenge"] == challenge:
                return redirect(f"/instance/{iid}/")

    with registry_lock:
        if len(registry) >= MAX_TOTAL_INSTANCES:
            return "Limite massimo di istanze raggiunto, riprova più tardi.", 503

    try:
        container_id, ip = start_container(challenge)
    except Exception as exc:
        logger.error("Errore avvio container: %s", exc)
        return "Impossibile avviare l'istanza, riprova tra qualche secondo.", 503

    instance_id = str(uuid.uuid4())
    with registry_lock:
        registry[instance_id] = {
            "container_id": container_id,
            "ip": ip,
            "user_key": user_key,
            "challenge": challenge,
            "created_at": time.time(),
            "ttl": INSTANCE_TTL,
        }

    logger.info("Istanza %s creata per %s (%s)", instance_id[:8], user_key, challenge)
    return redirect(f"/instance/{instance_id}/")


@app.route("/api/stop")
def api_stop():
    instance_id = request.args.get("instance_id", "")
    user_key = get_user_key()

    with registry_lock:
        info = registry.get(instance_id)

    if not info:
        return jsonify({"error": "Istanza non trovata"}), 404
    if info["user_key"] != user_key:
        return jsonify({"error": "Non autorizzato"}), 403

    _destroy_instance(instance_id)
    return jsonify({"status": "fermata"})


@app.route("/api/status")
def api_status():
    user_key = get_user_key()
    with registry_lock:
        user_instances = [
            {
                "instance_id": iid,
                "challenge": info["challenge"],
                "url": f"/instance/{iid}/",
                "ttl_remaining": int(info["ttl"] - (time.time() - info["created_at"])),
            }
            for iid, info in registry.items()
            if info["user_key"] == user_key
        ]
        total = len(registry)
    return jsonify({"instances": user_instances, "total_active": total})


# ---------------------------------------------------------------------------
# Pagina launch (embeddabile in RTB come iframe o link diretto)
# ---------------------------------------------------------------------------

LAUNCH_PAGE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>CTF Challenge Launcher</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: monospace; background: #1a1a2e; color: #e0e0e0; padding: 16px; }
    .card { background: #16213e; border: 1px solid #0f3460; border-radius: 8px; padding: 16px; }
    h3 { color: #e94560; margin-bottom: 10px; font-size: 15px; }
    .launch-btn {
      display: inline-block; background: #e94560; color: #fff;
      padding: 10px 22px; border-radius: 4px; text-decoration: none;
      font-size: 14px; font-weight: bold;
    }
    .launch-btn:hover { background: #c73652; color: #fff; }
    .active-box { background: #0f3460; border-radius: 6px; padding: 12px; margin-top: 10px; }
    .active-box a { color: #4cc9f0; font-weight: bold; font-size: 13px; }
    .timer { color: #f72585; font-weight: bold; }
    .stop-btn { background: #444; color: #ccc; border: none; padding: 6px 12px;
                border-radius: 4px; cursor: pointer; font-size: 12px; margin-top: 8px; }
    .stop-btn:hover { background: #666; }
    small { color: #888; font-size: 12px; }
  </style>
</head>
<body>
<!-- I dati vengono letti da data-attributes: niente Jinja2 dentro i tag script -->
<div class="card"
     id="launcher"
     data-challenge="{{ challenge }}"
     data-pid="{{ player_id }}"
     data-ttl="{{ ttl_minutes }}">
  <h3>&#x1F3AF; Challenge: {{ challenge }}</h3>
  <p style="margin-bottom:12px;font-size:13px;color:#aaa">
    Istanza privata &mdash; disponibile per
    <strong style="color:#e0e0e0">{{ ttl_minutes }} minuti</strong>.
  </p>
  <a class="launch-btn"
     href="/spawner/spawn-redirect?challenge={{ challenge }}&pid={{ player_id }}"
     target="_blank"
     id="launch-link">
    &#x25B6; Avvia e apri sfida
  </a>
  <br><br>
  <small>Si aprira' in una nuova scheda.</small>
  <div id="active-info"></div>
</div>
<script>
var launcher   = document.getElementById('launcher');
var challenge  = launcher.getAttribute('data-challenge');
var serverPid  = launcher.getAttribute('data-pid');
var ttlMinutes = parseInt(launcher.getAttribute('data-ttl'), 10);

// localStorage sopravvive al logout di RTB, cookie no
var storedPid = localStorage.getItem('ctf_player_id');
var pid;
if (storedPid && /^[0-9a-f-]{36}$/.test(storedPid)) {
  pid = storedPid;
} else {
  pid = serverPid;
  localStorage.setItem('ctf_player_id', pid);
}
// Aggiorna il link con il pid corretto
document.getElementById('launch-link').href =
  '/spawner/spawn-redirect?challenge=' + challenge + '&pid=' + pid;

function showActive(data) {
  var remaining = data.ttl_remaining;
  var box = document.getElementById('active-info');
  box.innerHTML =
    '<div class="active-box">' +
      '<div>Istanza attiva &mdash; scade tra <span id="timer" class="timer">--</span></div>' +
      '<div style="margin-top:6px"><a href="' + data.url + '" target="_blank">Riapri sfida</a></div>' +
      '<button class="stop-btn" onclick="stopInstance(\'' + data.instance_id + '\')">Termina istanza</button>' +
    '</div>';

  var link = document.getElementById('launch-link');
  if (link) { link.href = data.url; link.textContent = 'Riapri sfida'; }

  var iv = setInterval(function() {
    remaining--;
    var el = document.getElementById('timer');
    if (el) { el.textContent = Math.floor(remaining/60) + 'm ' + (remaining%60) + 's'; }
    if (remaining <= 0) { clearInterval(iv); location.reload(); }
  }, 1000);
}

function stopInstance(id) {
  fetch('/spawner/api/stop?instance_id=' + id + '&pid=' + pid)
    .then(function() { location.reload(); });
}

fetch('/spawner/api/status?pid=' + pid)
  .then(function(r) { return r.json(); })
  .then(function(data) {
    var ex = data.instances.filter(function(i) { return i.challenge === challenge; })[0];
    if (ex) showActive(ex);
  });
</script>
</body>
</html>"""


@app.route("/launch")
def launch_page():
    challenge = request.args.get("challenge", "").strip()
    if challenge not in CHALLENGE_IMAGES:
        return f"Sfida '{challenge}' non trovata. Disponibili: {list(CHALLENGE_IMAGES.keys())}", 404
    pid, is_new = get_player_id()
    resp = make_response(render_template_string(
        LAUNCH_PAGE,
        challenge=challenge,
        player_id=pid,
        ttl_minutes=INSTANCE_TTL // 60,
    ))
    if is_new:
        set_player_cookie(resp, pid)
    return resp


# ---------------------------------------------------------------------------
# Proxy reverse verso il container
# ---------------------------------------------------------------------------

_HOP_BY_HOP = frozenset([
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade", "content-length",
])

BASE_TAG_RE = re.compile(rb"(<head[^>]*>)", re.IGNORECASE)
ABS_PATH_RE = re.compile(rb'((?:href|src|action)=")(/[^"]*)"', re.IGNORECASE)


def _rewrite_html(body: bytes, instance_id: str) -> bytes:
    """Inietta <base> tag e riscrive percorsi assoluti nelle risposte HTML."""
    base_path = f"/instance/{instance_id}".encode()
    base_tag = b"<base href=\"" + base_path + b"/\">"
    # Inietta base tag dopo <head>
    body = BASE_TAG_RE.sub(rb"\1" + base_tag, body, count=1)
    # Riscrivi href/src/action assoluti
    body = ABS_PATH_RE.sub(
        lambda m: m.group(1) + base_path + m.group(2) + b'"',
        body,
    )
    return body


@app.route("/proxy/<instance_id>/", defaults={"path": ""})
@app.route("/proxy/<instance_id>/<path:path>")
def proxy(instance_id: str, path: str):
    with registry_lock:
        info = registry.get(instance_id)

    if not info:
        return render_template_string("""
            <html><body style="font-family:monospace;background:#1a1a2e;color:#e94560;padding:40px">
            <h2>Istanza scaduta o non trovata</h2>
            <p>L'istanza &egrave; scaduta. <a href="javascript:history.back()" style="color:#4cc9f0">Torna indietro</a>
            per avviarne una nuova.</p></body></html>"""), 404

    target_url = f"http://{info['ip']}:{CONTAINER_PORT}/{path}"
    if request.query_string:
        target_url += "?" + request.query_string.decode()

    # Header da inoltrare al container, con prefix per il path rewriting lato app
    forward_headers = {
        k: v for k, v in request.headers
        if k.lower() not in _HOP_BY_HOP and k.lower() != "host"
    }
    forward_headers["X-Forwarded-Prefix"] = f"/instance/{instance_id}"
    forward_headers["X-Real-IP"] = request.remote_addr

    try:
        resp = http_requests.request(
            method=request.method,
            url=target_url,
            headers=forward_headers,
            data=request.get_data(),
            allow_redirects=False,
            timeout=15,
            stream=True,
        )
    except http_requests.exceptions.ConnectionError:
        public_path = f"/instance/{instance_id}/{path}"
        if request.query_string:
            public_path += "?" + request.query_string.decode()
        return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="3;url={public_path}">
<style>body{{font-family:monospace;background:#1a1a2e;color:#e0e0e0;display:flex;
align-items:center;justify-content:center;height:100vh;margin:0;flex-direction:column;gap:16px}}
.spinner{{width:36px;height:36px;border:4px solid #0f3460;border-top-color:#e94560;
border-radius:50%;animation:spin 0.8s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}</style></head>
<body><div class="spinner"></div>
<div>Container in avvio, attendere...</div>
<div style="font-size:12px;color:#888">Ricarico automaticamente tra 3 secondi</div>
</body></html>""", 503
    except Exception as exc:
        logger.error("Proxy error %s: %s", instance_id[:8], exc)
        return "Errore del proxy", 503

    # Riscrittura header di risposta
    response_headers = {}
    for k, v in resp.headers.items():
        if k.lower() in _HOP_BY_HOP:
            continue
        if k.lower() == "location":
            if v.startswith("/"):
                v = f"/instance/{instance_id}{v}"
        response_headers[k] = v

    content_type = resp.headers.get("content-type", "")
    body = resp.content

    if "text/html" in content_type:
        body = _rewrite_html(body, instance_id)

    return Response(body, status=resp.status_code, headers=response_headers)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.route("/health")
def health():
    with registry_lock:
        active = len(registry)
    return jsonify({"status": "ok", "active_instances": active})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
