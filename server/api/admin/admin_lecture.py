from flask_restful import Resource, reqparse
from flask_restful_swagger_2 import swagger
from flask import g
from server.model import Lectures
from server import db

from server.api.utils import token_required, admin_required

import datetime

post_parser = reqparse.RequestParser()
post_parser.add_argument('title', type=str, required=True, location='form')
post_parser.add_argument('campus', type=str, required=True, location='form')
post_parser.add_argument('fee', type=int, required=True, location='form')

class AdminLecture(Resource):
    
    @swagger.doc({
        'tags' : ['admin'],
        'description' : '관리자 - 강의 개설',
        'parameters' : [
            {
                'name' : 'X-Http-Token',
                'description' : '사용자 인증용 헤더 - 관리자만 OK',
                'in' : 'header',
                'type' : 'string',
                'required' : True,
            },
            {
                'name' : 'title',
                'description' : '강의 제목',
                'in' : 'formData',
                'type' : 'string',
                'required' : True,
            },        
            {
                'name' : 'campus',
                'description' : '강의가 열리는 캠퍼스 이름',
                'in' : 'formData',
                'type' : 'string',
                'required' : True,
            },     
            {
                'name' : 'fee',
                'description' : '수강료',
                'in' : 'formData',
                'type' : 'integer',
                'required' : True,
            },     
        ],
        'responses' : {
            '200' : {
                'description' : '관리자 강의 등록 성공'
            }
        }
    })
    @token_required
    @admin_required
    def get(self):
        """관리자 - 강의 개설"""
        
        args = post_parser.parse_args()
        
        lecture = Lectures()
        lecture.title = args['title']
        lecture.campus = args['campus']
        lecture.fee = args['fee']
        
        db.session.add(lecture)
        db.session.commit()        
        
        return {
            'code' : 200,
            'message' : '관리자 강의 개설 성공',
        }
        
    