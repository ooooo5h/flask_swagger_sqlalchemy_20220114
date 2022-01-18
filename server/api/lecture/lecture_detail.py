from flask_restful import Resource
from server.model import Lectures

class LectureDetail(Resource):
    
    def get(self, lecture_id):
        
        lecture_row = Lectures.query.filter(Lectures.id == lecture_id).first()
        
        if lecture_row is None:
            return {
                'code' : 400,
                'message' : '해당 강의는 존재하지 않습니다.'
            }, 400
        
        return{
            'code' : 200,
            'message' : '강의 상세 조회',
            'data' : {
                'lecture' : lecture_row.get_data_object(need_teacher_info=True)  # 특정 강의 상세보기할때는 선생님 정보도 보여주자
            }
        }