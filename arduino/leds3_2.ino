#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

// ⚙️ Datos de tu red WiFi
const char* ssid = "OPPO A58";         // Nombre del hotspot (cámbialo si usas otra red)
const char* password = "Juan_PR17";      // Contraseña del hotspot

// 🌐 Dirección IP del servidor Flask (¡la de tu laptop!)
const char* servidor = "http://192.168.161.49:5000/leds";  // ← PON AQUÍ la IP de tu laptop

// Pines de los LEDs
const int ledRojo = D3;   // GPIO0
const int ledVerde = D4;  // GPIO2
const int ledAzul = D7;   // GPIO13

void setup() {
  Serial.begin(115200);
  delay(10);

  pinMode(ledRojo, OUTPUT);
  pinMode(ledVerde, OUTPUT);
  pinMode(ledAzul, OUTPUT);

  Serial.println("📶 Conectando al WiFi...");
  WiFi.begin(ssid, password);

  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < 20) {
    delay(500);
    Serial.print(".");
    intentos++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ Conectado a WiFi.");
    Serial.print("IP local: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ No se pudo conectar a la red WiFi.");
  }
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    http.begin(client, servidor);  // ← API moderna con WiFiClient

    int httpCode = http.GET();
    if (httpCode == HTTP_CODE_OK) {
      String payload = http.getString();
      Serial.println("📦 JSON recibido:");
      Serial.println(payload);

      StaticJsonDocument<1024> doc;
      DeserializationError error = deserializeJson(doc, payload);

      if (!error) {
        JsonArray leds = doc["leds"];
        for (JsonObject led : leds) {
          int id = led["id"];
          bool status = led["status"];

          switch (id) {
            case 1:
              digitalWrite(ledRojo, status ? HIGH : LOW);
              Serial.println(status ? "🔴 Rojo ON" : "🔴 Rojo OFF");
              break;
            case 2:
              digitalWrite(ledVerde, status ? HIGH : LOW);
              Serial.println(status ? "🟢 Verde ON" : "🟢 Verde OFF");
              break;
            case 3:
              digitalWrite(ledAzul, status ? HIGH : LOW);
              Serial.println(status ? "🔵 Azul ON" : "🔵 Azul OFF");
              break;
          }
        }
      } else {
        Serial.print("❌ Error al parsear JSON: ");
        Serial.println(error.c_str());
      }
    } else {
      Serial.print("❌ Error HTTP: ");
      Serial.println(httpCode);
    }

    http.end();
  } else {
    Serial.println("⚠️ WiFi desconectado.");
  }

  delay(5000);  // Espera 5 segundos antes de la próxima consulta
}






