from ast import arg
from flask import current_app, g
from flask_restful import Resource, reqparse
from flask_restful_swagger_2 import swagger

from server import db
from server.model import FeedReplies
from server.api.utils import token_required

post_parser = reqparse.RequestParser()
post_parser.add_argument('feed_id', type=int, required=True, location='form')
post_parser.add_argument('content', type=str, required=True, location='form')

put_parser = reqparse.RequestParser()
put_parser.add_argument('feed_reply_id', type=int, required=True, location='form')
put_parser.add_argument('content', type=str, required=True, location='form')


class FeedReply(Resource):

    @swagger.doc({
        'tags' : ['feed/reply'],  
        'description' : '댓글 등록하기',
        'parameters' : [
            {
                'name': 'X-Http-Token',
                'description': '어느 사용자인지를 토큰으로',
                'in': 'header',
                'type': 'string',
                'required': True
            },
            {
                'name': 'feed_id',
                'description': '어느 피드에 남긴 댓글인지',
                'in': 'formData',
                'type': 'integer',
                'required': True
            },
            {
                'name': 'content',
                'description': '댓글 내용',
                'in': 'formData',
                'type': 'string',
                'required': True
            },
        ],
        'responses' : {            
            '200' : {
                'description' : '게시글에 댓글 작성 성공!',
            },
            '400' : {
                'description' : '댓글 작성 실패!'
            }
        }
    })    
    @token_required
    def post(self):
        """댓글 등록하기"""        
        
        args = post_parser.parse_args()
        
        user = g.user 
        
        # FeedReplies 객체 생성 -> 데이터 기입 -> db전달
        new_reply = FeedReplies()
        
        new_reply.feed_id = args['feed_id']
        new_reply.user_id = user.id
        new_reply.content = args['content']
        
        db.session.add(new_reply)
        db.session.commit()
        
        return {
            'code' : 200,
            'message' : '댓글 등록 성공',
            'data' : {
                'feed' : new_reply.get_data_object()
            }
        }

    
    # put 메쏘드 만들기 (타 클래스 참고 / 코드 재활용)
    # 기존에 만들어진 댓글의 id를 받아서 수정처리
    # 제약 사항 : 본인이 쓴 댓글만 실제로 수정할 수 있음. 타인이 쓴 댓글이라면 400으로 '본인이 쓴 댓글만 수정가능합니다.'
    @swagger.doc({
        'tags' : ['feed/reply'],  
        'description' : '달아둔 댓글 수정',
        'parameters' : [
            {
                'name': 'X-Http-Token',
                'description': '사용자 구별 토큰',
                'in': 'header',
                'type': 'string',
                'required': True,
            },
            {
                'name': 'feed_reply_id',
                'description': '몇번 댓글을 수정할건지',
                'in': 'formData',
                'type': 'integer',
                'required': True,
            },
            {
                'name': 'content',
                'description': '수정해줄 댓글 내용',
                'in': 'formData',
                'type': 'string',
                'required': True,
            },                                       
        ],
        'responses' : {
            '200' : {
                'description' : '댓글 수정 성공!',
            },
        }
    })  
    @token_required      
    def put(self):
        """댓글 수정"""
        
        return {
            'code' : 200,
            'message' : '댓글 수정 성공'
        }
        



        