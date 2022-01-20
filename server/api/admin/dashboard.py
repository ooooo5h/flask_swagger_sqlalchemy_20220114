from flask_restful import Resource
from server.model import Users, LectureUser, Lectures

class AdminDashboard(Resource):
    
    def get(self):
        
        # 탈퇴안한 회원 수는 몇 명? => users 테이블에서 SELECT문
        
        # first()는 한 줄/ all()은 목록 / count()는 검색된 갯수
        users_count = Users.query.filter(Users.email != 'retired').count()
        
        
        # 연습 - 자바 강의 수강생의 정보 => JOIN을 썼었는데, ORM으로 어떻게 JOIN을 구현하나 
        
        java_user_list = Users.query\
            .filter(LectureUser.user_id == Users.id)\
            .filter(LectureUser.lecture_id == Lectures.id)\
            .filter(Lectures.title == '자바')\
            .all()
            
        print(java_user_list)
        
        
        
        return {
            'code' : 200,
            'message' : '임시 응답 : 관리자용 각종 통계 api',
            'data' : {
                'live_user_count' : users_count
            }
        }
        
    