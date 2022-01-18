import boto3
import time
import os
import hashlib

from flask import current_app
from flask_restful import Resource, reqparse
from flask_restful_swagger_2 import swagger
from werkzeug.datastructures import FileStorage

from server import db
from server.model import Feeds, Users, FeedImages

post_parser = reqparse.RequestParser()
post_parser.add_argument('user_id', type=int, required=True, location='form')
post_parser.add_argument('lecture_id', type=int, required=True, location='form')
post_parser.add_argument('content', type=str, required=True, location='form')

post_parser.add_argument('feed_images', type=FileStorage, required=False, location='files', action='append')

class Feed(Resource):

    @swagger.doc({
        'tags' : ['feed'],  
        'description' : '게시글 등록하기',
        'parameters' : [
            {
                'name': 'X-Http-Token',
                'description': '어느 사용자인지를 토큰으로',
                'in': 'header',
                'type': 'string',
                'required': True
            },
            {
                'name': 'lecture_id',
                'description': '어느 강의에 대해 작성했나?',
                'in': 'formData',
                'type': 'integer',
                'required': True
            },
            {
                'name': 'content',
                'description': '게시글 내용',
                'in': 'formData',
                'type': 'string',
                'required': True
            },
            {
                'name': 'feed_images',
                'description': '게시글에 첨부할 사진',
                'in': 'formData',
                'type': 'file',
                'required': False
            },
        ],
        'responses' : {            
            '200' : {
                'description' : '게시글 등록 성공!',
            },
            '400' : {
                'description' : '게시글 등록 실패!'
            }
        }
    })    
    def post(self):
        """게시글 등록"""        
        
        args = post_parser.parse_args()
        
        new_feed = Feeds()
        new_feed.user_id = args['user_id']
        new_feed.lecture_id = args['lecture_id']
        new_feed.content = args['content']
        
        db.session.add(new_feed)
        db.session.commit()     
        
        # commit시점 이후에는, DB에 등록이 완료 => new_feed의 id/created_at등의 자동 등록 데이터도 모두 설정 완료
        
        # 사진 목록을 등록하는 행위는 반드시 commit()으로 id값이 확인 가능하게 된 이후에 작업해야한다
        
        # 사진 자체가 첨부되지 않았을 경우도 있으니까, 확인해보고 올리자
        
        if args['feed_images']:   # 사진이 파라미터에 첨부되어있나요?
            
            # 1 : 사용자가 누구인가? 
            upload_user = Users.query.filter(Users.id == args['user_id']).first()
            
            # 2 : AWS 접속 도구 셋팅
            aws_s3 = boto3.resource('s3',\
                aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],\
                aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'])          
            
            for image in args['feed_images']:
                # 첨부된 사진들을 AWS S3에 올려주기
                
                # 1 : 파일 이름은 중복을 피해서 재가공
                # 사용자id 암호화하고, 현재 시간을 숫자로 표현해서 써먹기
                
                _, file_extensions = os.path.splitext(image.filename)
                encrypted_user_email = hashlib.md5(upload_user.email.encode('utf-8')).hexdigest()
                now_number = round(time.time() * 10000)
                
                s3_file_name = f"images/feed_images/MySNS_{encrypted_user_email}_{now_number}{file_extensions}"
                
                # 2 : AWS S3에 파일 업로드
                image_body = image.stream.read()  
                
                aws_s3\
                    .Bucket(current_app.config['AWS_S3_BUCKET_NAME'])\
                    .put_object(Key=s3_file_name, Body=image_body)
                
                aws_s3\
                    .ObjectAcl(current_app.config['AWS_S3_BUCKET_NAME'], s3_file_name)\
                    .put(ACL='public-read')
                
                # feed_images라는 테이블에 이 게시글의 사진으로 S3에 올라간 사진 주소를 등록해줘야함
                feed_img = FeedImages()
                feed_img.feed_id = new_feed.id
                feed_img.img_url = s3_file_name
                
                db.session.add(feed_img)
            
            # DB에 추가할 객체는 for문을 통해 모두 등록해두고, commit은 for문 외부에서 한번에 몰아서 날리자
            db.session.commit()  # 1번 실행마다 DB서버에 1회 접근 => for내부에 작성하면 반복적으로 DB서버에 접근한다는 뜻
        
        
        return {
            'code' : 200,
            'message' : '게시글 등록 성공',
            'data' : {
                'feed' : new_feed.get_data_object()
            }
        }

    @swagger.doc({
        'tags' : ['feed'],  
        'description' : '게시글 목록 조회하기',
        'parameters' : [
           
        ],
        'responses' : {            
            '200' : {
                'description' : '게시글 목록 조회 성공!',
            },
            '400' : {
                'description' : '게시글 조회 실패!'
            }
        }
    })          
    def get(self):
        """모든 게시글을 최신순으로 조회"""
        
        # 모든 게시글을 가져올 때, 생성일시의 역순으로 가져와야지 최신순이 됨 => SQL : ORDER BY + DESC => ORM으로는 어떻게 표현할까?
        feed_data_arr = Feeds.query.order_by(Feeds.created_at.desc()).all()
        
        feeds = [ row.get_data_object() for row in feed_data_arr]
        
        
        return {
            'code' : 200,
            'message' : '모든 게시글 조회',
            'data' : {
                'feeds' : feeds
            }
        }