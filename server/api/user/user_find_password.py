import email
from venv import create
import requests

from flask import current_app, g
from flask_restful_swagger_2 import swagger
from flask_restful import Resource, reqparse

from server import db
from server.model import Users
from server.api.utils import token_required

get_parser = reqparse.RequestParser()
get_parser.add_argument('email',type=str, required=True, location='args')
get_parser.add_argument('name',type=str, required=True, location='args')
get_parser.add_argument('phone',type=str, required=True, location='args')

class UserPasswordFind(Resource):

    @swagger.doc({
        'tags' : ['user'], 
        'description' : '비밀번호 찾기',
        'parameters' : [
            {
                'name': 'email',
                'description': '비밀번호를 찾을 이메일',
                'in': 'query',
                'type': 'string',
                'required': True,
            },
            {
                'name': 'name',
                'description': '가입했던 이름',
                'in': 'query',
                'type': 'string',
                'required': True,
            },
            {
                'name': 'phone',
                'description': '가입했던 연락처',
                'in': 'query',
                'type': 'string',
                'required': True,
            },
        ],
        'responses' : {
            '200' : {
                'description' : '비밀번호가 이메일로 전송됨',
            },
            '400' : {
                'description' : '이름 or 연락처 둘 중 하나 땡'
            }
        }
    })    
    def get(self):
        """비밀번호 찾기 (이메일로 전송)"""       
        
        args = get_parser.parse_args()
        
        user = Users.query\
            .filter(Users.email == args['email'])\
            .first()
            
        if user is None:
            return {
                'code' : 400,
                'message' : '해당 계정의 사용자는 없습니다.'
            }, 400
         
         
        # 이메일로 사용자 검색 성공
        # 연락처도 비교 => '-'를 모두 삭제하고 나서 비교하기 
        # 이름도 비교    
        input_phone = args['phone'].replace('-', '')
        user_phone = user.phone.replace('-', '')
        
        if (input_phone != user_phone) or (args['name'] != user.name):
            return{
                'code' : 400,
                'message' : '개인정보가 맞지 않습니다.'
            }, 400
            
        # 메일에 뭐라고 보내줄건지 내용을 작성해보기
        # 실제 비밀번호를 보내주면 안됨!! 그 뜻은 실제 비밀번호를 사이트 DB에 저장해뒀다는 이야기
        # 임시 비밀번호를 랜덤으로 설정해서 새 비밀번호로 update하고 메일로 발송해주자
        send_content = f"""
        안녕하세요. MySNS입니다.
        회원님의 비밀번호는 {user.password}입니다.
        Don't forget
        """    
        
        print(send_content)    
            
        # 메일 전송 경우에는 API 사이트가 mailgun.com이라는 사이트를 활용함
        # => 도메인 주소를 구매 후 저 사이트에 세팅까지 마친 후에 활용이 가능함
        
        # 어느 사이트(주소) / 메쏘드 / 파라미터 세가지를 세팅해서 requests 모듈 활용하자
        mailgun_url = 'https://api.mailgun.net/v3/mg.gudoc.in/messages'
        email_data = {
            'from' : 'system@gudoc.in',  # no-reply@웹주소.com
            'to' : user.email,              # 비밀번호 찾기를 하려는 사용자의 이메일주소
            'subject' : '[MySNS 비밀번호 안내] 비밀번호 찾기 알림 메일입니다.',
            'text' : send_content,
        }    
        
        response = requests.post(
            url = mailgun_url,
            data = email_data,
            auth= ('api', current_app.config['MAILGUN_API_KEY'])
        )

        respJson = response.json()
        print('메일건 응답 : ', respJson)
        
        return{
            'code' : 200,
            'message' : '비밀번호를 이메일로 전송했습니다.(임시)'
        }