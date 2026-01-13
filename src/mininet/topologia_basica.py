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

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

def crear_topologia_basica():
    """
    Crea topología simple con:
    - 1 servidor (víctima del DDoS)
    - 1 cliente legítimo
    - 1 atacante
    - 1 switch
    """
    
    info('*** Creando red\n')
    # Sin especificar controlador - usa el por defecto
    net = Mininet(
        link=TCLink,
        autoSetMacs=True
    )
    
    info('*** Añadiendo switch\n')
    s1 = net.addSwitch('s1', failMode='standalone')

    info('*** Añadiendo hosts\n')
    # Servidor (víctima)
    servidor = net.addHost(
        'servidor',
        ip='10.0.0.1/24',
        mac='00:00:00:00:00:01'
    )
    
    # Cliente normal
    cliente = net.addHost(
        'cliente',
        ip='10.0.0.2/24',
        mac='00:00:00:00:00:02'
    )
    
    # Atacante
    atacante = net.addHost(
        'atacante',
        ip='10.0.0.3/24',
        mac='00:00:00:00:00:03'
    )
    
    info('*** Creando enlaces\n')
    # Enlaces con ancho de banda limitado (más realista)
    net.addLink(
        servidor, s1,
        bw=100,  # 100 Mbps
        delay='5ms'
    )
    net.addLink(
        cliente, s1,
        bw=10,  # 10 Mbps
        delay='10ms'
    )
    net.addLink(
        atacante, s1,
        bw=10,  # 10 Mbps
        delay='10ms'
    )
    
    info('*** Iniciando red\n')
    net.start()
    
    info('*** Configurando servidor web en h1\n')
    # Iniciar servidor HTTP simple en el servidor
    servidor.cmd('python3 -m http.server 80 &')
    
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
    info('  cliente curl 10.0.0.1 - Probar servidor web\n')
    info('  xterm servidor      - Abrir terminal en servidor\n')
    info('  xterm atacante      - Abrir terminal en atacante\n')
    info('\n*** Abriendo CLI\n')
    
    CLI(net)
    
    info('*** Parando red\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    crear_topologia_basica()