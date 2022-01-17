# 논리 DB my_sns의 users 테이블에 연결되는 클래스
from server import db

class Users(db.Model):
    
    # SQLAlchemy 라이브러리의 Model 클래스를 활용
    # 1. 어느 테이블을 연결할건지
    # 2. 어떤 변수들이 있고, 그 변수들이 어떤 컬럼에 연결되는지
    # 3. 객체를 가지고 실제 dict로 변환해주는 메쏘드 생성(응답을 내려주는 용도)
    pass