from server import db

class Lectures(db.Model):
    
    __tablename__ = 'lectures'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    campus = db.Column(db.String(10), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def get_data_object(self):
        data = {
            'id' : self.id,
            'title' : self.title,
            'campus' : self.campus,
            'teacher_id' : self.teacher_id,
        }
        
        return data