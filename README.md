# IoT System for Hands-Free Smart Home Control

## Overview

This project implements a hands-free smart home control system using computer vision, IoT technologies, and embedded devices.

The system detects user hand gestures through a camera, classifies them using a computer vision model, and sends commands to smart home devices through MQTT. Device states are managed and visualized in Home Assistant.

## Technologies

### Computer Vision

* Python
* OpenCV
* MediaPipe
* NumPy

### IoT & Embedded

* ESP32-CAM
* ESP32
* MQTT
* Wi-Fi

### Smart Home

* Home Assistant
* Mosquitto MQTT Broker

### Development Tools

* Arduino IDE
* VS Code
* Postman

## System Architecture

```text
Camera
   │
   ▼
Computer Vision Model
   │
   ▼
Gesture Recognition
   │
   ▼
MQTT Broker
   │
   ▼
ESP32 Device
   │
   ▼
Smart Home Appliance
```

## Features

### Gesture Recognition

Supported commands:

* Turn light ON
* Turn light OFF
* Toggle device state
* Additional custom gestures

### IoT Communication

* MQTT publish/subscribe messaging
* Real-time command delivery
* Device state synchronization

### Smart Home Integration

* Home Assistant dashboard
* Real-time device monitoring
* Remote control capabilities
* Device status visualization

## Hardware Components

* ESP32-CAM
* ESP32 Development Board
* LED Module (for demonstration)
* Wi-Fi Network

## Software Components

### Computer Vision Module

Responsible for:

* Video capture
* Hand detection
* Landmark extraction
* Gesture classification
* Command generation

### MQTT Communication Layer

Responsible for:

* Publishing commands
* Receiving device states
* Message routing

### Embedded Controller

Responsible for:

* Receiving MQTT messages
* Processing commands
* Controlling connected devices

## Project Structure

```text
iot-smart-home-control/
│
├── cv/
│   ├── camera.py
│   ├── config.py
│   ├── main.py
│   ├── roomCamera.py
│   └── eyeStream.py
│
├── esp32/
│   ├── eyeStream.ino
│   ├── roomCamera.ino
│   └── esp8266.ino
│
└── README.md
```

## Workflow

1. Camera captures video stream.
2. Hand landmarks are detected using MediaPipe.
3. Gesture is classified.
4. Command is sent via MQTT.
5. ESP32 receives the command.
6. Smart device state is updated.
7. Home Assistant displays the current status.

## Results

The system successfully demonstrates:

* Real-time gesture recognition
* Wireless IoT communication
* Smart home automation
* Integration between Computer Vision and Embedded Systems

## Skills Demonstrated

* Computer Vision
* Machine Learning Fundamentals
* OpenCV
* MediaPipe
* MQTT Protocol
* IoT Development
* ESP32 Programming
* Home Assistant Integration
* Embedded Systems
* Python Development

## Future Improvements

* Deep learning-based gesture recognition
* Multiple device control
* User authentication
* Voice and gesture hybrid control
* Cloud connectivity
