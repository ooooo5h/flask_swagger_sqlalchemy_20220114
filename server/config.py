# 플라스크에서 적용 가능한 환경설정들을 모아두는 클래스가 될 예정
"""
Flask Configuration
"""

class Config(object):
    DEBUG = False
    TESTING = False

    # SQLAlchemy가 접속할 DB연결 정보(URI)
    # SQLAlchemy 라이브러리가, 어떤 변수를 끌어다 쓸지도 미리 지정되어 있음 => 변수이름 바꾸면 동작 안될 수도 있음
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://아이디:비밀번호@DB호스트주소/논리DB이름"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://admin:admin123"+\
                            "@my-first-db2.ckcb9pt3t4a9.ap-northeast-2.rds.amazonaws.com/my_sns"
                            
    # DB변경사항을 추적하는 기능 임시로 꺼두기
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # S3 접속 정보들을 변수들로 저장
    AWS_ACCESS_KEY_ID = 'AKIA2M6T2DEZLNT6VYXT'
    AWS_SECRET_ACCESS_KEY = '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'
    AWS_S3_BUCKET_NAME = 'neppplus.python.20220118.jeh'   # 어느 저장소에 저장할건지 이름(버킷이름)
    
    # 토큰 발급용 암호화 로직 이름 / 사용할 키값
    JWT_ALGORITHM = 'HS512'
    JWT_SECRET = 'my_strong_key'  # 임시 문구 -> 원하는 대로 변경 -> 타인에게 노출되면 안됨
    
    
    # 알리고 서버에서 제공하는 API 키
    ALIGO_API_KEY = 'i5m8plmyxhcpwfvty29hbzko2zzgi0nq'

class ProductionConfig(Config):
    # 기본 설정 그대로 실 서버에서도 적용시킬 예정
    pass

class TestConfig(Config):
    TESTING = True   # 테스팅 환경이 맞다고 설정
    
class DebugConfig(Config):
    DEBUG = True     # 개발 모드가 맞다고 설정