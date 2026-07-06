#!/usr/bin/env bash
# Costruisce l'immagine della sfida SQLi
set -e
docker build -t ctf-sqli:latest .
echo "Immagine ctf-sqli:latest costruita con successo."
