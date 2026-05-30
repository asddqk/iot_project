#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// WiFi
const char* ssid     = "Xiaomi_DBFF";
//const char* password = "1234qwer";

// MQTT — wqtt.ru
const char* mqtt_server   = "m4.wqtt.ru";
const int   mqtt_port     = 15940;        // твой порт с wqtt.ru
const char* mqtt_user     = "u_W69DQW";   // твой логин
const char* mqtt_pass     = "qqLgilhK";     // твой пароль
const char* mqtt_client   = "esp8266_socket";

// Топики
const char* topic_sub = "home/socket/command";   // сюда шлёт ноутбук
const char* topic_pub = "home/socket/status";    // сюда шлёт ESP статус

// Пин реле (LOW = включить, если реле инвертированное)
const int RELAY_PIN = D1;
//const int RELAY_PIN = D1;
bool relayState = false;

WiFiClient   espClient;
PubSubClient client(espClient);

void setup_wifi() {
  Serial.println();
  Serial.print("Подключение к WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    attempts++;
    if (attempts > 20) {
      Serial.println("\nНе удалось подключиться к WiFi!");
      return;
    }
  }
  Serial.println("\nWiFi подключён. IP: " + WiFi.localIP().toString());
}

void callback(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];
  Serial.println("MQTT IN [" + String(topic) + "]: " + msg);

  if (String(topic) == topic_sub) {
    if (msg == "ON") {
      digitalWrite(RELAY_PIN, HIGH);
      //digitalWrite(RELAY_PIN, LOW);   // LOW = замкнуть (зависит от реле)
      relayState = true;
      client.publish(topic_pub, "ON");
    } else if (msg == "OFF") {
      digitalWrite(RELAY_PIN, HIGH);
      digitalWrite(RELAY_PIN, LOW);
      //relayState = false;
      client.publish(topic_pub, "OFF");
    }
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("MQTT connecting...");
    if (client.connect(mqtt_client, mqtt_user, mqtt_pass)) {
      Serial.println("connected");
      client.subscribe(topic_sub);
      client.publish(topic_pub, "READY");
    } else {
      Serial.println("failed, rc=" + String(client.state()) + " retry in 5s");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(RELAY_PIN, OUTPUT);
  //digitalWrite(RELAY_PIN, HIGH);
  digitalWrite(RELAY_PIN, LOW);  // реле выключено при старте
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();
}