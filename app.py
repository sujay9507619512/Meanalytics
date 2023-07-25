from flask import Flask,request,jsonify
from flask_cors import CORS
from config import db,secret_key
from os import path,getcwd,environ
from dotenv import load_dotenv
from datetime import date

from models.customer_info import CustomerInfo
from models.food_items import FoodItems
from models.order import Order
from models.user_rating import UserRating

load_dotenv(path.join(getcwd(),'.env'))

def create_app():
    app=Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI']=environ.get('DB_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
    app.config['SQLALCHEMY_ECHO']=False
    app.secret_key=secret_key

    db.init_app(app)
    print("DB Initialized Successfully")

    CORS(app)

    with app.app_context():
#------------------------------------------------------------------------------------------
        ############ ----------------- USER SIDE ENDPOINTS --------------------------------
#------------------------------------------------------------------------------------------ 
        @app.route("/signup", methods=['GET'])
        def signup():
            data = request.form.to_dict(flat=True)
            
            phno=data['phno']
            res=CustomerInfo.query.filter_by(phno=phno).first()
            
            if res==None:
                new_cus = CustomerInfo(
                    c_name=data['username'],
                    phno=data['phno']
                )
                db.session.add(new_cus)
                db.session.commit()
                res=CustomerInfo.query.filter_by(phno=phno).first()
                return jsonify(user_token=res.c_id)
            else:
                return jsonify(user_token=res.c_id)


#------------------------------------------------------------------------------- 


        @app.route("/show_menu",methods=['GET'])
        def show_menu():
            avail_foods=FoodItems.query.filter_by(availability=True).all()
            if avail_foods==None:
                return jsonify(msg="No item available")
            else:    
                items=[]
                for food in avail_foods:
                    items.append({
                        'f_name':food.f_name,
                        'price':food.price,
                        'rating':food.rating,
                    })
                return jsonify(available_items=items)


#---------------------------------------------------------------------------------


        @app.route('/order_history',methods=['GET'])
        def order_history():
            c_id=int(request.args['c_id'])
            orders=Order.query.order_by(Order.o_id.desc()).filter_by(c_id=c_id).all()
            if orders==None:
                jsonify(msg="No order history")
            else:
                order_history={}
                for order in orders:
                    if order.date not in order_history:
                        order_history[order.date]=[]
                    order_details={
                        "item_name":FoodItems.query.filter_by(f_id=order.f_id).first().f_name,
                        "quantity": order.quantity
                    }
                    order_history[order.date].append(order_details)
                return jsonify(order_history=order_history)


#---------------------------------------------------------------------------------


        @app.route('/filter_by_price',methods=['GET'])
        def filter_by_price():
            price=int(request.args['price'])
            avail_foods=FoodItems.query.filter_by(availability=True).all()
            if avail_foods==None:
                return jsonify(msg="No item available")
            else:    
                items=[]
                for food in avail_foods:
                    if food.price<=price:
                        items.append({
                        'f_name':food.f_name,
                        'price':food.price,
                        'rating':food.rating,
                    })
                if items==[]:
                    return jsonify(msg=f"No item available below {price}")
                else:
                    return jsonify(avail_items=items)


#----------------------------------------------------------------------------------


        @app.route('/most_ordered',methods=['GET'])
        def most_ordered():
            items=FoodItems.query.order_by(FoodItems.ordercount.desc()).limit(5).all()
            if items==None:
                return jsonify(msg="No item available")
            else:
                top_items=[]
                for item in items:
                    top_items.append({
                        'f_name':item.f_name,
                        'price':item.price,
                        'rating':item.rating
                    })
                return jsonify(most_ordered_items=top_items)


#-------------------------------------------------------------------------------    


        @app.route("/placing_order",methods=["POST"])
        def placing_order():
            c_id=request.args['c_id']
            data=request.get_json()
            total_price=0
            order_ids=[]
            for order in data['orders']:
                f_name=order['f_name']
                item=FoodItems.query.filter_by(f_name=f_name).first()
                item.ordercount+=1
                total_price+=(item.price*order['quantity'])
                
                new_order=Order(
                    f_id=item.f_id,
                    quantity=order['quantity'],
                    cost=item.price*order['quantity'],
                    date=str(date.today()),
                    c_id=c_id,
                    delivery_status=False
                )
                db.session.add(new_order)
                db.session.commit()
                last_order=Order.query.order_by(Order.o_id.desc()).first()
                order_ids.append(last_order.o_id)

            return jsonify(order_list=order_ids,total_price=total_price)  


