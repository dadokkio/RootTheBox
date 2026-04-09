# Usiamo PyPy 3.9
FROM pypy:3.9

WORKDIR /opt/rtb

# 1. Installiamo le dipendenze di base
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. INSTALLIAMO RUST (tramite rustup, molto più affidabile per cryptography)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# 3. Prepariamo l'ambiente Python
COPY ./setup/requirements.txt /opt/rtb/requirements.txt

# Aggiorniamo pip e setuptools (fondamentale per gestire Rust)
RUN pypy3 -m pip install --no-cache-dir --upgrade pip setuptools wheel setuptools-rust

# 4. Installiamo i requirements (ora che Rust è presente, cryptography passerà)
RUN pypy3 -m pip install --no-cache-dir -r requirements.txt && \
    pypy3 -m pip install --no-cache-dir psycopg2cffi

ENV PATH="/usr/local/bin:/opt/pypy/bin:${PATH}"

ADD . .

# ENTRYPOINT pulito senza debug
ENTRYPOINT ["/usr/local/bin/pypy3", "/opt/rtb/rootthebox.py", "--start"]
