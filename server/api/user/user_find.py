import requests

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
        
        user = Users.query\
            .filter(Users.name == args['name'])\
            .first()
            
        if user is None:
            return {
                'code' : 400,
                'message' : '해당 이름의 사용자는 없는데?!?'
            }, 400
         
         
        # 맞는 이름자 검색 성공
        # 연락처도 비교 => '-'를 모두 삭제하고 나서 비교하기     
        input_phone = args['phone'].replace('-', '')
        user_phone = user.phone.replace('-', '')
        
        if input_phone != user_phone:
            return{
                'code' : 400,
                'message' : '이름은 맞지만, 연락처가 다릅니다.'
            }, 400
         
        # 이름과 연락처가 모두 맞는 사람을 찾았다면, 알리고 사이트의 API에 문자 전송하는 Request를 전송 => requests 모듈 활용 
        
        # 1 : 주소가 어디야?  apis.aligo.in/send/ 등의 주소
        
        # 2 : 어떤 메쏘드야? POST   
        
        # 3 : 파라미터 => 명세서 참조하기
        
        sms_url = 'https://apis.aligo.in/send/'
        
        # dict에 들고갈 파라미터에 담을 값들을 미리 세팅해두자
        send_data = {
            'key' : current_app.config['ALIGO_API_KEY'],
            'user_id' : 'cho881020',
            'sender' : '010-5112-3237',
            'receiver' : user.phone,
            'msg' : f"-MySNS 계정안내-\n가입하신 계정은 [{user.email}]입니다.",
        }
        
        # request의 요청에 대한 결과를 변수에 담자
        
        response = requests.post(url=sms_url, data=send_data)
        
        # 응답의 본문이 JSON으로 올 예정 => 본문을 json형태로 가공해서 받자
        respJson = response.json()

        # 결과 코드가 1인게 성공 => 우리 서버도 200번으로 리턴하자
        # 그 외의 값이 오면, 알리고에서 문제가 생긴건데, 그 내용을 그대로 500으로 리턴해주자
        # 400은 Bad Request (요청을 보낸 쪽에서 문제가 생겼음)
        # 403은 권한 문제
        # 404는 해당 주소의 기능이 없음
        # 500은 서버 내부의 문제 (Interer Server Error)
        
        if int(respJson['result_code']) != 1:
            # 정상 전송 실패
            return{
                'code' : 500,
                'message' : respJson['message']  # 알리고에서 왜 실패했는지는 알 수 없다.. 그냥 알리고에서 받은 문구 그대로 리턴
            }, 500
        else:
            # 정상 전송 성공
            return {
                'code' : 200,
                'message' : '이메일 찾기 - 문자 전송 완료',
            }