from flask import Flask, render_template, request #플라스크 앱 모듈 임포트

app = Flask(__name__) # 플라스크 앱 생성

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 #캐싱 비활성황

@app.route('/') #/ 라우트 설정
def index(): # /경로로 요청하면
    return render_template('view.html') #view.html 렌더링하여 return

if __name__ == '__main__': # 메인으로 실행되면
    app.run(host='0.0.0.0', port=8080, debug=True) #외부에서 접속 가능 
