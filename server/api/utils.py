# 토큰을 발급하고, 발급된 토큰이 들어오면 사용자가 누구인지 분석하는 등의 기능을 담당하는 파일
# JWT에 관한 기능을 모아두는 모듈로 만들거임

import jwt
from flask import current_app
from server.model import Users

# 토큰을 만드는 함수를 정의 , 토큰 왜만들어? => 사용자를 인증하는 용도라서, 어떤 사용자에 대한 토큰인지 알아야함
def encode_token(user):
    
    # 발급된 토큰을 곧바로 리턴
    # 1 : 사용자의 어떤 항목들로 토큰을 만들건지? (토큰 구성요소)  >> 나중에 복호화해서 꺼낼 것을 고려해서, dict를 넣어서 암호화해주는게 좋음
    # 2 : 어떤 비밀키를 섞어서 암호화를 할건지?
    # 3 : 어떤 알고리즘으로 암호화를 할건지?
    return jwt.encode(
        {'id' : user.id, 'email' : user.email, 'password' : user.password}, 
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
            .filter(Users.password == decoded_dict['password'])\
            .first()
            
        # 실제로 토큰이 제대로 들어왔다면, 복호화를 하면 제대로 된 정보가 들어있고, 그 정보를 가지고 사용자를 추출해서 리턴하는 기능으로 만든거임
            
        return user
    
    except jwt.exceptions.DecodeError:
        # 잘못된 토큰이 들어오면, 복호화에 실패하기 때문에 => 예외처리를 위해서 이쪽으로 빠짐.
        return None  # 토큰이 잘못됬으니까 사용자도 찾아내지 못했다고 리턴