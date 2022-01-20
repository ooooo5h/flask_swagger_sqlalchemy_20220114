from flask_restful import Resource
from server.model import Users

class AdminDashboard(Resource):
    
    def get(self):
        
        # 탈퇴안한 회원 수는 몇 명? => users 테이블에서 SELECT문
        users = Users.query.filter(Users.email != 'retired').all()
        
        return {
            'code' : 200,
            'message' : '임시 응답 : 관리자용 각종 통계 api',
            'data' : {
                'live_user_count' : len(users)
            }
        }