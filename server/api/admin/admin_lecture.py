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

patch_parser = reqparse.RequestParser()
patch_parser.add_argument('field', type=str, required=True, location='form')
patch_parser.add_argument('value', type=str, required=True, location='form')
patch_parser.add_argument('lecture_id', type=int, required=True, location='form')

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
    def post(self):
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
        
    @swagger.doc({
        'tags' : ['admin'],
        'description' : '관리자 - 강의 수정',
        'parameters' : [
            {
                'name' : 'X-Http-Token',
                'description' : '사용자 인증용 헤더 - 관리자만 OK',
                'in' : 'header',
                'type' : 'string',
                'required' : True,
            },
            {
                'name' : 'lecture_id',
                'description' : '몇 번 강의를 수정하겠습니까?',
                'in' : 'formData',
                'type' : 'integer',
                'required' : True,
            },        
            {
                'name' : 'field',
                'description' : '수정할 항목 - title / campus / fee / teacher_id 중 택일',
                'in' : 'formData',
                'type' : 'string',
                'enum' : ['title', 'campus', 'fee', 'teacher_id'],
                'required' : True,
            },        
            {
                'name' : 'value',
                'description' : '수정할 값',
                'in' : 'formData',
                'type' : 'string',   # int값이 필요한 fee와 teacher_id는 형변환으로 처리하자
                'required' : True,
            }, 
        ],
        'responses' : {
            '200' : {
                'description' : '관리자 강의 정보 수정 성공'
            }
        }
    })
    @token_required
    @admin_required
    def patch(self):
        """관리자 - 강의 수정"""
        
        args = patch_parser.parse_args() 
        
        # 실존하는 강의를 수정하는게 맞나요?
        lecture = Lectures.query.filter(Lectures.id == args['lecture_id']).first()
        
        if lecture == None:
            return {
                'code' : 400,
                'message' : '그런 강의 없수다',
            }, 400
        
        if args['field'] == 'title':
            lecture.title = args['value']
        elif args['field'] == 'campus':
            lecture.campus = args['value']
        elif args['field'] == 'fee':
            lecture.fee = int(args['value'])
        elif args['field'] == 'teacher_id':
            lecture.teacher_id = int(args['value'])               
        else : 
            return {
                'code' : 400,
                'message' : 'field에 제대로 된 값을 입력하세요.'
            }, 400
            
        db.session.add(lecture)
        db.session.commit()    
            
            
        return {
            'code' : 200,
            'message' : '관리자 강의 수정 성공',
        }