#-------------------------------------------------------------------------------------


        @app.route('/undelivered_order', methods=['GET'])
        def undelivered_order():
            c_id=int(request.args['c_id'])
            orders=Order.query.filter_by(c_id=c_id).all()
            undelivered_order=[]
            for order in orders:
                if order.delivery_status==False:
                    undelivered_order.append(order.o_id)
            
            if len(undelivered_order) == 0:
                return jsonify(msg="No pending orders")
            return jsonify(order_ids=undelivered_order)


#----------------------------------------------------------------------------------


        @app.route('/cancel_order', methods=['POST'])
        def cancel_order():
            o_id=int(request.args['o_id'])
            try:
                UserRating.query.filter_by(o_id=o_id).delete()
            except:
                pass
            Order.query.filter_by(o_id=o_id).delete()

            db.session.commit()

            return jsonify(msg=f"Order number {o_id} canceled successfully") 


#-------------------------------------------------------------------------------


        @app.route("/giving_rating",methods=["POST"])
        def giving_rating():
            data=request.get_json()
            new_rating=UserRating(
                o_id=data['o_id'],
                rating=data['rating']
            )
            db.session.add(new_rating)
            f_id=Order.query.filter_by(o_id=data['o_id']).first().f_id
            fooditem=FoodItems.query.filter_by(f_id=f_id).first()
            
            old_ratingcount = fooditem.ratingcount
            fooditem.ratingcount+=1
            new_ratingcount = fooditem.ratingcount

            fooditem.rating = ((fooditem.rating*old_ratingcount)+data['rating'])/new_ratingcount
            db.session.commit()

            return jsonify(msg="Rating updated successfully")     


#----------------------------------------------------------------------------------------
        ####--------------------- OWNER SIDE ENDPOINTS ----------------------------------
#----------------------------------------------------------------------------------------


        @app.route("/add_new_food_item",methods=["POST"])
        def add_new_food_item():
            food=request.get_json()
            new_food=FoodItems(
                price=food['price'],
                f_name=food['f_name'],
                rating=0,
                ordercount=0,
                ratingcount=0,
                availability=True
            )
            db.session.add(new_food)
            db.session.commit()
            return jsonify(msg="New item added successfully")


#-------------------------------------------------------------------------------------  

        @app.route('/change_availability',methods=['POST'])
        def change_availability():
            data=request.get_json()
            item=FoodItems.query.filter_by(f_name=data['f_name']).first()
            if item.availability==True:
                item.availability=False
            else:
                item.availability=True

            db.session.commit()
            return jsonify(msg="Availability changed succesfully")


#--------------------------------------------------------------------------------

        
        @app.route("/change_item_price",methods=["POST"])
        def change_item_price():
            data=request.get_json()
            item=FoodItems.query.filter_by(f_name=data['f_name']).first()
            item.price=data['new_price']

            db.session.commit()
            return jsonify(msg="Price changed succesfully")


#---------------------------------------------------------------------------------


        @app.route('/check_active_orders',methods=['GET'])
        def check_active_orders():
            actv_orders=Order.query.filter_by(delivery_status=False).all()
            if actv_orders==None:
                return jsonify(msg="No active orders to deliver")
            else:
                orders=[]
                for order in actv_orders:
                    orders.append({
                        "order_id":order.id,
                        "item_name":FoodItems.query.filter_by(f_id=order.f_id).first().f_name,
                        "quantity":order.quantity
                    })



#-----------------------------------------------------------------------------------


        @app.route('/change_delivery_status', methods=['POST'])
        def change_delivery_status():
            o_id=int(request.args['o_id'])
            order=Order.query.filter_by(o_id=o_id).first()
            order.delivery_status=True
            db.session.commit()
            return jsonify(msg="delivery status changed successfully")


#------------------------------------------------------------------------------------


        @app.route('/todays_sell',methods=['GET'])
        def todays_sell():
            today=str(date.today())
            todays_orders=Order.query.filter_by(date=today).all()
            if todays_orders==None:
                return jsonify(msg="today no sell till now")
            else:
                orders=[]
                total_sell=0
                for order in todays_orders:
                    total_sell+=order.cost
                    orders.append({
                        "order_id":order.id,
                        "item_name":FoodItems.query.filter_by(f_id=order.f_id).first().f_name,
                        "quantity":order.quantity,
                        "price":order.cost
                    })

                return jsonify(total_sell=total_sell,orders=orders)


#--------------------------------------------------------------------------------------------
                

        # db.drop_all()
        db.create_all()
        db.session.commit()

    return app


if __name__=='__main__':
    app=create_app()
    app.run(debug=True)