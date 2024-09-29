import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = "supersecretkey"

def format_currency(value):
    return "Rp. {:,}".format(int(value))

# Daftarkan filter ke Jinja
app.jinja_env.filters['currency'] = format_currency

# Konfigurasi Firebase
firebaseConfig = {
    'apiKey': "AIzaSyC6BuiB_At-GaFT3t4a5cuPzzFM0Jf9GfQ",
    'authDomain': "retailptsepedaonthelsurabaya.firebaseapp.com",
    'projectId': "retailptsepedaonthelsurabaya",
    'storageBucket': "retailptsepedaonthelsurabaya.appspot.com",
    'messagingSenderId': "438136407791",
    'appId': "1:438136407791:web:d796208b0179e7ad9afd1a",
    'measurementId': "G-3HE1W8GBQE",
    'databaseURL': ""
}

# Inisialisasi Firestore dengan Firebase Admin SDK
cred = credentials.Certificate('retailptsepedaonthelsurabaya-firebase-adminsdk-hjdab-2987e4b3c3.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('home'))
    return render_template('guestArea.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            # Cari user berdasarkan username di Firestore
            users_ref = db.collection(u'users')
            query = users_ref.where(u'username', u'==', username).stream()
            user = None
            for doc in query:
                user = doc.to_dict()
            
            if user and check_password_hash(user['password'], password):
                session['logged_in'] = True
                session['username'] = username
                # flash('Successfully logged in!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password.', 'error')
        except Exception as e:
            flash('Error during login: ' + str(e), 'error')
    
    if 'logged_in' in session:
        return redirect(url_for('home'))
    return render_template('signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        hashed_password = generate_password_hash(password)
        
        try:
            db.collection(u'users').add({
                u'username': username,
                u'password': hashed_password,
                u'role': role
            })
            flash('Account created successfully!', 'success')
            return redirect(url_for('signup'))
        except Exception as e:
            flash('Error creating account: ' + str(e), 'error')
    return render_template('signup.html')

# Tentukan folder untuk menyimpan gambar
UPLOAD_FOLDER = os.path.join('static', 'img')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Tambahkan folder upload di konfigurasi app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Fungsi untuk memeriksa ekstensi file yang diizinkan
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/addProduct', methods=['POST'])
def addProduct():
    name = request.form.get('name')
    price = request.form.get('price')
    image = request.files.get('image')
    wheel = request.form['wheel']
    frame = request.form['frame']

    # Cek apakah semua field diisi
    if not name or not price or not image:
        flash('Please fill out all fields and upload an image.', 'error')
        return redirect(url_for('product'))

    price_cleaned = price.replace('Rp', '').replace('.', '').replace(',', '').strip()

    try:
        price_numeric = int(price_cleaned)  # Mengonversi string menjadi integer
    except ValueError:
        flash('Invalid price format. Please enter a valid price.', 'error')
        return redirect(url_for('product'))
    
    # Simpan gambar di folder static/img
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        try:
            db.collection(u'product').add({
                u'name': name,
                u'price': price_numeric,
                u'image': filename,
                u'wheel': wheel,
                u'frame': frame
            })
            flash('Product added successfully!', 'success')
            return redirect(url_for('product'))
        except Exception as e:
            flash(f'Error adding product: {str(e)}', 'error')
            return redirect(url_for('product'))
    else:
        flash('Invalid image file. Please upload a valid image.', 'error')
        return redirect(url_for('product'))
@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('signin'))

    db = firestore.client()
    purchases_ref = db.collection(u'purchases')
    purchases = purchases_ref.stream()

    purchase_list = []

    # Loop through each purchase in the 'purchases' collection
    for purchase in purchases:
        purchase_data = purchase.to_dict()
        
        purchase_data['id'] = purchase.id

        # List to store detailed product information including prices
        detailed_products = []
        total_transaction_price = 0

        for product in purchase_data.get('products', []):
            product_id = product.get('id')
            product_quantity = product.get('quantity')

            # Fetch product details from the 'product' collection based on the product ID
            product_ref = db.collection(u'product').document(product_id).get()
            product_details = product_ref.to_dict()

            if product_details:
                product_price = float(product_details.get('price', 0))
                total_price = product_quantity * product_price
                total_transaction_price += total_price

                # Add the product details including price and total price to the detailed product list
                detailed_products.append({
                    'name': product_details.get('name'),
                    'quantity': product_quantity,
                    'price': product_price,
                    'total_price': total_price
                })

        # Add the detailed products back to the purchase data
        purchase_data['detailed_products'] = detailed_products
        purchase_data['total_transaction_price'] = total_transaction_price
        purchase_list.append(purchase_data)

    return render_template('dashboard.html', username=session.get('username'), purchases=purchase_list)
@app.route('/home')
def home():
    if 'logged_in' not in session:
        return redirect(url_for('signin'))
    db = firestore.client()
    products_ref = db.collection(u'product')
    products = products_ref.stream()

    items_ref = db.collection(u'items')
    items = items_ref.stream()

    item_stock = {}
    for item in items:
        item_data = item.to_dict()
        item_stock[item_data['name']] = int(item_data['amount'])

    product_list = []
    
    for product in products:
        product_data = product.to_dict()
        product_data['id'] = product.id 

        # Ambil requirement produk
        wheel = product_data.get('wheel', None)
        frame = product_data.get('frame', None)

        # Cek stok untuk setiap requirement dari warehouse
        wheel_stock = item_stock.get(wheel, 0)
        frame_stock = item_stock.get(frame, 0)

        # Hitung stok minimal berdasarkan requirement (misal, ban dan frame harus ada)
        product_stock = min(wheel_stock, frame_stock) if wheel and frame else 0

        # Tambahkan data stok ke dalam data produk
        product_data['stock'] = product_stock
        product_list.append(product_data)
    return render_template('home.html', username=session.get('username'), products=product_list)

@app.route('/product')
def product():
    if 'logged_in' not in session:
        return redirect(url_for('signin'))
    db = firestore.client()
    products_ref = db.collection(u'product')
    products = products_ref.stream()
    items_ref = db.collection(u'items')
    items = items_ref.stream()

    item_stock = {}
    for item in items:
        item_data = item.to_dict()
        item_stock[item_data['name']] = int(item_data['amount'])

    product_list = []
    
    for product in products:
        product_data = product.to_dict()

        # Ambil requirement produk
        wheel = product_data.get('wheel', None)
        frame = product_data.get('frame', None)

        # Cek stok untuk setiap requirement dari warehouse
        wheel_stock = item_stock.get(wheel, 0)
        frame_stock = item_stock.get(frame, 0)

        # Hitung stok minimal berdasarkan requirement (misal, ban dan frame harus ada)
        product_stock = min(wheel_stock, frame_stock) if wheel and frame else 0

        # Tambahkan data stok ke dalam data produk
        product_data['stock'] = product_stock
        product_list.append(product_data)

    return render_template('product.html', username=session.get('username'), products=product_list)

@app.route('/purchase_products', methods=['POST'])
def purchase_products():
    selected_products = []
    db = firestore.client()
    products_ref = db.collection(u'product')
    products = products_ref.stream()

    for product in products:
        product_id = product.id
        quantity = request.form.get(f'quantity-{product_id}')
        
        if quantity and int(quantity) > 0:
            product_name = request.form.get(f'product_name-{product_id}')
            selected_products.append({
                'id': product_id,
                'name': product_name,
                'quantity': int(quantity)
            })

    if selected_products:
        try:
            purchase_data = {
                'user': session.get('username'),
                'products': selected_products,
                'total_items': sum([p['quantity'] for p in selected_products]),
                'storeName': 'Sepeda Onthel Skena',
                'storeLoc': 'bali',
                'timestamp': firestore.SERVER_TIMESTAMP,
            }
            for product in selected_products:
                product_id = product['id']
                quantity = product['quantity']
                
                # Ambil data produk untuk mendapatkan requirement
                product_ref = db.collection(u'product').document(product_id).get()
                product_data = product_ref.to_dict()

                if product_data:
                    wheel_type = product_data.get('wheel')
                    frame_type = product_data.get('frame')

                    # Kurangi stok wheel (Ban)
                    if wheel_type:
                        decrement_item_stock(db, wheel_type, quantity)

                    # Kurangi stok frame
                    if frame_type:
                        decrement_item_stock(db, frame_type, quantity)
            
            db.collection(u'purchases').add(purchase_data)
            flash("Purchase successfully processed and warehouse updated!", "success")
        except Exception as e:
            flash(f"Error processing purchase: {str(e)}", "error")
    else:
        flash("No products selected!", "error")
    
    return redirect(url_for('home'))
def decrement_item_stock(db, item_name, quantity):
    try:
        items_ref = db.collection(u'items')
        query = items_ref.where(u'name', u'==', item_name).get()

        if query:
            item_ref = query[0].reference
            item_data = query[0].to_dict()

            current_stock = int(item_data.get('amount', 0))
            new_stock = max(current_stock - quantity, 0)

            # Update stok di Firestore
            item_ref.update({u'amount': str(new_stock)})
        else:
            flash(f"Item '{item_name}' not found in warehouse.", "error")
    except Exception as e:
        flash(f"Error updating stock for item '{item_name}': {str(e)}", "error")

@app.route('/warehouse')
def warehouse():
    if 'logged_in' not in session:
        return redirect(url_for('signin'))
    
    db = firestore.client()
    items_ref = db.collection(u'items')
    items = items_ref.stream()

    item_list = []
    
    for item in items:
        item_data = item.to_dict()
        item_list.append(item_data)

    return render_template('warehouse.html', username=session.get('username'), items=item_list)
@app.route('/signout', methods=['POST'])
def signout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('index'))
@app.route('/edit_transaction/<transaction_id>', methods=['POST'])
def edit_transaction(transaction_id):
    if 'logged_in' not in session:
        return redirect(url_for('signin'))

    db = firestore.client()

    # Fetch the original transaction data
    transaction_ref = db.collection(u'purchases').document(transaction_id)
    transaction = transaction_ref.get().to_dict()

    if not transaction:
        flash("Transaction not found.", "error")
        return redirect(url_for('dashboard'))

    total_items = 0
    updated_products = []
    for product in transaction.get('products', []):
        product_name = product.get('name')
        new_quantity = int(request.form.get(f'quantity-{product_name}', product['quantity']))
        total_items += new_quantity
        updated_products.append({
            'id': product.get('id'),
            'name': product_name,
            'quantity': new_quantity,
        })

    # Update transaction data in Firestore
    try:
        transaction_ref.update({
            'products': updated_products,
            'total_items': total_items
        })
        flash("Transaction updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating transaction: {str(e)}", "error")

    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(debug=True)