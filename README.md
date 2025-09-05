# QR-Info-Portal für Laborstandorte

Ein Web-Portal für medizinische Laborstandorte, das Besuchern über QR-Code sofortige Informationen zu Verfügbarkeit und Öffnungszeiten bereitstellt.

## Installation

```bash
git clone https://github.com/Ralle1976/qr-info-portal.git
cd qr-info-portal

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python -c "from app.database import init_database; init_database()"

flask run --host 0.0.0.0 --port 5000
```

## Konfiguration

Bearbeiten Sie `config.yml` für Ihre Einstellungen:

```yaml
site:
  name: "Labor Pattaya"
  languages: ["de", "th", "en"]
  timezone: "Asia/Bangkok"

location:
  address: "Ihre Adresse"
  latitude: 12.923556
  longitude: 100.882507

contact:
  phone: "+66 XXX XXX XXX"
  email: "info@example.com"
```

## Verwendung

- **Öffentlich**: QR-Code an Tür → Status und Öffnungszeiten
- **Admin**: `/admin` → Verwaltung von Status und Zeiten
- **Kiosk**: `/kiosk/single` oder `/kiosk/triple` für Monitore

## Lizenz

MIT License