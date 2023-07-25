# MeAnalytics for Resturants

Tables
    - CustomerInfo
            - Phone number (unique) (len==10)
            - Name
            - Customer id (primary key)
            
    - Order
            - Order id (primary key)
            - Quantity of item ordered
            - Food id (foreign key)
            - Order cost
            - Date
            - customer id (foreign key)
                    - Delivery Status
            
    - UserRatings
            - Order id (primary & foreign key)
            - Rating given
            
    - FoodItems
            - Item id (primary key)
            - Item price
            - Item name
            - Item rating
            - Orderd Count
                    - Rating Count
            - Availability

Endpoints
    User
        - Login/Signup
        - Show menu
        - Order history
        - Filter by price
        - Most ordered
        - Placing order
        - Undelivered orders
        - Cancel order
        - Giving rating
    Owner
        - Add new food item
        - Change availability
        - Change item price
        - Check active orders
        - Change delivery status
        - Todays sell