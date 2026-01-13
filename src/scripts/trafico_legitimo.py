#!/usr/bin/env python3
"""
Generador de tráfico legítimo para establecer baseline
Proyecto: RSE 2025 - Detección DDoS
Autores: Daniel Carracedo, Hernán López, Rubén Subiela

Este script simula un cliente legítimo que:
- Hace peticiones HTTP periódicas al servidor
- Envía pings de conectividad
- Mantiene un patrón predecible y estable
"""

import time
import subprocess
import requests
import argparse
from datetime import datetime
import sys

class ClienteLegitimo:
    """
    Cliente que genera tráfico HTTP normal
    """
    
    def __init__(self, servidor_ip, duracion_minutos, intervalo_segundos):
        self.servidor_ip = servidor_ip
        self.duracion = duracion_minutos * 60  # Convertir a segundos
        self.intervalo = intervalo_segundos
        self.url = f"http://{servidor_ip}"
        
        # Contadores para estadísticas
        self.peticiones_exitosas = 0
        self.peticiones_fallidas = 0
        self.pings_exitosos = 0
        self.pings_fallidos = 0
    
    def log(self, mensaje):
        """Imprime mensaje con timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {mensaje}")
    
    def hacer_peticion_http(self):
        """
        Realiza una petición HTTP GET al servidor
        """
        try:
            respuesta = requests.get(self.url, timeout=5)
            if respuesta.status_code == 200:
                self.peticiones_exitosas += 1
                self.log(f"✓ HTTP GET {self.url} - Status: {respuesta.status_code}")
                return True
            else:
                self.peticiones_fallidas += 1
                self.log(f"✗ HTTP GET {self.url} - Status: {respuesta.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.peticiones_fallidas += 1
            self.log(f"✗ HTTP GET falló: {e}")
            return False
    
    def hacer_ping(self):
        """
        Envía un ping ICMP al servidor
        """
        try:
            # -c 1: solo 1 paquete
            # -W 2: timeout de 2 segundos
            resultado = subprocess.run(
                ['ping', '-c', '1', '-W', '2', self.servidor_ip],
                capture_output=True,
                text=True
            )
            
            if resultado.returncode == 0:
                self.pings_exitosos += 1
                self.log(f"✓ PING {self.servidor_ip} - OK")
                return True
            else:
                self.pings_fallidos += 1
                self.log(f"✗ PING {self.servidor_ip} - Falló")
                return False
        except Exception as e:
            self.pings_fallidos += 1
            self.log(f"✗ PING error: {e}")
            return False
    
    def generar_trafico(self):
        """
        Bucle principal que genera tráfico legítimo
        """
        self.log("=" * 60)
        self.log("INICIO DE GENERACIÓN DE TRÁFICO LEGÍTIMO")
        self.log(f"Servidor: {self.servidor_ip}")
        self.log(f"Duración: {self.duracion/60:.1f} minutos")
        self.log(f"Intervalo entre peticiones: {self.intervalo} segundos")
        self.log("=" * 60)
        
        tiempo_inicio = time.time()
        tiempo_fin = tiempo_inicio + self.duracion
        iteracion = 0
        
        try:
            while time.time() < tiempo_fin:
                iteracion += 1
                tiempo_restante = (tiempo_fin - time.time()) / 60
                
                self.log(f"\n--- Iteración {iteracion} (quedan {tiempo_restante:.1f} min) ---")
                
                # Hacer petición HTTP
                self.hacer_peticion_http()
                
                # Cada 5 iteraciones, hacer un ping
                if iteracion % 5 == 0:
                    self.hacer_ping()
                
                # Esperar antes de la siguiente iteración
                time.sleep(self.intervalo)
        
        except KeyboardInterrupt:
            self.log("\n⚠ Interrumpido por usuario")
        
        finally:
            self.mostrar_estadisticas()
    
    def mostrar_estadisticas(self):
        """
        Muestra resumen de la actividad
        """
        total_peticiones = self.peticiones_exitosas + self.peticiones_fallidas
        total_pings = self.pings_exitosos + self.pings_fallidos
        
        self.log("\n" + "=" * 60)
        self.log("RESUMEN DE TRÁFICO LEGÍTIMO")
        self.log("=" * 60)
        self.log(f"Peticiones HTTP totales: {total_peticiones}")
        self.log(f"  ✓ Exitosas: {self.peticiones_exitosas}")
        self.log(f"  ✗ Fallidas:  {self.peticiones_fallidas}")
        
        if total_peticiones > 0:
            tasa_exito_http = (self.peticiones_exitosas / total_peticiones) * 100
            self.log(f"  Tasa de éxito: {tasa_exito_http:.1f}%")
        
        self.log(f"\nPings ICMP totales: {total_pings}")
        self.log(f"  ✓ Exitosos: {self.pings_exitosos}")
        self.log(f"  ✗ Fallidos:  {self.pings_fallidos}")
        
        if total_pings > 0:
            tasa_exito_ping = (self.pings_exitosos / total_pings) * 100
            self.log(f"  Tasa de éxito: {tasa_exito_ping:.1f}%")
        
        self.log("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Generador de tráfico legítimo para baseline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Generar tráfico durante 5 minutos, 1 petición cada 3 segundos
  python3 trafico_legitimo.py --servidor 10.0.0.1 --duracion 5 --intervalo 3
  
  # Tráfico más frecuente (cada segundo) durante 2 minutos
  python3 trafico_legitimo.py --servidor 10.0.0.1 --duracion 2 --intervalo 1
        """
    )
    
    parser.add_argument(
        '--servidor',
        type=str,
        default='10.0.0.1',
        help='IP del servidor (default: 10.0.0.1)'
    )
    
    parser.add_argument(
        '--duracion',
        type=int,
        default=5,
        help='Duración en MINUTOS (default: 5)'
    )
    
    parser.add_argument(
        '--intervalo',
        type=int,
        default=3,
        help='Segundos entre peticiones (default: 3)'
    )
    
    args = parser.parse_args()
    
    # Validaciones
    if args.duracion <= 0:
        print("ERROR: La duración debe ser mayor que 0")
        sys.exit(1)
    
    if args.intervalo <= 0:
        print("ERROR: El intervalo debe ser mayor que 0")
        sys.exit(1)
    
    # Crear cliente y generar tráfico
    cliente = ClienteLegitimo(
        servidor_ip=args.servidor,
        duracion_minutos=args.duracion,
        intervalo_segundos=args.intervalo
    )
    
    cliente.generar_trafico()


if __name__ == '__main__':
    main()