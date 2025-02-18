import time
import RPi.GPIO as GPIO
import Adafruit_MCP3008
from adafruit_htu21d import HTU21D
import busio
import cv2

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# LED 핀 번호 설정
white_1 = 5
white_2 = 6
red = 13
green = 19
GPIO.setup(white_1, GPIO.OUT)
GPIO.setup(white_2, GPIO.OUT)
GPIO.setup(red, GPIO.OUT)
GPIO.setup(green, GPIO.OUT)
    
# 스위치 핀 설정
switch = 21
GPIO.setup(switch, GPIO.IN, GPIO.PUD_DOWN)

# 초음파 센서 핀 설정
trig = 20
echo = 16
GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)

# I2C 버스 설정
i2c = busio.I2C(3, 2)  # SCL1 (GPIO 3), SDA1 (GPIO 2)
sensor = HTU21D(i2c)   # HTU21D 온습도 센서 객체 생성

# ADC 설정 (조도 센서)
mcp = Adafruit_MCP3008.MCP3008(clk=11, cs=8, miso=9, mosi=10)

#led 제어 함수
def led_on_off(pin, value):
  GPIO.output(pin, value)

#흰 색 led 제어 함수
def controlIlluminance(count):
    # 0개일 때 모두 끔
  led_on_off(white_1, GPIO.LOW)
  led_on_off(white_2, GPIO.LOW)
    #1개일 때 1개만 켬
  if count == 1:
    led_on_off(white_1, GPIO.HIGH)
    led_on_off(white_2, GPIO.LOW)
    #2개일 때 2개 전부 켬
  if count == 2:
    led_on_off(white_1, GPIO.HIGH)
    led_on_off(white_2, GPIO.HIGH)

def getTemperature() : # 센서로부터 온도 값 수신 함수
  return round(float(sensor.temperature),2) # HTU21D 장치로부터 온도 값 읽기

def getHumidity() : # 센서로부터 습도 값 수신 함수
  return round(float(sensor.relative_humidity),2) # HTU21D 장치로부터 습도 값 읽기

def measureDistance(trig, echo):
  time.sleep(0.2) # 초음파 센서의 준비 시간을 위해 200밀리초 지연
  GPIO.output(trig, 1) # trig 핀에 1(High) 출력
  GPIO.output(trig, 0) # trig 핀에 0(Low) 출력. High->Low. 초음파 발사 지시

  while(GPIO.input(echo) == 0): # echo 핀 값이 0->1로 바뀔 때까지 루프
    pass

  # echo 핀 값이 1이면 초음파가 발사되었음# 초음파 발사 시간 기록
  pulse_start = time.time()
  while(GPIO.input(echo) == 1): # echo 핀 값이 1->0으로 바뀔 때까지 루프
    pass
  
  # echo 핀 값이 0이 되면 초음파 수신하였음
  pulse_end = time.time() # 초음파가 되돌아 온 시간 기록
  pulse_duration = pulse_end - pulse_start # 경과 시간 계산
  return round(pulse_duration*340*100/2,2) # 거리 계산하여 리턴(단위 cm)

# 조도 센서 데이터 읽기
def getIlluminance():
    # MCP3008에서 조도 값을 읽는 코드 (채널 0)
    light_intensity = mcp.read_adc(0)  # 채널 0에 연결된 조도 센서 데이터 읽기
    return light_intensity

# 스위치 상태 읽기  
def getSwitchState():
    return GPIO.input(switch) == GPIO.LOW  # 스위치가 눌리면 LOW

# 스위치 상태 읽기  
def controlAutoFeeder(client):
    switch_status = GPIO.input(switch)  # 스위치 상태 읽기
    led_on_off(green, switch_status)   # 스위치 상태에 따라 LED 제어
    client.publish("switch_state", "True" if switch_status else "False", qos=1)  # MQTT 메시지 전송


camera = cv2.VideoCapture(0, cv2.CAP_V4L) # 카메라 객체 생성
camera.set(cv2.CAP_PROP_BUFFERSIZE, 10) # 버퍼 크기를 10으로

def take_picture( ):
  size = camera.get(cv2.CAP_PROP_BUFFERSIZE) # 버퍼 크기를 읽어온다
  while size > 0: # 버퍼 내에 저장된 모든 프레임을 버린다
    camera.grab( ) # camera.read( )로 해도 됨
    size -= 1
  ret, frame = camera.read( ) # 버퍼에 있는 현재 프레임을 읽는다.
  return frame if ret == True else None

def take_photo():
    frame = take_picture()  # 한 장의 이미지를 가져옴
    if frame is not None:
        file_name = f"./static/image.jpg"
        cv2.imwrite(file_name, frame)  # 프레임을 jpg 파일에 저장
        return file_name  # 저장된 파일 경로를 반환
    return None
