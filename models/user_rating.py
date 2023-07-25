from config import db

class UserRating(db.Model):
    __tablename__='user_rating'
    o_id=db.Column(db.Integer,db.ForeignKey('order.o_id'),primary_key=True)
    rating=db.Column(db.Integer,nullable=False)