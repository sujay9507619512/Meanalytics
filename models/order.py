from config import db

class Order(db.Model):
    __tablename__='order'
    o_id=db.Column(db.Integer,primary_key=True)
    quantity=db.Column(db.Integer,nullable=False)
    f_id=db.Column(db.Integer,db.ForeignKey('food_items.f_id'))
    cost=db.Column(db.Integer,nullable=False)
    date=db.Column(db.String(150),nullable=False)
    c_id=db.Column(db.Integer,db.ForeignKey('customer_info.c_id'))
    delivery_status=db.Column(db.Boolean,nullable=False)
    user_rating_oid=db.relationship('UserRating',backref='order')