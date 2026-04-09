#!/bin/bash
# ============================================================
# FonoApp - Script de despliegue en Ubuntu 24.04
# Ejecutar como usuario ubuntu: bash setup.sh
# ============================================================
set -e

APP_DIR="/home/ubuntu/fonoapp"
REPO="https://github.com/fduarte88/agenda_paciente.git"

echo ">>> [1/8] Actualizando paquetes del sistema..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.12 python3.12-venv python3-pip nginx git

echo ">>> [2/8] Clonando repositorio..."
if [ -d "$APP_DIR" ]; then
    cd "$APP_DIR" && git pull
else
    git clone "$REPO" "$APP_DIR"
    cd "$APP_DIR"
fi

echo ">>> [3/8] Creando entorno virtual..."
python3.12 -m venv "$APP_DIR/venv"
source "$APP_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

echo ">>> [4/8] Configurando variables de entorno..."
if [ ! -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    echo ""
    echo "  IMPORTANTE: Edita el archivo .env antes de continuar:"
    echo "  nano $APP_DIR/.env"
    echo ""
    read -p "  Presiona ENTER cuando hayas guardado el .env..."
fi

echo ">>> [5/8] Configurando base de datos PostgreSQL..."
source "$APP_DIR/.env"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -c "ALTER DATABASE $DB_NAME OWNER TO $DB_USER;"

echo ">>> [6/8] Migraciones y archivos estáticos..."
export DJANGO_SETTINGS_MODULE=fonoapp.settings_prod
python manage.py migrate --noinput
python manage.py collectstatic --noinput
mkdir -p "$APP_DIR/media"

echo ">>> [7/8] Configurando Gunicorn como servicio..."
sudo cp "$APP_DIR/deploy/gunicorn.service" /etc/systemd/system/fonoapp.service
sudo systemctl daemon-reload
sudo systemctl enable fonoapp
sudo systemctl restart fonoapp

echo ">>> [8/8] Configurando Nginx..."
sudo cp "$APP_DIR/deploy/nginx.conf" /etc/nginx/sites-available/fonoapp
sudo ln -sf /etc/nginx/sites-available/fonoapp /etc/nginx/sites-enabled/fonoapp
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

echo ""
echo "============================================================"
echo "  DESPLIEGUE COMPLETADO"
echo "  Accede en: http://$(curl -s ifconfig.me)"
echo "============================================================"
echo ""
echo "  Logs Gunicorn : sudo journalctl -u fonoapp -f"
echo "  Logs Nginx    : sudo tail -f /var/log/nginx/error.log"
echo "  Reiniciar app : sudo systemctl restart fonoapp"
echo ""
