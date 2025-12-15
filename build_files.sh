#!/bin/bash

echo "Building project..."
# Instala as dependências
python3.12 -m pip install -r requirements.txt

echo "Collect Static..."
# Gera os arquivos estáticos (Essencial para o CSS funcionar)
python3.12 manage.py collectstatic --noinput --clear

# COMENTE AS MIGRAÇÕES NO BUILD (Faça isso via terminal local)
# echo "Make Migration..."
# python3.12 manage.py makemigrations
# python3.12 manage.py migrate

echo "Build End"