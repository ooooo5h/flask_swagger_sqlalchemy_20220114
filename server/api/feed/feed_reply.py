from flask import current_app, g
from flask_restful import Resource, reqparse
from flask_restful_swagger_2 import swagger

from server import db
from server.model import FeedReplies
from server.api.utils import token_required

post_parser = reqparse.RequestParser()
post_parser.add_argument('content', type=str, required=True, location='form')


put_parser =reqparse.RequestParser()
put_parser.add_argument('feed_reply_id', type=int, required=True, location='form')
put_parser.add_argument('content', type=str, required=True, location='form')

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('feed_reply_id', type=int, required=True, location='args')


class FeedReply(Resource):

    @swagger.doc({
        'tags' : ['feed/reply'],  
        'description' : '게시글에 댓글 작성하기',
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
                'in': 'path',
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
                'description' : '댓글 등록 성공!',
            },
            '400' : {
                'description' : '댓글 등록 실패!'
            }
        }
    })    
    @token_required
    def post(self, feed_id):
        """댓글 등록"""        
        
        args = post_parser.parse_args()
        
        user = g.user # 전역변수에 저장된 토큰에서 뽑아낸 사용자를 변수에 저장
        
        # FeedReplies 객체 생성 -> 데이터 기입 -> db에 전달
        new_reply = FeedReplies()
        new_reply.feed_id = feed_id
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
        
        
    @swagger.doc({
        'tags' : ['feed/reply'],
        'description' : '달아둔 댓글 수정',
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
                'description': '몇번 게시글에 포함된 댓글을 수정할건지?',
                'in': 'path',
                'type': 'integer',
                'required': True
            },
            {
                'name': 'feed_reply_id',
                'description': '몇번 댓글을 수정할건지?',
                'in': 'formData',
                'type': 'integer',
                'required': True
            },
            {
                'name':'content',
                'description':'수정해줄 내용',
                'in': 'formData',
                'type': 'string',
                'required': True,
            },
        ],
        'responses':{
            '200':{
                'description': '수정 성공'
            }
        },
    })
    @token_required
    def put(self, feed_id):
        """ 댓글 수정 """
        args = put_parser.parse_args()
        user = g.user
        
        reply = FeedReplies.query.filter(FeedReplies.id == args['feed_reply_id']).first()
        
        if reply.user_id != user.id:
            return {
                'code' : 400,
                'message' : '본인이 쓴 댓글만 수정가능합니다.'
            }, 400
            
        reply.content = args['content']
        
        db.session.add(reply)
        db.session.commit()
        
        
        return {
            'code':200,
            'message': '댓글 수정 성공'
        } 
        
    @swagger.doc({
        'tags' : ['feed/reply'],
        'description' : '달아둔 댓글 삭제',
        'parameters' : [
            {
                'name': 'X-Http-Token',
                'description': '사용자 토큰',
                'in': 'header',
                'type': 'string',
                'required': True
            },
            {
                'name': 'feed_id',
                'description': '몇번 게시글에 포함된 댓글을 삭제할거야?',
                'in': 'path',
                'type': 'integer',
                'required': True
            },
            {
                'name': 'feed_reply_id',
                'description': '몇번 댓글을 삭제할거야?',
                'in': 'query',
                'type': 'integer',
                'required': True
            },
        ],
        'responses':{
            '200':{
                'description': '삭제 성공'
            }
        },
    })
    @token_required
    def delete(self, feed_id):
        """ 댓글 삭제 """
        args = delete_parser.parse_args()
        user = g.user
        
        reply = FeedReplies.query.filter(FeedReplies.id == args['feed_reply_id']).first()
        
        if reply.user_id != user.id:
            return {
                'code' : 400,
                'message' : '본인이 쓴 댓글만 삭제 가능.'
            }, 400
                    
        db.session.delete(reply)
        db.session.commit()
        
        
        return {
            'code':200,
            'message': '댓글 삭제 성공'
        } 


    @swagger.doc({
        'tags': ['feed/reply'],
        'description': '특정 게시글에 달린 댓글 목록 보기',
        'parameters': [
            {
                'name':'feed_id',
                'description':'몇번 게시글에 포함된 댓글목록을 조회할지?',
                'in': 'path',
                'type': 'integer',
                'required': True,
            },
        ],
        'responses':{
            '200':{
                'description': '댓글 목록 조회 성공'
            }
        },
    })
    def get(self, feed_id):
        """ 게시글의 댓글 목록 조회 """

        reply_data_list = FeedReplies.query\
            .filter(FeedReplies.feed_id == feed_id)\
            .all()

        replies = [ reply.get_data_object() for reply in reply_data_list ]

        return {
            'code':200,
            'message': '댓글 목록 조회 성공',
            'data': {
                'replies': replies
            }
        } 
