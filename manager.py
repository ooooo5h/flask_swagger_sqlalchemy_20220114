# 서버를 구동시키는 역할
# 디버그 / 테스트 / 라이브 모드 설정 => flask_script 라이브러리 활용 

from server import create_app

app = create_app()

# 디버그 모드 => 파이썬 파일을 저장하면 서버도 자동으로 재시작되게

app.run(host='0.0.0.0')