#!/usr/bin/env bash
# Script care rulează la build pe Render

# Actualizare pachete
apt-get update

# Instalare dependențe
apt-get install -y curl gnupg unixodbc-dev

# Importare cheie Microsoft
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

# Adaugă repo Microsoft SQL Server pentru Ubuntu
curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Update și instalare driver
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Verificare
odbcinst -q -d
