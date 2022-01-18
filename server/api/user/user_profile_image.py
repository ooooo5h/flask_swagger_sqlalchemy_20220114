from flask_restful import Resource

class UserProfileImage(Resource):
    
    def put(self):
        return {
            '임시' : '사용자가 프사를 등록하는 기능'
        }