"""
CTF Challenge: SQL Injection
Obiettivo: recupera il flag dalla tabella 'secrets'.
Difficoltà: facile/medio
"""

import os
import sqlite3

from flask import Flask, g, render_template_string, request

app = Flask(__name__)

FLAG = os.environ.get("CTF_FLAG", "RTB{placeholder_change_me}")
DATABASE = "/tmp/challenge.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user'
            );
            CREATE TABLE IF NOT EXISTS secrets (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                value TEXT NOT NULL
            );
            DELETE FROM users;
            DELETE FROM secrets;
            INSERT INTO users VALUES (1,'admin','s3cr3tP@ss','admin');
            INSERT INTO users VALUES (2,'alice','alice123','user');
            INSERT INTO users VALUES (3,'bob','bob456','user');
        """)
        conn.execute(
            "INSERT INTO secrets VALUES (1,'flag',?)", (FLAG,)
        )
        conn.commit()


TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>User Search - CTF Challenge</title>
  <style>
    * { box-sizing:border-box; }
    body { font-family:'Courier New',monospace; background:#0d1117; color:#c9d1d9; margin:0; padding:30px; }
    h1 { color:#58a6ff; border-bottom:1px solid #30363d; padding-bottom:10px; }
    .hint { background:#161b22; border:1px solid #30363d; border-radius:6px; padding:15px; margin:20px 0; font-size:13px; }
    .hint span { color:#f0883e; }
    form { margin:20px 0; }
    input[type=text] { background:#161b22; border:1px solid #30363d; color:#c9d1d9; padding:8px 12px; width:300px; border-radius:6px; font-family:monospace; }
    input[type=submit] { background:#238636; color:#fff; border:none; padding:8px 16px; border-radius:6px; cursor:pointer; margin-left:8px; }
    input[type=submit]:hover { background:#2ea043; }
    table { border-collapse:collapse; width:100%; max-width:700px; margin-top:15px; }
    th { background:#161b22; color:#58a6ff; padding:10px; border:1px solid #30363d; text-align:left; }
    td { padding:10px; border:1px solid #30363d; }
    tr:nth-child(even) td { background:#161b22; }
    .error { color:#f85149; background:#161b22; border:1px solid #f85149; padding:10px; border-radius:6px; margin:10px 0; }
    .query-box { background:#161b22; border:1px solid #30363d; padding:10px; border-radius:6px; font-size:12px; color:#8b949e; margin-top:10px; }
  </style>
</head>
<body>
  <h1>&#x1F50D; User Search Panel</h1>

  <div class="hint">
    <p><span>Obiettivo:</span> Trova il flag nascosto nel database.</p>
    <p>Suggerimento: questa applicazione esegue query SQL senza sanitizzazione. La tabella
    <code>secrets</code> contiene qualcosa di interessante...</p>
  </div>

  <form method="GET" action="">
    <input type="text" name="q" value="{{ query }}" placeholder="Cerca username...">
    <input type="submit" value="Cerca">
  </form>

  {% if query %}
  <div class="query-box">Query eseguita: <code>SELECT id,username,role FROM users WHERE username = '{{ query }}'</code></div>
  {% endif %}

  {% if error %}
  <div class="error">Errore DB: {{ error }}</div>
  {% endif %}

  {% if results %}
  <table>
    <tr><th>ID</th><th>Username</th><th>Role</th></tr>
    {% for row in results %}
    <tr><td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td></tr>
    {% endfor %}
  </table>
  {% elif query and not error %}
  <p style="color:#8b949e">Nessun risultato trovato.</p>
  {% endif %}

</body>
</html>"""


@app.route("/")
def index():
    query = request.args.get("q", "")
    results = []
    error = None

    if query:
        db = get_db()
        # VULNERABILE INTENZIONALMENTE: NO parameterized query
        sql = f"SELECT id,username,role FROM users WHERE username = '{query}'"
        try:
            results = db.execute(sql).fetchall()
        except sqlite3.OperationalError as exc:
            error = str(exc)

    return render_template_string(
        TEMPLATE,
        query=query,
        results=results,
        error=error,
    )


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=80, debug=False)
