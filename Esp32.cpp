WiFi und HTTP-Bibliotheken: Import der benötigten Bibliotheken für die WLAN-Verbindung und die HTTP-Kommunikation.

Konstanten für WLAN und API: Festlegung der WLAN-Zugangsdaten und der URL sowie des API-Schlüssels für die Flask API.

Variablen für Ort und Sensordaten: Definition von Variablen für den Messort, ESP-Namen und Sensornamen.

DHT-Sensor-Konfiguration: Konfiguration des DHT-Sensors für die Temperatur- und Luftfeuchtigkeitsmessung.

setup()-Funktion: Initialisierung der Seriellen Kommunikation, Verbindung zum WLAN und Start des DHT-Sensors.

loop()-Funktion: Hauptprogrammschleife, die die Temperatur und Luftfeuchtigkeit misst, ein JSON-Objekt erstellt und an die Flask API sendet. Wartet dann 10 Sekunden, bevor der nächste Messzyklus beginnt.


#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <WiFiClientSecure.h>
#include <esp_crt_bundle.h>
#include <ssl_client.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <ArduinoJson.hpp>

// WiFi-Zugangsdaten
const char* ssid = "1";
const char* password = "12345678";

// URL und API-Schlüssel für die Flask API
const char* api_url = "http://tobiaswiechmann.de:8080/data";
const char* api_key = "123321";

// Variablen für Ort und Sensorinformationen
String messort;
String espname;
String sensorname;

// DHT-Sensor
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  
  // Verbindung zum WLAN herstellen
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Verbunden mit WLAN");

  // Initialisiere den DHT-Sensor
  dht.begin();
}

void loop() {
  // Lese die Temperatur und Luftfeuchtigkeit
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  // Festlegen des Messorts, ESP-Namens und Sensornamens
  messort = "Büro";
  espname = "ESP32";
  sensorname = "DHT22";

  // Erstellen eines JSON-Objekts mit den Sensordaten
  DynamicJsonDocument jsonDocument(200);
  jsonDocument["messort"] = messort;
  jsonDocument["espname"] = espname;
  jsonDocument["sensorname"] = sensorname;
  jsonDocument["temperature"] = temperature;
  jsonDocument["humidity"] = humidity;

  // Sende das JSON-Objekt an die Flask API
  HTTPClient http;
  http.begin(api_url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Authorization", "Bearer " + String(api_key));

  // Konvertiere das JSON-Objekt in einen String
  String jsonPayload;
  serializeJson(jsonDocument, jsonPayload);

  // Sende das HTTP-POST-Anfrage
  int httpCode = http.POST(jsonPayload);
  if (httpCode == 200) {
    Serial.println("Daten an die Flask API gesendet");
  } else {
    Serial.println("Fehler beim Senden der Daten an die Flask API");
    Serial.println("httpCode: " + httpCode);
  }
  http.end();

  // Warte 10 Sekunden, bevor der nächste Messzyklus beginnt
  delay(10000);
}
