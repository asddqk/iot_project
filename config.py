CAM_EYE_IP   = "192.168.1.208"   # обновлённый IP
CAM_ROOM_IP  = "192.168.43.100"  # вторая камера пока старый

CAM_EYE_STREAM   = f"http://{CAM_EYE_IP}/stream"
CAM_ROOM_CAPTURE = f"http://{CAM_ROOM_IP}/capture"

MQTT_BROKER = "localhost"
MQTT_PORT   = 1883

# EAR_THRESHOLD     = 0.22   # чуть строже чтобы не было ложных срабатываний
# EAR_CONSEC_FRAMES = 1      # 1 кадр вместо 2 — быстрее реагирует
# DOUBLE_BLINK_SEC  = 2.0    # увеличь окно до 2 секунд — больше времени на двойное моргание