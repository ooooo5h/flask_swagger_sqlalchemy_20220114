from flask import Flask
from flask_restful_swagger_2 import Api

def create_app(config_name):
    app = Flask(__name__)
    
    # 만들어진 앱에, (server>config>환경클래스) 환경 설정을 불러오자
    app.config.from_object(f'server.config.{config_name}')
    
    # 클래스에 있는 함수들을 자동으로, 기능으로 연결해주는 라이브러리 세팅, 부가 환경설정도 진행
    api = Api(app, api_speck_url='/api/spec', title='my_server spec', api_version='0.1', catch_all_404s=True)
    
    return app