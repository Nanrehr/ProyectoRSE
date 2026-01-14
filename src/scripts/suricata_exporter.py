import json
import time
import os
from prometheus_client import start_http_server, Counter

PROYECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ===== CONFIGURACIÓN =====
EVE_PATH = os.path.join(PROYECT_PATH, "logs", "suricata", "eve.json")
EXPORTER_PORT = 8000

# ===== MÉTRICAS =====
suricata_alerts_by_category = Counter(
    "suricata_alerts_by_category_total",
    "Total de alertas de Suricata por categoría",
    ["category"]
)

# ===== ESTADO =====
file_offset = 0

def process_new_events():
    global file_offset

    if not os.path.exists(EVE_PATH):
        return

    with open(EVE_PATH, "r") as f:
        f.seek(file_offset)

        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            if event.get("event_type") != "alert":
                continue

            alert = event.get("alert", {})
            category = alert.get("category", "unknown")

            suricata_alerts_by_category.labels(
                category=category
            ).inc()

        file_offset = f.tell()


if __name__ == "__main__":
    print("▶Iniciando Suricata Exporter")
    print(f"Métricas en http://localhost:{EXPORTER_PORT}/metrics")

    start_http_server(EXPORTER_PORT)

    while True:
        process_new_events()
        time.sleep(1)
