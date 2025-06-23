#include <Arduino.h>
#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <Servo.h>

// WiFi credentials
const char *ssid = "YOUR_SSID";
const char *password = "YOUR_PASSWORD";

// Servo pins
const int servoPins[3] = {13, 12, 14}; // Change to your preferred pins

Servo servos[3];
AsyncWebServer server(80);

void connectToWiFi()
{
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected! IP address: " + WiFi.localIP().toString());
}

void setup()
{
  Serial.begin(115200);

  // Attach servos to pins
  for (int i = 0; i < 3; i++)
  {
    servos[i].attach(servoPins[i]);
  }

  connectToWiFi();

  server.on("/move", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    if (!request->hasParam("servo") || !request->hasParam("place")) {
      request->send(400, "text/plain", "Missing parameters");
      return;
    }

    int servoIndex = request->getParam("servo")->value().toInt();
    int place = request->getParam("place")->value().toInt();

    if (servoIndex < 0 || servoIndex >= 3 || place < 0 || place > 180) {
      request->send(400, "text/plain", "Invalid servo index or position");
      return;
    }

    servos[servoIndex].write(place);
    String response = "Moved servo " + String(servoIndex) + " to position " + String(place);
    request->send(200, "text/plain", response); });

  server.begin();
}

void loop()
{
  // Nothing needed here; all handled asynchronously
}
