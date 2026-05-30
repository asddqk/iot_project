#include "esp_camera.h"
#include <WiFi.h>
#include "esp_http_server.h"

// ================= WIFI =================
const char* ssid = "12345678";
const char* password = "12345678";

// ================= CAMERA PINS (AI THINKER) =================
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5

#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ================= SERVER =================
httpd_handle_t stream_httpd = NULL;

// ================= MJPEG STREAM =================
static esp_err_t stream_handler(httpd_req_t *req)
{
    camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;

    // Разрешаем долгоживущее соединение
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    httpd_resp_set_hdr(req, "X-Framerate", "20");

    res = httpd_resp_set_type(req, "multipart/x-mixed-replace; boundary=frame");
    if (res != ESP_OK) return res;

    while (true)
    {
        fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("Frame capture failed, skipping...");
            vTaskDelay(pdMS_TO_TICKS(100)); // ждём пока буфер освободится
            continue;
        }

        // Проверяем что кадр валидный
        if (fb->len == 0) {
            esp_camera_fb_return(fb);
            vTaskDelay(pdMS_TO_TICKS(50));
            continue;
        }

        char header[128];
        int hlen = snprintf(header, sizeof(header),
            "--frame\r\n"
            "Content-Type: image/jpeg\r\n"
            "Content-Length: %u\r\n\r\n",
            fb->len
        );

        res = httpd_resp_send_chunk(req, header, hlen);
        if (res == ESP_OK)
            res = httpd_resp_send_chunk(req, (const char*)fb->buf, fb->len);
        if (res == ESP_OK)
            res = httpd_resp_send_chunk(req, "\r\n", 2);

        esp_camera_fb_return(fb); // ВСЕГДА возвращаем буфер

        if (res != ESP_OK) {
            Serial.println("Send failed, client disconnected");
            break;
        }

        vTaskDelay(pdMS_TO_TICKS(50));
    }

    return res;
}

// ================= SNAPSHOT =================
static esp_err_t capture_handler(httpd_req_t *req)
{
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }

    httpd_resp_set_type(req, "image/jpeg");
    httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg");
    httpd_resp_send(req, (const char*)fb->buf, fb->len);

    esp_camera_fb_return(fb);
    return ESP_OK;
}

// ================= START SERVER =================
void startServer()
{
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 80;

    httpd_uri_t stream_uri = {
        .uri = "/stream",
        .method = HTTP_GET,
        .handler = stream_handler,
        .user_ctx = NULL
    };

    httpd_uri_t capture_uri = {
        .uri = "/capture",
        .method = HTTP_GET,
        .handler = capture_handler,
        .user_ctx = NULL
    };

    if (httpd_start(&stream_httpd, &config) == ESP_OK)
    {
        httpd_register_uri_handler(stream_httpd, &stream_uri);
        httpd_register_uri_handler(stream_httpd, &capture_uri);
        Serial.println("HTTP server started");
    }
}

// ================= SETUP =================
void setup()
{
    Serial.begin(115200);
    delay(1000);

    // -------- CAMERA CONFIG --------
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer   = LEDC_TIMER_0;

    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;

    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;

    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;

    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;

    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;

    // ===== СТАБИЛЬНАЯ НАСТРОЙКА =====
    config.frame_size = FRAMESIZE_QQVGA;   // 160x120
    config.jpeg_quality = 25;
    config.fb_count = 1;
    config.grab_mode = CAMERA_GRAB_LATEST;

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed: 0x%x\n", err);
        return;
    }

    sensor_t *s = esp_camera_sensor_get();
    s->set_vflip(s, 1);
    s->set_hmirror(s, 0);

    // -------- WIFI --------
    WiFi.begin(ssid, password);
    Serial.print("Connecting");

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("\nWiFi connected!");
    Serial.print("Stream: http://");
    Serial.print(WiFi.localIP());
    Serial.println("/stream");

    Serial.print("Capture: http://");
    Serial.print(WiFi.localIP());
    Serial.println("/capture");

    startServer();
}

// ================= LOOP =================
void loop()
{
    Serial.printf("WiFi RSSI: %d dBm\n", WiFi.RSSI());
    delay(3000);
}