from config import db

class CustomerInfo(db.Model):
    __tablename__='customer_info'
    c_id=db.Column(db.Integer,primary_key=True)
    c_name=db.Column(db.String(200),nullable=False)
    phno=db.Column(db.String(200),nullable=False,unique=True)
    order_cid=db.relationship('Order',backref='customer_info')    