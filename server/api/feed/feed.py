from flask_restful import Resource

class Feed(Resource):
    
    def post(self):
        return {
            '임시' : '게시글 등록'
        }