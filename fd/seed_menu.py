from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb+srv://harshabathala12:harshasai0810@fooddeliverydb.l0h7yuy.mongodb.net/?retryWrites=true&w=majority&appName=foodDeliveryDB")
db = client['foodDeliveryDB']
menu = db['menu']

# Updated prices based on your latest hardcoded menu
updated_menu = {
    "Pizza": 249,
    "Burger": 149,
    "Pasta": 199,
    "Sushi": 299,
    "Steak": 349,
    "Tacos": 179,
    "Fried Chicken": 229,
    "Ramen": 189,
    "Cheesecake": 129,
    "Coffee": 99
}

# Update items one by one
for item_name, new_price in updated_menu.items():
    menu.update_one(
        {"name": item_name},
        {"$set": {"price": new_price}}
    )

print("✅ Prices updated in MongoDB!")
