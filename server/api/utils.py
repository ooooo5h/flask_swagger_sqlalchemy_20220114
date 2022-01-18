# 토큰을 발급하고, 발급된 토큰이 들어오면 사용자가 누구인지 분석하는 등의 기능을 담당하는 파일
# JWT에 관한 기능을 모아두는 모듈로 만들거임

import jwt
from flask import current_app

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
        ).decode('utf-8')