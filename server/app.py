from flask import Flask

def create_app(config_name):
    app = Flask(__name__)
    
    # 만들어진 앱에, (server>config>환경클래스) 환경 설정을 불러오자
    app.config.from_object(f'server.config.{config_name}')
    
    return app