FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir flask==3.1.0

COPY app.py .

# Il flag viene passato come variabile d'ambiente al momento dell'avvio
ENV CTF_FLAG="RTB{change_me_in_spawner_config}"

# Inizializza il DB e avvia l'app
CMD python -c "import app; app.init_db()" && python app.py
