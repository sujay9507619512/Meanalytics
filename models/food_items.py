from config import db

class FoodItems(db.Model):
    __tablename__='food_items'
    f_id=db.Column(db.Integer,primary_key=True)
    price=db.Column(db.Integer,nullable=False)
    f_name=db.Column(db.String(200),nullable=False)
    ordercount=db.Column(db.Integer,nullable=False)
    rating=db.Column(db.Float,nullable=False)
    ratingcount=db.Column(db.Integer,nullable=False)
    availability=db.Column(db.Boolean,nullable=False)
    order_fid=db.relationship('Order',backref='food_items')
