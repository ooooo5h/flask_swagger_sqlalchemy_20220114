import boto3
import time
import os
import hashlib # str -> 암호화된 문구로 변경

from flask import current_app
from flask_restful_swagger_2 import swagger
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage  # 파라미터로 파일을 받을 때 필요한 클래스

put_parser = reqparse.RequestParser()

# 파일을 받는 파라미터는 FileStorage, files에서, 추가행동 : append가 필요
put_parser.add_argument('profile_image', type=FileStorage, required=True, location='files', action='append')
put_parser.add_argument('user_id', type=int, required=True, location='form')

class UserProfileImage(Resource):

    @swagger.doc({
        'tags' : ['user'], 
        'description' : '사용자 프로필 사진 등록',
        'parameters' : [
            {
                'name': 'user_id',
                'description': '누구의 프사를 등록할거야?',
                'in': 'formData',
                'type': 'integer',
                'required': True,
            },
            {
                'name': 'profile_image',
                'description': '실제로 첨부할 사진',
                'in': 'formData',
                'type': 'file',
                'required': True,
            }
        ],
        'responses' : {
            '200' : {
                'description' : '등록 성공!',
            },
            '400' : {
                'description' : '등록 실패!'
            }
        }
    })    
    def put(self):
        """사용자 프로필 사진 등록"""       
        
        args = put_parser.parse_args()
        
        # aws - s3에 어떤 키와 비밀키를 들고 갈지 셋팅해야함
        # 키값들은 환경설정(config)에 저장해둔 값을 불러와서 사용
        aws_s3 = boto3.resource('s3',\
            aws_access_key_id= current_app.config['AWS_ACCESS_KEY_ID'],\
            aws_secret_access_key= current_app.config['AWS_SECRET_ACCESS_KEY'] )
        
        # 파일의 경우 보통 여러장 첨부가 가능하다
        # args['profile_image'] 는 list로 구성되어있는 경우가 많다(여러장이니까)
        
        for file in args['profile_image']:
            # file : 파일이름 / 실제 이미지들의 본문이 분리된 형태로 만들어져 있음
            
            # 파일 이름 저장  => S3 버킷에 저장될 경로 생성에 활용할꺼임 == > 중복 발생 소지가 있다
            # 파일 이름은 재가공(누가_언제)해서 확장자(.jpg)만 가져다 사용하면 해결됨
            # 예시. PC카카오톡 파일 전송해서 다운로드하면 보낸 파일이름을 무시하고, Kakao_?????.jpg 등으로 받아짐
            
            # 1 : 파일이름을 재가공
            
            user_email = 'test1@test.com' # 임시 이메일
            now = round(time.time() * 10000) # 현재 시간을 적당한 숫자값으로 표현하기 위해서. 중복을 피하기 위한 요소로 활용만 하면 되니까 대충~
            
            new_file_name = f"MySNS_{hashlib.md5(user_email.encode('utf-8')).hexdigest()}_{now}"
            
            # 2 : 확장자를 추출
            # 파일이름과 확장자 중에서 확장자만 변수에 담기 위해서 이름은 _,로 처리
            _, file_extension = os.path.splitext(file.filename)  # 원래 올라온 파일 명을 파일이름, 확장자로 분리
            
            new_file_name = f"{new_file_name}{file_extension}"
            
            # 최종 경로에는 1 + 2 + S3의 폴더            
            s3_file_path = f'images/profile_imgs/{new_file_name}'   # 올라갈 경로가 만들어짐
            
            # 파일 본문도 따로 불러내서 저장해보자 => 실제로 S3경로에 업로드하는 데 활용할꺼임
            file_body = file.stream.read()   # 올려줄 파일이 만들어짐
            
            # 어떤 버킷에 올려줄건지 설정 => 파일 업로드(put_object())까지 한 큐에 하도록 처리
            aws_s3.Bucket(current_app.config['AWS_S3_BUCKET_NAME']).put_object(Key=s3_file_path, Body=file_body)
            
            # 이 파일을 누구나 볼 수 있게 public으로 허용하는 작업 필요함 , s3_file_path(파일이름을 찾아서)
            aws_s3.ObjectAcl(current_app.config['AWS_S3_BUCKET_NAME'], s3_file_path).put(ACL='public-read')
        
        return {
            '임시' : '사용자가 프사를 등록하는 기능'
        }