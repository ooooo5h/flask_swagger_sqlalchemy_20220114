from server import db

class LectureUser(db.Model):
    
    __tablename__ = 'lecture_user'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    
    # 굳이 dict로 변경하는 함수는 제작하지 않겠음