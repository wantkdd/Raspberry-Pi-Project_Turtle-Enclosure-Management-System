import time
import paho.mqtt.client as mqtt
import circuit

# MQTT 클라이언트 콜백 함수 설정
def on_connect(client, userdata, flags, rc, prop=None):
    client.subscribe("led_control") # led_control 토픽 구독

def on_message(client, userdata, message): #메시지 도착하면 
    led_count = int(message.payload) #led 개수 저장
    circuit.controlIlluminance(led_count) #메시지 도착하면 조도 제어 함수 출력

def publish_data():
    try:
        temperature = circuit.getTemperature() #온도 저장
        humidity = circuit.getHumidity() #습도 저장
        light = circuit.getIlluminance() #조도 저장
        distance = circuit.measureDistance(circuit.trig,circuit.echo) #거리 저장

        client.publish("temperature", temperature, qos=1) #temperature 토픽으로 온도 publish
        client.publish("humidity", humidity, qos=1) #humidity 토픽으로 습도 publish
        client.publish("illuminance", light, qos=1) #illuminance 토픽으로 조도 publish
        client.publish("distance",distance, qos=1) #distance 토픽으로 거리 publish

        circuit.controlAutoFeeder(client) #자동급식기 작동 함수 호출

        if distance <= 20 or temperature > 25 or humidity > 50:
            circuit.led_on_off(circuit.red, 1)  # 조건 중 하나라도 충족되면 LED 켜기
        else:
            circuit.led_on_off(circuit.red, 0)  # 모두 충족되지 않으면 LED 끄기

        if distance <= 20: #거리가 20이하이면
            img_path = circuit.take_photo() #사진 촬영하여 경로 젖ㅇ
            if img_path: # 경로가 none이 아니면
                client.publish("doorPhoto", img_path, qos=1) #사진 publish

    except Exception as e: #예외처리
        print(f"Error in publish_data: {e}") #예외 내용 출력

# MQTT 브로커 정보 설정
broker_ip = "192.168.137.24"
broker_port = 1883
 
# MQTT 클라이언트 객체 생성
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

# MQTT 클라이언트 연결
client.connect(broker_ip, broker_port, keepalive=120)

# MQTT 클라이언트 루프 시작
client.loop_start()

try:
    while True: #무한 루프 시작
        publish_data() #publish 함수 호출
        time.sleep(1) #간격 설정
except KeyboardInterrupt: 
    client.loop_stop()
    client.disconnect()
