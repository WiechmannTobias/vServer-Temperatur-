import pymysql
from datetime import datetime
import jinja2
import time
from flask import Flask, request, jsonify

# Flask-App initialisieren
app = Flask(__name__)

api_key = "123321"

# Datenbankverbindung herstellen
connection = pymysql.connect(
    host="localhost",
    user="Master",
    password="M1!)fwntov2!",
    database="my_database"
)

# Template laden

# Import der Jinja2-Bibliothek
import jinja2

# Template laden
template_str = """
<!DOCTYPE html>
<html lang="de">
<head>
<link href="https://unpkg.com/gridjs/dist/theme/mermaid.min.css" rel="stylesheet" />
    <meta charset="UTF-8">
    <title>Wetterdaten</title>
    <style>
        body {
            font-family: sans-serif;
        }

        table {
            border-collapse: collapse;
            width: 500px;
        }

        th, td {
            border: 1px solid black;
            padding: 10px;
        }

        th {
            text-align: center;
        }

        .header {
            text-align: center;
        }

        .temp, .humid {
            font-weight: bold;
            text-align: center;
        }

        canvas {
            display: block;
            margin: 0 auto;
        }
    </style>
    <script src="https://unpkg.com/gridjs/dist/gridjs.umd.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Wetterdaten</h1>
        </div>
        <input type="text" id="myInput" onkeyup="filterTable()" placeholder="Search for values..">

        <!-- Ergänzte HTML-Teile -->
        <label for="startTime">Startzeit:</label>
        <input type="datetime-local" id="startTime" onchange="updateCharts()">
        <label for="endTime">Endzeit:</label>
        <input type="datetime-local" id="endTime" onchange="updateCharts()">

        <div class="temp">
            <h2>Temperatur</h2>
            <canvas id="tempChart" width="400" height="200"></canvas>
        </div>
        <div class="humid">
            <h2>Luftfeuchtigkeit</h2>
            <canvas id="humidChart" width="400" height="200"></canvas>
        </div>
        <div id="wrapper"></div>
    </div>

    <script>
        // Jinja2-Code für die Daten
        var data = {{ data | tojson | safe }};

        // Grid.js
        var grid = new gridjs.Grid({
            search: true,
            columns: ["Messpunkt", "Temperatur", "Luftfeuchtigkeit", "Messort", "ESP-Name", "Sensorname", "Zeitstempel"],
            data: data
        }).render(document.getElementById("wrapper"));

        // Chart.js
        function updateCharts() {
            // Daten aus den letzten 15 Einträgen abrufen
            var labels = data.slice(-15).map(function(row) {
                return row[0];
            });

            var tempData = {
                labels: labels,
                datasets: [{
                    label: 'Temperature',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    data: data.slice(-15).map(function(row) {
                        return row[1];
                    })
                }]
            };

            var humidData = {
                labels: labels,
                datasets: [{
                    label: 'Humidity',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    data: data.slice(-15).map(function(row) {
                        return row[2];
                    })
                }]
            };

            var tempCtx = document.getElementById('tempChart').getContext('2d');
            var tempChart = new Chart(tempCtx, {
                type: 'line',
                data: tempData,
            });

            var humidCtx = document.getElementById('humidChart').getContext('2d');
            var humidChart = new Chart(humidCtx, {
                type: 'line',
                data: humidData,
            });
        }
    </script>
</body>
</html>
"""

# Erzeuge ein Jinja2-Template-Objekt
template = jinja2.Template(template_str)


# Zeitgeber erstellen
def update_page():
    # Daten aus der Datenbank abrufen
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM wetterdaten ORDER BY id DESC LIMIT 15")
    latest_data = cursor.fetchall()
    latest_data = [list(row) for row in latest_data]

    for row in latest_data:
        try:
            row[6] = datetime.isoformat(row[6])
        except:
            pass

    cursor.execute("SELECT * FROM wetterdaten")
    all_data = cursor.fetchall()

    # Template mit Daten ausfüllen
    html = template.render(data=latest_data, data2=all_data)

    # HTML-Datei speichern
    with open("/var/www/html/index.nginx-debian.html", "w") as f:
        f.write(html)

# Route für den Datenempfang
@app.route("/data", methods=["POST"])
def receive_data():
    erhalten_key = request.headers.get('Authorization')

    if erhalten_key == f"Bearer {api_key}":
        # Authentifizierung erfolgreich, verarbeite die Daten
        data = request.get_json()
        temperature = data["temperature"]
        humidity = data["humidity"]
        messort = data["messort"]
        espname = data["espname"]
        sensorname = data["sensorname"]
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        # Daten in die Datenbank schreiben
        cursor = connection.cursor()
        cursor.execute("INSERT INTO wetterdaten (temperatur, luftfeuchtigkeit, messort, espname, sensorname, timestamp) VALUES (%s, %s, %s, %s, %s, %s)", (temperature, humidity, messort, espname, sensorname, timestamp))
        connection.commit()

        # Aktualisieren der HTML-Seite nach dem Einfügen der Daten
        update_page()

        # Erfolg zurückgeben
        return jsonify({"success": True})
    else:
        jsonify({"Error": True})

# App starten
if __name__ == '__main__':
    app.run(debug=True, host='tobiaswiechmann.de', port=8080)
