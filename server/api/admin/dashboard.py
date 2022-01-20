from flask_restful import Resource
from server.model import Users, LectureUser, Lectures
from server import db

import datetime

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
        
        #### 이해못했음
        # 남성 회원수와 여성 회원수 => 조건추가 : 탈퇴하지 않은 사람들만!
        gender_by_user_count_list = db.session.query(Users.is_male, db.func.count(Users.id))\
            .filter(Users.retired_at == None)\
            .group_by(Users.is_male)\
            .all()
            
        # 성별에 따른 사용자 수
        gender_user_counts = [{'is_male' : row[0], 'user_count' : int(row[1])} for row in gender_by_user_count_list]
        
        
        # 최근 10일(2022-01-10 이후)간의 날짜별 매출 총합
        # 지금으로부터 10일전은 몇일인가?를 구해서 쿼리에 반영하자
        now = datetime.datetime.utcnow()  # DB가 표준 시간대를 사용하기 때문에, 계산도 표준시간대 기준으로 하자
        
        diff_days = datetime.timedelta(days= -10)  # 10일 이전으로 계산해줄 변수
        
        ten_days_ago = now + diff_days  # 10일 전의 날짜를 구했음  >>######### date를 안해줘도 되나..?? 
        
        print(ten_days_ago) # 2022-01-10 03:06:08.504041 뒤에 초까지 나오는데..
                   
        amount_by_date_list = db.session.query(db.func.date(LectureUser.created_at), db.func.sum(Lectures.fee))\
            .filter(Lectures.id == LectureUser.lecture_id)\
            .filter(LectureUser.created_at > ten_days_ago)\
            .group_by(db.func.date(LectureUser.created_at))\
            .all()
            
        date_amounts = []
        
        # 매출이 없는 날은, DB쿼리 결과도 아예 없다 => 목록이 아예 등록이 안됨
        # 날짜는 무조건 10개를 가져오고, 매출 없는 날은 0원으로 처리해보자
        
        # 10일 전 ~ 오늘까지를 for문으로 돌아보기
        for i in range(0, 11):
            
            # 시간/분/초까지 날짜에 들어가니까, 2022-01-11 양식으로 변경해서 넣어주겠다
 
            amount_dict = {
                'date' : ten_days_ago.strftime('%Y-%m-%d'),
                'amount' : 0,
            }
            date_amounts.append(amount_dict)

            # 해당 날짜에서 하루 지난 날로 변경
            ten_days_ago += datetime.timedelta(days=1)
        
        # for row in amount_by_date_list:
        #     amount_dict = {
        #         'date' : str(row[0]),
        #         'amount' : int(row[1]),
        #     }
        #     date_amounts.append(amount_dict)
        
        return {
            'code' : 200,
            'message' : '임시 응답 : 관리자용 각종 통계 api',
            'data' : {
                'live_user_count' : users_count,
                'group_by_lecture_fee_amount' : amount_list,
                'gender_by_user_counts' : gender_user_counts,  
                'date_amounts' : date_amounts,
            }
        }
        
    