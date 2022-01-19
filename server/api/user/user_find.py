from flask import current_app, g
from flask_restful_swagger_2 import swagger
from flask_restful import Resource, reqparse

from server import db
from server.model import Users
from server.api.utils import token_required

get_parser = reqparse.RequestParser()
get_parser.add_argument('name',type=str, required=True, location='args')
get_parser.add_argument('phone',type=str, required=True, location='args')

class UserFind(Resource):

    @swagger.doc({
        'tags' : ['user'], 
        'description' : '아이디 찾기',
        'parameters' : [
            {
                'name': 'name',
                'description': '가입했던 이름 확인, 너 누구야!',
                'in': 'query',
                'type': 'string',
                'required': True,
            },
            {
                'name': 'phone',
                'description': '가입했던 연락처 확인, 너 핸드폰 번호 뭐야! 둘 다 맞아야지만 문자로 전송 가능',
                'in': 'query',
                'type': 'string',
                'required': True,
            },
        ],
        'responses' : {
            '200' : {
                'description' : '이메일이 문자로 전송됨',
            },
            '400' : {
                'description' : '이름 or 연락처 둘 중 하나 땡'
            }
        }
    })    
    def get(self):
        """이메일 찾기 (문자 전송)"""       
        
        args = get_parser.parse_args()
           
        return {
            'code' : 200,
            'message' : '이메일 찾기 - 문자 전송 완료',
        }