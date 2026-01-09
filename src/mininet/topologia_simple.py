#!/usr/bin/env python3
"""
Topología simple para el proyecto de detección DDoS
Autor: [Tu nombre]
Fecha: [Fecha actual]
"""

from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def crear_topologia():
    """
    Crea una topología simple:
    - 1 switch
    - 1 servidor (víctima potencial)
    - 2 clientes (uno normal, uno atacante)
    """
    
    info('*** Creando red\n')
    net = Mininet(controller=Controller)
    
    info('*** Añadiendo controlador\n')
    net.addController('c0')
    
    info('*** Añadiendo switch\n')
    s1 = net.addSwitch('s1')
    
    info('*** Añadiendo hosts\n')
    servidor = net.addHost('h1', ip='10.0.0.1/24')
    cliente_normal = net.addHost('h2', ip='10.0.0.2/24')
    atacante = net.addHost('h3', ip='10.0.0.3/24')
    
    info('*** Creando enlaces\n')
    net.addLink(servidor, s1)
    net.addLink(cliente_normal, s1)
    net.addLink(atacante, s1)
    
    info('*** Iniciando red\n')
    net.start()
    
    info('*** Probando conectividad\n')
    net.pingAll()
    
    info('*** Abriendo CLI\n')
    CLI(net)
    
    info('*** Parando red\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    crear_topologia()