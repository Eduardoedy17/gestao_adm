#!/bin/bash

echo "Building project..."
python3.12 -m pip install -r requirements.txt

# echo "Make Migration..."             <-- COMENTE ESTA LINHA
# python3.12 manage.py makemigrations  <-- COMENTE ESTA LINHA
# python3.12 manage.py migrate         <-- COMENTE ESTA LINHA

echo "Collect Static..."
python3.12 manage.py collectstatic --noinput --clear

echo "Build End"