let client = null; //client 객체
let connectionFlag = false; //브로커 연결 상태 깃발

function connect() {
  //브로커 연결
  if (connectionFlag == true) return; //연결된 상태이면 return

  const broker = '192.168.137.24'; //라즈베리 파이 ip
  const port = 9001; //웹소켓 포트

  client = new Paho.MQTT.Client(broker, port, 'client'); //client 객체 생성

  client.onConnectionLost = onConnectionLost; //연결 끊길 시 호출할 함수
  client.onMessageArrived = onMessageArrived; //메시지 도착시 호출할 함수

  client.connect({
    //mqtt연결
    onSuccess: onConnect, //연결 성공시 onConnect함수 호출
  });
}

function onConnect() {
  client.subscribe('temperature'); //temperature 구독
  client.subscribe('humidity'); //humidity 구독
  client.subscribe('illuminance'); //illuminance 구독
  client.subscribe('switch_state'); //switch_state구독
  client.subscribe('distance'); //distance구독
  client.subscribe('doorPhoto'); //doorPhoto 구독
  connectionFlag = true; //연결 상태 깃발 올림
}

function onMessageArrived(message) {
  switch (
    message.destinationName //토픽으로 나눔
  ) {
    case 'temperature': //temperature 토픽이라면
      const tem = parseFloat(message.payloadString).toFixed(2); //소숫점 두 자리까지 tem 저장
      document.getElementById('temperature').textContent = tem + '°C'; //화면에 온도 출력
      if (tem > 25) {
        //25도 초과면
        document.getElementById('temperature-warning').textContent = '경고'; //경고 출력
      } else {
        //이하이면
        document.getElementById('temperature-warning').textContent = '정상'; //정상 출력
      }
      break; //탈출
    case 'humidity': //humidity 토픽이라면
      const hum = parseFloat(message.payloadString).toFixed(2); //소숫점 두 자리까지 hum 저장
      document.getElementById('humidity').textContent = hum + '%'; //화면에 습도 출력
      if (hum > 50) {
        //50% 초과이면
        document.getElementById('humidity-warning').textContent = '경고'; //경고 출력
      } else {
        //이하이면
        document.getElementById('humidity-warning').textContent = '정상'; //정상 출력
      }
      break; //탈출
    case 'illuminance': //illuminance 토픽이라면
      const lightLevel = parseInt(message.payloadString, 10); //10자리까지 정수로 lightlevel 저장
      document.getElementById('light-level').textContent =
        message.payloadString + ' lx'; //화면에 조도 출력
      if (lightLevel >= 300) {
        //300이상이면
        document.getElementById('day-night').textContent = '낮'; //낮 출력
      } else {
        //미만이면
        document.getElementById('day-night').textContent = '밤'; //밤 출력
      }
      break; //탈출
    case 'switch_state': //switch_state 토픽이라면
      if (message.payloadString == 'True')
        //스위치가 눌렸다면
        document.getElementById('feeder-status').textContent = 'ON'; //on 출력
      else document.getElementById('feeder-status').textContent = 'OFF'; //아니면 off출력
      break; //탈출
    case 'distance': //distance 토픽이라면
      const distance = parseFloat(message.payloadString).toFixed(2); //소숫점 두 자리까지 distance 저장
      document.getElementById('door-distance').textContent = distance + ' cm'; //화면에 거리 출력
      if (distance < 20) {
        //거리가 20미만이면
        document.getElementById('door-warning').textContent = '경고'; //경고 문구 출력
      } else {
        document.getElementById('door-warning').textContent = '정상'; //정상 문구 출력
      }
      const alertFlag = false;
      if (distance < 10) {
        //거리가 10미만이면
        if (alertFlag) return;
        else {
          alert('거북이 탈출 위험!! 사육장으로 가보세요!'); //위험 안내
          alertFlag = true;
        }
      }
      addChartData(parseFloat(distance)); // 차트 데이터 업데이트
      break;
    case 'doorPhoto': //토픽이 doorPhoto이면
      const imgPath = message.payloadString; //사진경로 가져와서
      document.getElementById('door-image').src =
        imgPath + `?t=${new Date().getTime()}`; //사진 출력 (캐싱 방지)
      break;
  }
}

function onConnectionLost(responseObject) {
  //연결 끊기면 호출
  connectionFlag = false; //플래그 내림
}

let ledCount = 0; //led 개수

function setupLEDControls() {
  const increaseBtn = document.getElementById('increase-led'); //led 증가버튼
  const decreaseBtn = document.getElementById('decrease-led'); //led 감소 버튼
  const ledCountDisplay = document.getElementById('led-count'); //led 개수 표시

  increaseBtn.addEventListener('click', () => {
    if (ledCount < 2) {
      //2개 이하까지
      ledCount++; //led 개수 증가
      updateLEDCount(ledCount); //led개수 업데이트
    }
  });

  decreaseBtn.addEventListener('click', () => {
    if (ledCount > 0) {
      //0개이상까지
      ledCount--; //led 개수 감소
      updateLEDCount(ledCount); //led 개수 업데이트
    }
  });

  function updateLEDCount(count) {
    ledCountDisplay.textContent = count; //현재 led개수 표시
    client.send('led_control', String(count), (qos = 1)); //led 개수 전송
  }
}

window.onload = function () {
  connect(); //mqtt 연결
  setupLEDControls(); //led제어 초기화
  drawChart(); //차트 그림
};
