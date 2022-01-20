# 토큰을 발급하고, 발급된 토큰이 들어오면 사용자가 누구인지 분석하는 등의 기능을 담당하는 파일
# JWT에 관한 기능을 모아두는 모듈로 만들거임

from functools import wraps
import jwt
from flask import current_app, g  # g: global의 약자. 프로젝트 전역에서 공유할 수 있는 메모 공간
from flask_restful import reqparse

from server.model import Users

token_parser =reqparse.RequestParser()
token_parser.add_argument('X-Http-Token', type=str, required=True, location='headers')  # 토큰을 받아오는 parser를 생성함

# 토큰을 만드는 함수를 정의 , 토큰 왜만들어? => 사용자를 인증하는 용도라서, 어떤 사용자에 대한 토큰인지 알아야함
def encode_token(user):
    
    # 발급된 토큰을 곧바로 리턴
    # 1 : 사용자의 어떤 항목들로 토큰을 만들건지? (토큰 구성요소)  >> 나중에 복호화해서 꺼낼 것을 고려해서, dict를 넣어서 암호화해주는게 좋음
    # 2 : 어떤 비밀키를 섞어서 암호화를 할건지?
    # 3 : 어떤 알고리즘으로 암호화를 할건지?
    return jwt.encode(
        {'id' : user.id, 'email' : user.email, 'password' : user.password_hashed},   # password변수는 쓰기 전용이기때문에, 실제 DB에 기록된 값 활용으로 변경함
        current_app.config['JWT_SECRET'],
        algorithm=current_app.config['JWT_ALGORITHM']
        )  # 이 실행 결과가 곧바로 토큰 str로 나옴
    

# 토큰값을 가지고, 복호화해서 사용자 객체(Users)로 변환하는 함수
def decode_token(token):
    
    try:
        # 이미 암호화가 된 string을 받아오면, 복호화를 거쳐, 이전에 넣었던 dict를 추출
        # 1 : 어떤 토큰을 해체할꺼야?
        # 2 : 풀어낼 때 어떤 비밀키로 복호화를 할건지?
        # 3 : 어떤 알고리즘으로 복호화를 할건지?
        decoded_dict = jwt.decode(
            token, 
            current_app.config['JWT_SECRET'],
            algorithms=current_app.config['JWT_ALGORITHM']
        )
        
        user = Users.query\
            .filter(Users.id == decoded_dict['id'])\
            .filter(Users.email == decoded_dict['email'])\
            .filter(Users.password_hashed == decoded_dict['password'])\
            .first()
            
        # 실제로 토큰이 제대로 들어왔다면, 복호화를 하면 제대로 된 정보가 들어있고, 그 정보를 가지고 사용자를 추출해서 리턴하는 기능으로 만든거임
            
        return user
    
    except jwt.exceptions.DecodeError:
        # 잘못된 토큰이 들어오면, 복호화에 실패하기 때문에 => 예외처리를 위해서 이쪽으로 빠짐.
        return None  # 토큰이 잘못됬으니까 사용자도 찾아내지 못했다고 리턴
    
    
# 데코레이터 사용 => 추가함수에 적힌 코드를 먼저 실행하고, 그 다음에 실제 함수를 이어서 진행하도록 하는 기능

# @추가함수 
# def 함수이름 : 

def token_required(func):
    
    @wraps(func)
    def decorator(*args, **kwargs):   # 어떤 모양의 함수든지 가능하다고 명시함  *args=> 몇개의 인자를 입력할 지 모를때, *kwargs => name:'전은형' 이렇게 입력할 때
        # 실제 함수 내용이 시작되기전에, 먼저 해줄 함수를 적는다
        
        # 1. 토큰 파라미터를 받자
        args = token_parser.parse_args()        
        
        # 2. 그 토큰으로 실제 사용자를 추출해보자
        user = decode_token(args['X-Http-Token'])
        
        # 3-1. 사용자가 제대로 나왔다면 올바른 토큰으로 간주해서 원래 함수의 내용을 실행하자
        if user:
            
            # 만약에 토큰으로 사용자를 찾아냈다면, 데코레이터가 붙어있는 원본 함수에서도 사용자를 가져다 쓰면 편할 것 같다
            # 전역변수를 이용해서, 사용자를 전달하자
            g.user = user
            
            return func(*args, **kwargs)  # 원래 함수 내용을 실행해서 리턴해라
        
        # 3-2. 사용자가 안나왔다면(None), 이유를 막론하고 잘못된 토큰이니까 403으로 에러 리턴
        else : 
            return {
                'code' : 403,
                'message' : '올바르지 않은 토큰입니다.'
            }, 403
            
    # token_required이름표가 붙은 함수들에게 decorator라는 함수를 전달해주자
    return decorator

# 다른 함수의 시작 전에, 토큰을 통해 얻어낸 사용자가 관리자가 맞는지만 추가 검사하는 데코레이터
def admin_required(func):
    
    @wraps(func)
    def decorator(*args, **kwargs):
        # 토큰으로 사용자는 받아냈다고 전제하자 => g변수에 이미 user가 들어있다
        user = g.user
        
        if not user.is_admin:
            return {
                'code' : 403,
                'message' : '관리자 권한이 없습니다.'
            }, 403
            
        return func(*args, **kwargs)
    
    return decorator