# 논리 DB my_sns의 users 테이블에 연결되는 클래스
from server import db
import datetime

class Users(db.Model):
    
    # SQLAlchemy 라이브러리의 Model 클래스를 활용
    # 1. 어느 테이블을 연결할건지
    __tablename__ = 'users'  # DB테이블 이름
    
    
    # 2. 어떤 변수들이 있고, 그 변수들이 어떤 컬럼에 연결되는지 => 변수이름과 컬럼이름은 같아야함
    id = db.Column(db.Integer, primary_key=True)  # id컬럼은 int로 되어있고 기본키라고 명시
    email = db.Column(db.String(50), nullable=False, default='이메일 미입력') # email컬럼은 50자 문구, null허용, 이메일미입력이라는 기본값 있다고 명시
    password = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(15))  # nullable의 기본값은 null허용이라서 nullable=False의 경우만 기재해줘도 됨
    
    birth_year = db.Column(db.Integer, nullable=False, default=1995)    
    # created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now()) # 일반 datetitme.datetime.now()를 하면 현재 작업중인 pc서버의 시간이 기록됨 => DB 현재시간 아님
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    
    # 3. 객체를 가지고 실제 dict로 변환해주는 메쏘드 생성(응답을 내려주는 용도)
    def get_data_object(self):
        data = {
            'id' : self.id,
            'email' : self.email,
            'name' : self.name,
            'phone' : self.phone,
            'birth_year' : self.birth_year,
            'created_at' : str(self.created_at),    # SQLAlchemy의 DateTime은 JSON응답 처리 불가 => str으로 변환해서 리턴
        } 
        
        return data