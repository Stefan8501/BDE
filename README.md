# IWS BDE Plattform

Dieses Projekt implementiert eine modulare Betriebsdatenerfassung (BDE) für die IWS GmbH. 
Die Lösung basiert auf FastAPI, SQLAlchemy und einer SQLite Datenbank und orientiert sich 
an den Funktionen gängiger BDE-Systeme.

## Funktionsumfang

- Verwaltung von Stammdaten wie Mitarbeitern, Maschinen, Arbeitsaufträgen und Operationen.
- Erfassung von Leistungsdaten über Activity Records mit Gut- und Ausschussmengen.
- REST-API mit CRUD-Endpunkten für alle relevanten Stammdatenobjekte.
- CSV-Import und Export für alle Entitäten zur einfachen Anbindung an bestehende Systeme.
- Automatische Validierung der Daten mit Pydantic-Schemata.

## Projektstruktur

```
app/
├── crud.py         # Datenbankoperationen
├── csv_io.py       # CSV Import/Export
├── database.py     # Datenbankkonfiguration
├── main.py         # FastAPI Applikation
├── models.py       # SQLAlchemy Modelle
└── schemas.py      # Pydantic Schemata
```

## Entwicklung & Tests

1. Abhängigkeiten installieren (inkl. Testwerkzeuge):
   ```bash
   pip install -e .[test]
   ```
2. Tests ausführen:
   ```bash
   pytest
   ```
3. Anwendung starten (lokal):
   ```bash
   uvicorn app.main:app --reload
   ```

Die API-Dokumentation ist nach dem Start der Anwendung unter `http://localhost:8000/docs` erreichbar.

## CSV Formate

Für den CSV-Austausch werden folgende Spalten erwartet bzw. bereitgestellt:

- **employees**: `personnel_number, first_name, last_name, department, role, active`
- **machines**: `code, name, description, location, active`
- **work_orders**: `order_number, customer, article, quantity, due_date, status`
- **operations**: `code, description, order_number, machine_code, standard_time_minutes, is_active`
- **activity_records**: `id, start_time, end_time, personnel_number, operation_code, quantity_good, quantity_reject, status, comment`

Zeitangaben werden im ISO-Format (`YYYY-MM-DDThh:mm:ss`) erwartet und geliefert.
