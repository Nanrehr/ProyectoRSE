#!/bin/bash
# Este script instala todas las dependencias necesarias para ejecutar el proyecto.

# Colores para los logs
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[OK] $1${NC}"; }
log_error() { echo -e "${RED}[ERROR] $1${NC}"; }

# Aviso al usuario
echo -e "${RED}⚠️  ATENCIÓN:${NC} Este script modifica los archivos de configuración de grafana y suricata, sobreescribiendo cambios. Quieres continuar?"
read -p "$PREGUNTA_USUARIO" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    log_error "Instalación cancelada por el usuario."
    exit 1
fi

echo "--- Iniciando Instalación de dependencias del proyecto ---"

# 1. Actualización del sistema
echo "Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

# 2. Paquetes base
echo "Instalando paquetes base..."
sudo apt install -y git curl wget vim python3 python3-pip python3-scapy build-essential software-properties-common xterm
python3 --version && pip3 --version && log_info "Paquetes base instalados"

# 3. Instalar Mininet
echo "Instalando Mininet..."
sudo apt install -y mininet openvswitch-switch
if sudo mn --test pingall; then
    log_info "Mininet verificado correctamente"
else
    log_error "Fallo en verificación de Mininet"
fi

# 4. Instalar Suricata
echo "Instalando Suricata..."
sudo apt install -y suricata -y
SURICATA_V=$(suricata -V | grep -o '6.0.4')
if [ "$SURICATA_V" == "6.0.4" ]; then
    log_info "Suricata versión 6.0.4 instalada"
else
    log_error "Versión de suricata incorrecta ($(suricata -V)), se recomienda usar suricata 6.0.4"
fi

# Configuración de reglas Suricata
sudo suricata-update
sudo sed -i 's|default-rule-path: /etc/suricata/rules|default-rule-path: /var/lib/suricata/rules|' /etc/suricata/suricata.yaml
# Intentar detectar interfaz activa (ej. enp0s3 o eth0) y cambiarla
IFACE=$(ip route get 8.8.8.8 | awk -- '{printf $5}')
IFACE=${IFACE:-enp0s3} # Asignar enp0s3 por defecto (si lo anterior falla)
sudo sed -i "s/interface: eth0/interface: $IFACE/" /etc/suricata/suricata.yaml

sudo systemctl enable suricata
sudo systemctl restart suricata
log_info "Suricata configurado en interfaz $IFACE"

# 5. Instalar Prometheus
echo "Instalando Prometheus..."
if ! id "prometheus" &>/dev/null; then
    # Añadir usuario para prometheus
    sudo useradd --no-create-home --shell /bin/false prometheus
fi

# Descargar, descomprimir, mover archivos y dar permisos
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v2.49.1/prometheus-2.49.1.linux-amd64.tar.gz
tar xvf prometheus-2.49.1.linux-amd64.tar.gz
sudo mv prometheus-2.49.1.linux-amd64/prometheus /usr/local/bin/
sudo mv prometheus-2.49.1.linux-amd64/promtool /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/prometheus /usr/local/bin/promtool

sudo mkdir -p /etc/prometheus /var/lib/prometheus
sudo mv prometheus-2.49.1.linux-amd64/consoles /etc/prometheus
sudo mv prometheus-2.49.1.linux-amd64/console_libraries /etc/prometheus
sudo chown -R prometheus:prometheus /etc/prometheus /var/lib/prometheus

# Crear configuración de Prometheus
cat <<EOF | sudo tee /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]
EOF

# Crear servicio Systemd para Prometheus
cat <<EOF | sudo tee /etc/systemd/system/prometheus.service
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/var/lib/prometheus/

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now prometheus
log_info "Prometheus instalado y ejecutándose en puerto 9090"

# 6. Instalar Grafana
echo "Instalando Grafana..."
wget https://dl.grafana.com/enterprise/release/grafana-enterprise_11.4.0_amd64.deb
sudo dpkg -i grafana-enterprise_11.4.0_amd64.deb || sudo apt-get install -f -y
sudo systemctl enable --now grafana-server
log_info "Grafana instalado en puerto 3000 (admin/admin)"


echo -e "\n==============================================="
echo -e "      VERIFICANDO ESTADO DEL SISTEMA"
echo -e "==============================================="

# Función para verificar servicios de systemd
check_service() {
    if systemctl is-active --quiet $1; then
        log_ok "Servicio '$1': ACTIVO (running)"
    else
        log_error "Servicio '$1': INACTIVO o con errores"
    fi
}

# Función para verificar conectividad
check_connectivity() {
    local url=$1
    local name=$2
    if curl -s --head --request GET "$url" | grep "HTTP/1.1 [23]0" > /dev/null; then
        log_ok "Conexión a $name ($url): FUNCIONANDO"
    else
        log_error "Conexión a $name ($url): FALLIDA"
    fi
}

# Comprobar estados de Systemd
log_info "Comprobando servicios del sistema..."
check_service "suricata"
check_service "prometheus"
check_service "grafana-server"
check_service "openvswitch-switch"

# Comprobar conectividad a prometheus y grafana
log_info "Comprobando acceso a paneles web..."
# Esperar unos segundos a que los servicios terminen de arrancar antes de probar
sleep 2 
check_connectivity "http://localhost:9090" "Prometheus"
check_connectivity "http://localhost:3000" "Grafana"
