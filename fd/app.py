from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from flask import render_template, request, redirect, url_for
import json

app = Flask(__name__)

# ✅ MongoDB Connection
MONGO_URI = "mongodb+srv://harshabathala12:harshasai0810@fooddeliverydb.l0h7yuy.mongodb.net/?retryWrites=true&w=majority&appName=foodDeliveryDB"
client = MongoClient(MONGO_URI)
db = client['foodDeliveryDB']
contacts_collection = db['contacts']
addresses_collection = db['addresses']
menu_collection = db['menu']

# ✅ Home Page
@app.route('/')
def home():
    return render_template('index.html')

# ✅ Menu Page with food items from DB
@app.route('/menu')
def menu():
    food_items = list(menu_collection.find({}, {'_id': 0}))  # Exclude _id for cleaner rendering
    return render_template('menu.html', food_items=food_items)

# ✅ Contact Page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# ✅ Cart Page
@app.route('/cart')
def cart():
    return render_template('cart.html')

# ✅ Address Page
@app.route('/address')
def address():
    return render_template('address.html')

from flask import render_template
import random

@app.route('/thankyou')
def thankyou():
    order_id = f"#FD{random.randint(100000, 999999)}"
    eta = "30–40 minutes"
    return render_template("thankyou.html", order_id=order_id, eta=eta)


# ✅ Contact Form Submission
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    contacts_collection.insert_one({'name': name, 'email': email, 'message': message})
    return render_template('confirmation.html', name=name)


@app.route('/submit_address', methods=['POST'])
def submit_address():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    landmark = request.form.get('landmark')
    instructions = request.form.get('instructions')
    cart_data = request.form.get('cartData')

    try:
        cart = json.loads(cart_data)
    except Exception as e:
        cart = []

    total = sum(item['price'] * item['quantity'] for item in cart)

    return render_template('thankyou.html',
                           name=name,
                           email=email,
                           phone=phone,
                           address=address,
                           landmark=landmark,
                           instructions=instructions,
                           cart=cart,
                           total=total)

# ✅ Recommendation Route using HARDCODED menu (not MongoDB)
@app.route('/recommend', methods=['GET'])
def recommend():
    item_name = request.args.get('item', '').strip().lower()

    # Hardcoded menu items
    items = [
        {"name": "Pizza", "description": "Cheesy pizza with tomato sauce and toppings", "price": "199"},
        {"name": "Burger", "description": "Grilled patty with lettuce, tomato and cheese", "price": "149"},
        {"name": "Pasta", "description": "Creamy white sauce pasta with herbs", "price": "179"},
        {"name": "Sushi", "description": "Fresh sushi rolls with wasabi and soy sauce", "price": "299"},
        {"name": "Steak", "description": "Juicy grilled steak with pepper sauce", "price": "349"},
        {"name": "Tacos", "description": "Spicy Mexican tacos with salsa and cheese", "price": "129"},
        {"name": "Fried Chicken", "description": "Crispy fried chicken with special seasoning", "price": "179"},
        {"name": "Ramen", "description": "Hot and spicy Japanese noodle soup", "price": "199"},
        {"name": "Cheesecake", "description": "Rich and creamy cheesecake slice", "price": "149"},
        {"name": "Coffee", "description": "Fresh brewed coffee served hot", "price": "99"},
    ]

    df = pd.DataFrame(items)
    df['name_lower'] = df['name'].str.lower()

    if item_name not in df['name_lower'].values:
        return jsonify({'error': f'Item "{item_name}" not found in menu.'}), 404

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['description'])

    idx = df[df['name_lower'] == item_name].index[0]
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:4]
    recommended_items = df.iloc[[i[0] for i in sim_scores]]

    return jsonify(recommended_items[['name', 'description', 'price']].to_dict(orient='records'))

# ✅ Run the App
if __name__ == '__main__':
    app.run(debug=True)
