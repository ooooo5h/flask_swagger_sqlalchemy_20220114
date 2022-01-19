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

        return{
            'code' : 200,
            'message' : '비밀번호를 이메일로 전송했습니다.(임시)'
        }