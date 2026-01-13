#!/usr/bin/env python3
"""
Topología Mininet con Suricata integrado
Proyecto RSE 2025 - Detección DDoS
"""

import time
import os
import subprocess
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

# Rutas absolutas
PROYECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGS_DIR = os.path.join(PROYECT_PATH, "logs", "suricata")
CONFIG_TEMPLATE = os.path.join(PROYECT_PATH, "src", "suricata", "suricata_template.yaml")
CONFIG_RUN = os.path.join(PROYECT_PATH, "src", "suricata", "suricata_run.yaml")

print(CONFIG_RUN)
print(LOGS_DIR)

def limpiar():
    """Limpia procesos y archivos previos"""
    info('*** Limpiando procesos previos\n')
    subprocess.run(['sudo', 'pkill', '-9', 'suricata'], stderr=subprocess.DEVNULL)
    subprocess.run(['sudo', 'rm', '-f', '/var/run/suricata*.pid'], stderr=subprocess.DEVNULL)
    subprocess.run(['sudo', 'mn', '-c'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

def main():
    # Limpiar antes de empezar
    limpiar()

    # Crear nuevo .yaml a raíz de la plantilla, con la ruta absoluta obtenida dinámicamente
    # 1. Leer el contenido de la plantilla original
    with open(CONFIG_TEMPLATE, 'r') as file:
        data = file.read()

    # 2. Reemplar la ruta
    data_actualizada = data.replace("REEMPLAZAR_CON_RUTA_PROYECTO", PROYECT_PATH)

    # 3. Guardar el resultado en un archivo nuevo y dar permisos
    with open(CONFIG_RUN, 'w') as file:
        file.write(data_actualizada)

    subprocess.run(['sudo', 'chmod', '777', CONFIG_RUN])
    
    # Crear directorio de logs con permisos
    os.makedirs(LOGS_DIR, exist_ok=True)
    subprocess.run(['sudo', 'chmod', '777', LOGS_DIR])
    
    info('*** Creando red Mininet\n')
    net = Mininet(link=TCLink, autoSetMacs=True)
    
    info('*** Añadiendo nodos\n')
    s1 = net.addSwitch('s1', failMode='standalone')
    servidor = net.addHost('servidor', ip='10.0.0.1/24')
    cliente = net.addHost('cliente', ip='10.0.0.2/24')
    atacante = net.addHost('atacante', ip='10.0.0.3/24')
    
    info('*** Creando enlaces\n')
    net.addLink(servidor, s1, bw=100, delay='5ms')
    net.addLink(cliente, s1, bw=10, delay='10ms')
    net.addLink(atacante, s1, bw=10, delay='10ms')
    
    info('*** Iniciando red\n')
    net.start()
    
    info('*** Iniciando servidor HTTP\n')
    servidor.cmd('python3 -m http.server 80 &')
    time.sleep(1)

    info('*** Desactivando offloading en el servidor\n')
    servidor.cmd('ethtool -K servidor-eth0 rx off tx off gso off gro off lro off tso off')
    time.sleep(1)
    
    info('*** Iniciando Suricata en el SERVIDOR\n')
    # CRÍTICO: -i servidor-eth0 (interfaz DENTRO de Mininet)
    servidor.cmd(f'suricata -c {CONFIG_RUN} -i servidor-eth0 -l {LOGS_DIR} > {LOGS_DIR}/startup_error.log 2>&1 &')
    #servidor.cmd(f'suricata -c {CONFIG_RUN} -i servidor-eth0 -l {LOGS_DIR} -D')
    servidor.cmd(f'suricata -V')
    time.sleep(3)
    
    # Verificar
    pid = servidor.cmd('pgrep -f "suricata.*servidor-eth0"').strip()
    if pid:
        info(f'*** ✅ Suricata corriendo (PID: {pid})\n')
    else:
        info('*** ❌ ERROR: Suricata no arrancó\n')
    
    info('***  Probando conectividad\n')
    net.pingAll()
    
    info('\n' + '='*60 + '\n')
    info('🚀 RED LISTA PARA PRUEBAS\n')
    info('='*60 + '\n\n')
    info('📝 COMANDOS IMPORTANTES:\n\n')
    info('1️⃣  Ver alertas EN OTRA TERMINAL:\n')
    info(f'   tail -f {LOGS_DIR}/fast.log\n\n')
    info('2️⃣  Lanzar ataque AQUÍ:\n')
    info(f'   atacante python3 ${PROYECT_PATH}/src/ataques/syn_flood.py 10.0.0.1 80 100 0.01\n\n')
    info('3️⃣  Tráfico legítimo:\n')
    info(f'   cliente python3 ${PROYECT_PATH}/src/scripts/trafico_legitimo.py --servidor 10.0.0.1 --duracion 1 --intervalo 3 &\n\n')
    info('4️⃣  Salir:\n')
    info('   exit\n\n')
    info('='*60 + '\n')
    
    CLI(net)
    
    info('*** Deteniendo red\n')
    net.stop()
    limpiar()

if __name__ == '__main__':
    setLogLevel('info')
    main()