from email.policy import default
from server import db

class Feeds(db.Model):
    __tablename__ = 'feeds'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    lecture_id = db.Column(db.Integer)                  # null이면, 특정 강의에 대한 글이 아님
    content = db.Column(db.TEXT, nullable=False)        # TEXT 컬럼 대응
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    
    def get_data_object(self):
        data = {
            'id' : self.id,
            'user_id' : self.user_id,
            'lecture_id' : self.lecture_id,
            'content' : self.content,
            'created_at' : str(self.created_at),            
        }
        
        return data