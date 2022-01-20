# 논리 DB my_sns의 users 테이블에 연결되는 클래스
from server import db
import datetime
import hashlib

class Users(db.Model):
    
    # SQLAlchemy 라이브러리의 Model 클래스를 활용
    # 1. 어느 테이블을 연결할건지
    __tablename__ = 'users'  # DB테이블 이름
    
    
    # 2. 어떤 변수들이 있고, 그 변수들이 어떤 컬럼에 연결되는지 => 변수이름과 컬럼이름은 같아야함
    id = db.Column(db.Integer, primary_key=True)  # id컬럼은 int로 되어있고 기본키라고 명시
    email = db.Column(db.String(50), nullable=False, default='이메일 미입력') # email컬럼은 50자 문구, null허용, 이메일미입력이라는 기본값 있다고 명시
    password_hashed = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(15))  # nullable의 기본값은 null허용이라서 nullable=False의 경우만 기재해줘도 됨
    
    birth_year = db.Column(db.Integer, nullable=False, default=1995)    
    is_male = db.Column(db.Boolean, default=False)   # 남성/여성여부를 bool로 표현(0과 1)   
    profile_img_url = db.Column(db.String(200))
    # created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now()) # 일반 datetitme.datetime.now()를 하면 현재 작업중인 pc서버의 시간이 기록됨 => DB 현재시간 아님
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    retired_at = db.Column(db.DateTime)
    
    # cf) Feeds테이블에서, Users로 외래키를 들고 연결을 설정한 상태
    # Users의 입장에서는 Feeds 테이블에서 본인을 참조하는 row들이 여러개가 있을 예정
    my_feeds = db.relationship('Feeds', backref='writer')
    
    # 3. 객체를 가지고 실제 dict로 변환해주는 메쏘드 생성(응답을 내려주는 용도)
    # 사용자 입장에서는 게시글 정보가 항상 필요한건 아님
    def get_data_object(self, need_feeds=False):
        data = {
            'id' : self.id,
            'email' : self.email,
            'name' : self.name,
            'phone' : self.phone,
            'birth_year' : self.birth_year,
            'profile_img_url' : f"https://s3.ap-northeast-2.amazonaws.com/neppplus.python.20220118.jeh/{self.profile_img_url}" if self.profile_img_url else None,  # 프사가 있다면 S3주소로 가공해서 내려주고, 없다면 None으로 내려주자
            'created_at' : str(self.created_at),    # SQLAlchemy의 DateTime은 JSON응답 처리 불가 => str으로 변환해서 리턴
            'retired_at' : str(self.retired_at) if self.retired_at else None,
        } 
        
        if need_feeds:
            data['my_feeds'] = [feed.get_data_object(need_writer=False) for feed in self.my_feeds]
        
        # print(f"내 게시글들 :  {self.my_feeds}")
        
        return data
    
    # 비밀번호 암호화에 관련된 기능들
    
    # 코드에서는 사용자.password = 비밀번호값 형태로 사용을 지원하고 싶다
    # 대입은 가능하지만 읽기는 불가능 => 원문 파악이 되면 안되기 때문에!!!
    @property
    def password(self):   # 조회하려는 상황에서 에러 처리
        raise AttributeError('password 변수는 쓰기 전용입니다. 조회는 불가합니다.')
    
    # password변수에 대입은 허용해주고 싶다
    @password.setter
    def password(self, input_password):
        # password = 대입값   >> 이 상황에서 대입값을 input_password에 담아주자
        # 비밀번호 원문을 가지고, 암호화를 해서 대입하자
        self.password_hashed = self.generate_password_hash(input_password)
        
    # 함수 추가 - 비밀번호 원문을 입력받으면, 그거를 가지고 암호화해주는 함수
    def generate_password_hash(self, input_password):
        
        # 입력받은 비밀번호를 SHA512로 변환해보자. (맞추기 어렵다/ 길이가 길게 나온다)  1차 암호화
        pre_hashed = hashlib.sha512(input_password.encode('utf8')).hexdigest()
            
        # 1차 암호화된 결과물을 다시 md5라는 걸로 변환해보자 => hashlib모듈을 활용하자는 이야기
        return hashlib.md5(pre_hashed.encode('utf8')).hexdigest()
    
    # 비밀번호 원문을 받아서, 비밀번호가 맞는지 암호화된 값 끼리 비교해보는 함수
    def verify_password(self, input_password):
        
        # 입력된 비밀번호를 암호화해두자
        hashed_input_pw = self.generate_password_hash(input_password)
        
        # 암호화한 후, 내 암호화된 비밀번호랑 같은지 비교해보자
        return self.password_hashed == hashed_input_pw