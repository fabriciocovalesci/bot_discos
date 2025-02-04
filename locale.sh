#!/bin/bash

echo "Gerando localidade pt_BR.UTF-8..."

sudo locale-gen pt_BR.UTF-8
sudo update-locale LANG=pt_BR.UTF-8
sudo localedef -i pt_BR -f UTF-8 pt_BR.UTF-8

echo "Localidade pt_BR.UTF-8 configurada com sucesso!"
locale

q5fLfxLbL;;JclSiBpV?

gunicorn --workers 3 --bind 0.0.0.0:8000 unix:/root/bot_discos/api.sock api:app


ps aux | grep api.py
