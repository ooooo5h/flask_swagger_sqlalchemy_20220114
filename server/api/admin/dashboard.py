from flask_restful import Resource
from server.model import Users, LectureUser, Lectures
from server import db

class AdminDashboard(Resource):
    
    def get(self):
        
        # 탈퇴안한 회원 수는 몇 명? => users 테이블에서 SELECT문
        
        # first()는 한 줄/ all()은 목록 / count()는 검색된 갯수
        users_count = Users.query.filter(Users.email != 'retired').count()
        
        
        # 연습 - 자바 강의의 매출 총액 => JOIN을 썼었는데, ORM으로 어떻게 JOIN을 구현하나  + 집계함수
        # query( SELECT문의 컬럼 선택처럼 여러 항목이 가능)
        # db.func.집계함수(컬럼) = 실제로 SELECT문을 이용한 집계함수를 동작시키는 방법
        
        # filter 나열 => JOIN / ON 한번에 명시
        # filter 나열2 => JOIN이 끝나고 나면, 마지막 filter에 WHERE처럼 실제 필터조건을 작성해주면 됨
        
        # group_by => 실제로 어떤 값을 기준으로 그룹지을건지 모델을 이용해서 써주면 짜잔~
        group_by_lecture_fee_amount = db.session.query( Lectures.title, db.func.sum(Lectures.fee) )\
            .filter(Lectures.id == LectureUser.lecture_id)\
            .filter(LectureUser.user_id == Users.id)\
            .group_by(Lectures.id)\
            .all() 
            
        # print(group_by_lecture_fee_amount)   => JSON응답으로 내려갈 수 없어서, 추가 가공처리가 필요함
        amount_list = [{'lecture_title' : row[0], 'amount' : int(row[1])} for row in group_by_lecture_fee_amount ]  
        
        
        # 모든 남성 유저 목록을 출력해보기
        male_users = Users.query.filter(Users.is_male == True).all()
        print(male_users)
        
        return {
            'code' : 200,
            'message' : '임시 응답 : 관리자용 각종 통계 api',
            'data' : {
                'live_user_count' : users_count,
                'group_by_lecture_fee_amount' : amount_list,
            }
        }
        
    