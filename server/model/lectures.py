from server import db

class Lectures(db.Model):
    
    __tablename__ = 'lectures'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    campus = db.Column(db.String(10), nullable=False)
    fee = db.Column(db.Integer, nullable=False, default=0)   # DB(HeidiSQL)에 컬럼 추가했으면 여기서도 추가해야함
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    teacher = db.relationship('Users')  # 강의의 입장에서, 강사를 찾아가자는 것도 가능하다는 의미에서 남겨둠(정석은 아님)
    # 정석 : 부모가 자식을 여러개 보유하고, 부모를 찾아오게끔 하는 것
    # 편의 : 자식의 입장에서 부모를 찾아가자
    feeds = db.relationship('Feeds', backref='lecture')
    
    def get_data_object(self, need_teacher_info=False):
        data = {
            'id' : self.id,
            'title' : self.title,
            'campus' : self.campus,
            'fee' : self.fee,
            'teacher_id' : self.teacher_id,    
        }
        
        if need_teacher_info:
            data['teacher'] =  self.teacher.get_data_object() if self.teacher else None
        
        return data