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
LOGS_DIR = '/home/hlopper/Desktop/RSE/ProyectoRSE/logs/suricata'
CONFIG_FILE = '/home/hlopper/Desktop/RSE/ProyectoRSE/src/suricata/suricata.yaml'

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
    
    info('*** Iniciando Suricata en el SERVIDOR\n')
    # CRÍTICO: -i servidor-eth0 (interfaz DENTRO de Mininet)
    servidor.cmd(f'suricata -c {CONFIG_FILE} -i servidor-eth0 -l {LOGS_DIR} -D')
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
    info('   atacante python3 /home/hlopper/Desktop/RSE/ProyectoRSE/src/ataques/syn_flood.py 10.0.0.1 80 100 0.01\n\n')
    info('3️⃣  Tráfico legítimo:\n')
    info('   cliente python3 /home/hlopper/Desktop/RSE/ProyectoRSE/src/scripts/trafico_legitimo.py --servidor 10.0.0.1 --duracion 1 --intervalo 3 &\n\n')
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