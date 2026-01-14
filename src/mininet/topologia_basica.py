#!/usr/bin/env python3
"""
Topología básica para detección de DDoS
Proyecto: RSE 2025
Autores: Daniel Carracedo, Hernán López, Rubén Subiela

Topología:
    servidor (h1) --- switch (s1) --- cliente (h2)
                              |
                          atacante (h3)
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

# Obtener la ruta base del proyecto
PROYECTO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(PROYECTO_DIR, 'scripts')

def limpiar():
    """Limpia procesos y archivos de forma agresiva"""
    info('*** Limpiando restos de ejecuciones anteriores...\n')
    # Usamos pkill que es mucho más directo y no falla con las comillas de awk
    subprocess.run(['sudo', 'pkill', '-9', '-f', 'suricata'], stderr=subprocess.DEVNULL)
    
    # Limpieza de Mininet
    subprocess.run(['sudo', 'mn', '-c'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Borrar archivos de PID sobrantes
    subprocess.run('sudo rm -f /var/run/suricata*.pid', shell=True)
    time.sleep(2)

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

    info('*** Configurando variables de entorno en hosts\n')
    # Establecer variable de entorno en cada host con la ruta a scripts
    for host in net.hosts:
        host.cmd(f'export SCRIPTS_DIR={SCRIPTS_DIR}')
    
    info('*** Configurando servidor web en h1\n')
    # Iniciar servidor HTTP simple en el servidor
    servidor.cmd('python3 -m http.server 80 &')

    info('*** Iniciando Suricata en el SERVIDOR\n')
    # Descativar offloading
    #servidor.cmd('ethtool -K servidor-eth0 rx off tx off gso off gro off lro off tso off')
    # CRÍTICO: -i servidor-eth0 (interfaz DENTRO de Mininet)
    servidor.cmd(f'suricata -c {CONFIG_RUN} -i servidor-eth0 -l {LOGS_DIR} > {LOGS_DIR}/suricata_stdout.log 2>&1 &')
    time.sleep(3)

    # Verificación de PID (Añade esto para saber si realmente arrancó)
    pid = servidor.cmd('pgrep -f suricata').strip()
    if pid:
        info(f'*** ✅ Suricata iniciado (PID: {pid})\n')
    else:
        info(f'*** ❌ ERROR: Suricata no arrancó. Revisa {LOGS_DIR}/suricata_stdout.log\n')
    
    info('*** Probando conectividad\n')
    net.pingAll()
    
    info('\n*** Red lista!\n')
    info('*** Comandos útiles:\n')
    info('  nodes               - Ver todos los nodos\n')
    info('  net                 - Ver topología completa\n')
    info('  dump                - Ver configuración de hosts\n')
    info('  links               - Ver enlaces\n')
    info('  pingall             - Probar conectividad\n')
    info('  servidor ifconfig   - Ver IP del servidor\n')
    info('  cliente ifconfig    - Ver IP del cliente\n')
    info('  cliente curl 10.0.0.1 - Probar servidor web\n')
    info('  xterm servidor      - Abrir terminal en servidor\n')
    info('  xterm cliente       - Abrir terminal en cliente\n')
    info('  xterm atacante      - Abrir terminal en atacante\n')
    info('  atacante ataque-syn          - Ejecutar ataque syn_flood\n')
    atacante.cmd(f'alias ataque-syn="python3 {PROYECT_PATH}/src/ataques/syn_flood.py 10.0.0.1 80 100 0.01"')
    info('  cliente trafico-legitimo     - Ejecutar tráfico legítimo (2 min, cada 5 seg)\n')
    cliente.cmd(f'alias trafico-legitimo="python3 {SCRIPTS_DIR}/trafico_legitimo.py --servidor 10.0.0.1 --duracion 2 --intervalo 5"')
    info('\n*** Abriendo CLI\n')
    
    CLI(net)
    
    info('*** Parando red\n')
    net.stop()
    limpiar()

if __name__ == '__main__':
    setLogLevel('info')
    main()