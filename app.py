import os
import pytz
import requests
from datetime import datetime
from flask import jsonify
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Firebase Configuration
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
cred = credentials.Certificate('retail.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Image Upload Requirements
UPLOAD_FOLDER = os.path.join('static', 'img')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Time Filter
def get_local_timestamp():
    tz = pytz.timezone('Asia/Jakarta')
    return datetime.now(tz)
def format_timestamp(timestamp, timezone_str='Asia/Jakarta'):
    # Pastikan timestamp adalah tipe yang sesuai
    if isinstance(timestamp, datetime):
        # Konversi dari UTC ke zona waktu lokal
        utc_zone = pytz.utc
        local_zone = pytz.timezone(timezone_str)
        utc_time = timestamp.replace(tzinfo=utc_zone)
        local_time = utc_time.astimezone(local_zone)
        return local_time.strftime('%H:%M:%S')
    else:
        return 'N/A'
app.jinja_env.filters['format_timestamp'] = format_timestamp

# Currency Filter
def format_currency(value):
    return "Rp. {:,}".format(int(value))
app.jinja_env.filters['currency'] = format_currency

# Fungsi untuk memeriksa ekstensi file yang diizinkan
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
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
def restore_item_stock(db, item_name, quantity):
    """Restore the item stock in the warehouse."""
    try:
        items_ref = db.collection(u'items')
        query = items_ref.where(u'name', u'==', item_name).get()

        if query:
            item_ref = query[0].reference
            item_data = query[0].to_dict()

            # Get the current stock and add the quantity back to the warehouse
            current_stock = int(item_data.get('amount', 0))
            new_stock = current_stock + quantity

            # Update stock in Firestore
            item_ref.update({u'amount': str(new_stock)})
        else:
            flash(f"Item '{item_name}' not found in warehouse.", "error")
    except Exception as e:
        flash(f"Error restoring stock for item '{item_name}': {str(e)}", "error")

# Guest Area
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
@app.route('/signout', methods=['POST'])
def signout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('index'))

# Product
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
    wheel_list = []
    frame_list = []
    sparepart_list = []

    for item in items:
        item_data = item.to_dict()
        item_name = item_data.get('name')
        supplier_name = item_data.get('supplier')

        # Check if it's a wheel or frame and categorize based on supplier
        if supplier_name == 'Supplier 1':
            wheel_list.append(item_name)
        elif supplier_name == 'Supplier 2':
            frame_list.append(item_name)
        elif supplier_name == 'Supplier 3':
            sparepart_list.append(item_name)

        # Keep track of stock levels
        item_stock[item_name] = int(item_data['amount'])

    product_list = []

    for product in products:
        product_data = product.to_dict()

        product_data['id'] = product.id

        # Get product requirements
        wheel = product_data.get('wheel', None)
        frame = product_data.get('frame', None)

        # Check stock for each requirement from warehouse
        wheel_stock = item_stock.get(wheel, 0)
        frame_stock = item_stock.get(frame, 0)

        # Calculate stock based on wheel and frame availability
        product_stock = min(wheel_stock, frame_stock) if wheel and frame else 0

        # Add stock data to product
        product_data['stock'] = product_stock
        product_list.append(product_data)

    return render_template('product.html', 
                        username=session.get('username'), 
                        products=product_list,
                        wheel_list=wheel_list,
                        frame_list=frame_list,
                        sparepart_list=sparepart_list)

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
@app.route('/editProduct/<product_id>', methods=['POST'])
def editProduct(product_id):
    name = request.form.get('name')
    price = request.form.get('price')
    image = request.files.get('image')
    wheel = request.form['wheel']
    frame = request.form['frame']
    sparepart = request.form['sparepart']


    # Cek apakah field penting diisi
    if not name or not price:
        flash('Please fill out all required fields.', 'error')
        return redirect(url_for('product'))

    price_cleaned = price.replace('Rp', '').replace('.', '').replace(',', '').strip()

    try:
        price_numeric = int(price_cleaned)
    except ValueError:
        flash('Invalid price format. Please enter a valid price.', 'error')
        return redirect(url_for('product'))

    # Jika ada gambar yang diunggah, simpan
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        filename = None

    # Perbarui data produk di Firestore
    try:
        product_ref = db.collection(u'product').document(product_id)
        update_data = {
            u'name': name,
            u'price': price_numeric,
            u'wheel': wheel,
            u'frame': frame,
            u'sparepart': sparepart
        }

        # Jika ada gambar baru, tambahkan ke data yang diperbarui
        if filename:
            update_data[u'image'] = filename

        product_ref.update(update_data)
        flash('Product updated successfully!', 'success')
        return redirect(url_for('product'))
    except Exception as e:
        flash(f'Error updating product: {str(e)}', 'error')
        return redirect(url_for('product'))
@app.route('/deleteProduct/<product_id>', methods=['POST'])
def deleteProduct(product_id):
    try:
        # Hapus produk dari Firestore
        product_ref = db.collection(u'product').document(product_id)
        product_ref.delete()

        flash('Product deleted successfully!', 'success')
        return redirect(url_for('product'))
    except Exception as e:
        flash(f'Error deleting product: {str(e)}', 'error')
        return redirect(url_for('product'))

# Cashier Area
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

# Dashboard (CRUD and Visualization)
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

    # BARU
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

    product_stocks = [product['stock'] for product in product_list]
    product_names = [product['name'] for product in product_list]

    
    # Siapkan data untuk visualisasi Chart 1 dan Chart 2
    monthly_sales = defaultdict(lambda: defaultdict(int))
    monthly_revenue = defaultdict(int)
    
    for purchase in purchase_list:
        if 'timestamp' in purchase:
            month = purchase['timestamp'].strftime("%B")
            for product in purchase.get('detailed_products', []):
                product_name = product.get('name', 'Unknown')
                quantity = product.get('quantity', 0)
                price = product.get('price', 0)
                monthly_sales[month][product_name] += quantity
                monthly_revenue[month] += quantity * price

    # Siapkan data untuk Chart 1 (Revenue)
    all_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    revenue_data = [monthly_revenue.get(month, 0) for month in all_months]

    # Siapkan data untuk Chart 2 (Sales per Product)
    labels = all_months
    all_products = set()
    for month_data in monthly_sales.values():
        all_products.update(month_data.keys())
    
    series = []
    for product in all_products:
        product_data = []
        for month in labels:
            product_data.append(monthly_sales[month].get(product, 0))
        series.append({
            'name': product,
            'data': product_data
        })

    # Render template dengan data penjualan dan pendapatan bulanan
    return render_template('dashboard.html', 
                        username=session.get('username'), 
                        purchases=purchase_list, 
                        products=product_list, 
                        product_stocks=product_stocks, 
                        product_names=product_names,
                        sales_data=series,
                        revenue_data=revenue_data,
                        months=labels)
@app.route('/edit_transaction/<transaction_id>', methods=['POST'])
def edit_transaction(transaction_id):
    if 'logged_in' not in session:
        return redirect(url_for('signin'))

    db = firestore.client()

    # Fetch the original transaction data
    transaction_ref = db.collection(u'purchases').document(transaction_id)
    transaction_snapshot = transaction_ref.get()
    transaction = transaction_snapshot.to_dict()

    if not transaction:
        flash("Transaction not found.", "error")
        return redirect(url_for('dashboard'))

    total_items = 0
    updated_products = []
    stock_adjustments = {}  # Dictionary to hold required item adjustments
    stock_update_errors = []
    for product in transaction.get('products', []):
        product_id = product.get('id')
        product_name = product.get('name')
        original_quantity = product['quantity']
        new_quantity = int(request.form.get(f'quantity-{product_name}', original_quantity))
        total_items += new_quantity
        updated_products.append({
            'id': product_id,
            'name': product_name,
            'quantity': new_quantity,
        })

        delta_quantity = new_quantity - original_quantity

        if delta_quantity != 0:
            # Fetch product details to get the required items
            product_ref = db.collection(u'product').document(product_id).get()
            product_data = product_ref.to_dict()

            if product_data:
                wheel_type = product_data.get('wheel')
                frame_type = product_data.get('frame')

                # For each required item, accumulate the total adjustment
                required_items = {}
                if wheel_type:
                    required_items[wheel_type] = required_items.get(wheel_type, 0) + delta_quantity
                if frame_type:
                    required_items[frame_type] = required_items.get(frame_type, 0) + delta_quantity

                # Update the stock_adjustments dictionary
                for item_name, adjustment in required_items.items():
                    stock_adjustments[item_name] = stock_adjustments.get(item_name, 0) + adjustment
            else:
                stock_update_errors.append(f"Product data not found for '{product_name}'.")
    # Check if there are any errors
    if stock_update_errors:
        flash("Some errors occurred while preparing to update stock:\n" + "\n".join(stock_update_errors), "error")
        return redirect(url_for('dashboard'))

    # Now, check if there is sufficient stock for all items
    items_ref = db.collection(u'items')
    insufficient_stock = False
    stock_check_errors = []
    for item_name, total_adjustment in stock_adjustments.items():
        if total_adjustment > 0:
            # Need to decrease stock by total_adjustment
            item_query = items_ref.where(u'name', u'==', item_name).get()
            if item_query:
                item_doc = item_query[0]
                item_data = item_doc.to_dict()
                current_stock = int(item_data.get('amount', 0))
                if current_stock < total_adjustment:
                    insufficient_stock = True
                    stock_check_errors.append(f"Not enough stock for item '{item_name}'. Required: {total_adjustment}, Available: {current_stock}")
            else:
                insufficient_stock = True
                stock_check_errors.append(f"Item '{item_name}' not found in warehouse.")
    if insufficient_stock:
        error_message = "Cannot update transaction due to insufficient stock:\n" + "\n".join(stock_check_errors)
        flash(error_message, "error")
        return redirect(url_for('dashboard'))

    # If sufficient stock, proceed to update the warehouse stock
    try:
        for item_name, total_adjustment in stock_adjustments.items():
            if total_adjustment > 0:
                # Need to decrease stock
                decrement_item_stock(db, item_name, total_adjustment)
            elif total_adjustment < 0:
                # Need to increase stock
                restore_item_stock(db, item_name, abs(total_adjustment))
        # Update transaction data in Firestore
        transaction_ref.update({
            'products': updated_products,
            'total_items': total_items
        })
        flash("Transaction updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating transaction: {str(e)}", "error")
        return redirect(url_for('dashboard'))

    return redirect(url_for('dashboard'))
@app.route('/delete_transaction/<transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    if 'logged_in' not in session:
        return redirect(url_for('signin'))

    db = firestore.client()

    try:
        # Retrieve the transaction being deleted
        transaction_ref = db.collection(u'purchases').document(transaction_id)
        transaction = transaction_ref.get().to_dict()

        if not transaction:
            flash("Transaction not found.", "error")
            return redirect(url_for('dashboard'))

        # Retrieve the products in the transaction
        products = transaction.get('products', [])

        # For each product, restore the corresponding wheel and frame stock to the warehouse
        for product in products:
            product_id = product.get('id')
            product_quantity = product.get('quantity')

            # Fetch the product details to get the wheel and frame types
            product_ref = db.collection(u'product').document(product_id).get()
            product_data = product_ref.to_dict()

            if product_data:
                wheel_type = product_data.get('wheel')
                frame_type = product_data.get('frame')

                # Restore stock for the wheel (if applicable)
                if wheel_type:
                    restore_item_stock(db, wheel_type, product_quantity)

                # Restore stock for the frame (if applicable)
                if frame_type:
                    restore_item_stock(db, frame_type, product_quantity)

        # Delete the transaction after restoring the stock
        transaction_ref.delete()

        flash("Transaction deleted successfully and warehouse stock updated!", "success")
    except Exception as e:
        flash(f"Error deleting transaction: {str(e)}", "error")

    return redirect(url_for('dashboard'))

# Warehouse
@app.route('/warehouse')
def warehouse():
    if 'logged_in' not in session:
        return redirect(url_for('signin'))
    
    # Inisialisasi Firestore
    db = firestore.client()
    items_ref = db.collection(u'items')
    
    suppliers = [
        {
            'name': 'Supplier 1',
            'url': 'http://167.99.238.114:8000/api/products',
            'key_name': 'nama_produk',
            'key_price': 'harga',
            'key_id': 'id_produk',
            'key_stock': 'stock',
            'weight': 'berat'
        },
        {
            'name': 'Supplier 2',
            'url': 'https://suplierman.pythonanywhere.com/products/api/products',
            'key_name': 'nama_produk',
            'key_price': 'harga',
            'key_id': 'id_produk',
            'key_stock': 'stock',
            'weight': 'berat'
        },
        {
            'name': 'Supplier 3',
            'url': 'https://supplier3.pythonanywhere.com/api/products',
            'key_name': 'nama_produk',
            'key_price': 'harga',
            'key_id': 'id_produk',
            'key_stock': 'stock',
            'weight': 'berat'
        }
    ]

    # Fungsi untuk memproses setiap supplier
    def process_supplier(supplier):
        supplier_name = supplier['name']
        url = supplier['url']
        key_name = supplier['key_name']
        key_price = supplier['key_price']
        key_id = supplier['key_id']
        key_stock = supplier['key_stock']
        weight = supplier['weight']
        
        response = requests.get(url)
        if response.status_code == 200:
            try:
                items_api = response.json()
                print(f"Successfully retrieved products from {supplier_name}.")
            except ValueError:
                flash(f"Invalid JSON response from {supplier_name}.", "error")
                return [], []
        else:
            flash(f"Failed to retrieve products from {supplier_name}. Status code: {response.status_code}", "error")
            return [], []
        
        # Mengambil daftar produk dari Firestore untuk supplier ini
        items_db = [item.to_dict() for item in items_ref.where('supplier', '==', supplier_name).stream()]
        
        # Buat set supplier_id dari API untuk memudahkan pencarian
        supplier_ids_api = set()
        new_items = []
        list_stock = []
        
        for item_api in items_api:
            product_name = item_api.get(key_name)
            product_price = item_api.get(key_price)
            supplier_id = item_api.get(key_id)
            weight = item_api.get(weight, 0)
            stock = item_api.get(key_stock, 0)
            
            if not product_name or not supplier_id:
                print(f"Produk tanpa nama atau ID ditemukan di {supplier_name}: {item_api}")
                continue  # Lewati produk tanpa nama atau ID
            
            # Menambahkan supplier_id ke set
            supplier_ids_api.add(supplier_id)
            
            # Cek apakah produk sudah ada di Firestore berdasarkan nama dan supplier_id
            exists = any(
                item['name'] == product_name and item.get('supplier_id') == supplier_id 
                for item in items_db
            )
            
            if not exists:
                # Menangani format harga
                try:
                    if isinstance(product_price, str):
                        # Jika harga berakhiran '.00', hapus bagian desimalnya
                        if product_price.endswith('.00'):
                            product_price = product_price[:-3]
                        # Konversi ke integer
                        product_price_int = int(product_price)
                    elif isinstance(product_price, float):
                        # Konversi float ke integer
                        product_price_int = int(product_price)
                    elif isinstance(product_price, int):
                        # Harga sudah integer
                        product_price_int = product_price
                    else:
                        # Format tidak dikenali, tetapkan ke 0 atau nilai default
                        product_price_int = 0
                        print(f"Unrecognized price format for product '{product_name}' from {supplier_name}: {product_price}")
                except (ValueError, TypeError) as e:
                    # Tangani kesalahan konversi
                    product_price_int = 0
                    print(f"Error processing price for product '{product_name}' from {supplier_name}: {str(e)}")
                
                new_item = {
                    'name': product_name,
                    'amount': 0,
                    'price': product_price_int,
                    'supplier': supplier_name,
                    'supplier_id': supplier_id
                }

                try:
                    items_ref.add(new_item)
                    new_items.append(new_item)
                    print(f"Added new product from {supplier_name}: {product_name}")
                except Exception as e:
                    flash(f"Error adding product '{product_name}' from {supplier_name}: {str(e)}", "error")
            
            if isinstance(product_price, str):
                # Jika harga berakhiran '.00', hapus bagian desimalnya
                if product_price.endswith('.00'):
                    product_price = product_price[:-3]
                # Konversi ke integer
                product_price_int = int(product_price)
            elif isinstance(product_price, float):
                # Konversi float ke integer
                product_price_int = int(product_price)
            elif isinstance(product_price, int):
                # Harga sudah integer
                product_price_int = product_price
            else:
                # Format tidak dikenali, tetapkan ke 0 atau nilai default
                product_price_int = 0
                print(f"Unrecognized price format for product '{product_name}' from {supplier_name}: {product_price}")
            list_stock.append({
                'name': product_name,
                'stock': stock,
                'price': product_price_int,
                'supplier': supplier_name,
                'weight': weight,
            })
        
        # Mengidentifikasi produk yang ada di Firestore tetapi tidak ada di API
        supplier_ids_db = set(item['supplier_id'] for item in items_db)
        ids_to_delete = supplier_ids_db - supplier_ids_api
        
        # Hapus produk yang tidak ada di API
        for item in items_db:
            if item['supplier_id'] in ids_to_delete:
                try:
                    # Cari dokumen berdasarkan supplier_id dan supplier name
                    doc_ref = items_ref.where('supplier_id', '==', item['supplier_id']).where('supplier', '==', supplier_name).stream()
                    for doc in doc_ref:
                        doc.reference.delete()
                        print(f"Deleted product from {supplier_name}: {item['name']} (ID: {item['supplier_id']})")
                        flash(f"Deleted product '{item['name']}' from {supplier_name} as it no longer exists in the API.", "info")
                except Exception as e:
                    flash(f"Error deleting product '{item['name']}' from {supplier_name}: {str(e)}", "error")
        
        return new_items, list_stock

    # Memproses kedua supplier dan menyimpan daftar produk baru masing-masing
    new_items_supplier1, list_stock1 = process_supplier(suppliers[0])
    new_items_supplier2, list_stock2 = process_supplier(suppliers[1])
    new_items_supplier3, list_stock3 = process_supplier(suppliers[2])
    
    # Fetch the updated list of items from Firestore
    updated_items = [item.to_dict() for item in items_ref.stream()]
    
    # Memisahkan daftar item berdasarkan supplier
    items_supplier1 = [item for item in updated_items if item.get('supplier') == 'Supplier 1']
    items_supplier2 = [item for item in updated_items if item.get('supplier') == 'Supplier 2']
    items_supplier3 = [item for item in updated_items if item.get('supplier') == 'Supplier 3']

    suppliers = [
        {'id': 'Supplier1', 'name': 'Supplier 1'},
        {'id': 'Supplier2', 'name': 'Supplier 2'},
        {'id': 'Supplier3', 'name': 'Supplier 3'},
    ]


    # Render the warehouse page dengan daftar item yang diperbarui
    return render_template(
        'warehouse.html',
        username=session.get('username'),
        supplier1_new_items=new_items_supplier1,
        supplier2_new_items=new_items_supplier2,
        supplier3_new_items=new_items_supplier3,
        items_supplier1=items_supplier1,
        items_supplier2=items_supplier2,
        items_supplier3=items_supplier3,
        suppliers=suppliers,
        list_stock1=list_stock1,
        list_stock2=list_stock2,
        list_stock3=list_stock3
    )
@app.route('/addItems/<supplier_name>', methods=['POST'])
def addItems(supplier_name):
    if 'logged_in' not in session:
        return redirect(url_for('signin'))

    # Tentukan ID supplier berdasarkan supplier_name
    supplier_map = {
        "Supplier 1": "SUP01",
        "Supplier 2": "SUP02",
        "Supplier 3": "SUP03"
    }

    suppliers = [
        {
            'name': 'Supplier 1',
            'url': 'http://167.99.238.114:8000/api/products',
            'key_name': 'nama_produk',
            'key_price': 'harga',
            'key_id': 'id_produk',
            'key_stock': 'stock',
            'weight': 'berat'
        },
        {
            'name': 'Supplier 2',
            'url': 'https://suplierman.pythonanywhere.com/products/api/products',
            'key_name': 'nama_produk',
            'key_price': 'harga',
            'key_id': 'id_produk',
            'key_stock': 'stock',
            'weight': 'berat'
        },
        {
            'name': 'Supplier 3',
            'url': 'https://supplier3.pythonanywhere.com/api/products',
            'key_name': 'nama_produk',
            'key_price': 'harga',
            'key_id': 'id_produk',
            'key_stock': 'stock',
            'weight': 'berat'
        }
    ]

    supplier_id = supplier_map.get(supplier_name)

    # Cari supplier yang sesuai
    supplier_info = next((supplier for supplier in suppliers if supplier['name'] == supplier_name), None)

    if not supplier_info:
        flash("Invalid supplier name.", "error")
        return redirect(url_for('warehouse'))

    # Ambil data produk dari API supplier
    try:
        response = requests.get(supplier_info['url'])
        if response.status_code != 200:
            flash(f"Failed to retrieve products from {supplier_name}.", "error")
            return redirect(url_for('warehouse'))
        items_api = response.json()  # Asumsikan responnya dalam format JSON
    except Exception as e:
        flash(f"Error fetching products from {supplier_name}: {str(e)}", "error")
        return redirect(url_for('warehouse'))

    # Inisialisasi data dari form
    cart = []
    total_price = 0
    total_weight = 0

    # Ambil data input dari form (items dan quantity)
    for key, value in request.form.items():
        if key.startswith("quantity-"):
            product_name = key.replace("quantity-", "")

            # Pastikan value tidak kosong
            if value.strip() == "":
                continue

            try:
                quantity = int(value)
            except ValueError:
                quantity = 0  # Tetapkan ke 0 jika tidak valid

            if quantity > 0:
                # Cari produk dalam items_api berdasarkan nama produk
                item_api = next((item for item in items_api if item[supplier_info['key_name']] == product_name), None)

                if item_api:
                    product_price = item_api.get(supplier_info['key_price'], 0)
                    product_weight = item_api.get(supplier_info['weight'], 0)
                    product_id = item_api.get(supplier_info['key_id'])

                    # Hitung total harga dan berat
                    total_price += int(product_price) * quantity
                    total_weight += float(product_weight) * quantity

                    # Tambahkan ke keranjang
                    cart.append({
                        "name": product_name,
                        "id_produk": product_id,
                        "quantity": quantity,
                        'price': product_price,
                    })

    if supplier_id == "SUP01":
        supdis = "Supplier1"
    elif supplier_id == "SUP02":
        supdis = "Supplier2"
    else:
        supdis = "Supplier3"
    # Tangkap distributor yang dipilih dari form
    distributor = request.form.get(f"dist-{supdis}")

    if not distributor:
        flash("Distributor not selected.", "error")
        return redirect(url_for('warehouse'))

    # Siapkan data yang akan dikirim ke API check_price
    payload = {
        "id_supplier": supplier_id,
        "cart": cart,
        "id_retail": "RET03",
        "id_distributor": distributor,
        "total_harga_barang": total_price,
        "total_berat_barang": total_weight,
        "kota_tujuan": "bali"
    }

    # return jsonify(payload)

    try:

        if supplier_id == "SUP01":
            check_price_response = requests.post("http://167.99.238.114:8000/api/check_price", json=payload)
        elif supplier_id == "SUP02":
            check_price_response = requests.post("https://suplierman.pythonanywhere.com/products/api/check_price", json=payload)
        else:
            check_price_response = requests.post("https://192.241.128.66:8000/api/cek_harga", json=payload)
        
        check_price_data = check_price_response.json()

        # Tampilkan hasil jika berhasil
        if check_price_response.status_code == 200:
            # Ambil informasi yang dibutuhkan dari respons
            harga_pengiriman = check_price_data.get("harga_pengiriman")
            lama_pengiriman = check_price_data.get("lama_pengiriman")
            id_log = check_price_data.get("id_log")
            try:
                total_price = int(total_price)
                harga_pengiriman = int(harga_pengiriman) 
                totalll = total_price + harga_pengiriman # atau float(harga_pengiriman) jika diperlukan
            except ValueError:
                flash("Invalid price format.", "error")
                return redirect(url_for('warehouse'))
            # Tampilkan informasi di halaman hasil
            return render_template("result.html", 
                                    supplier_name=supplier_name,
                                    supplier1_new_items=cart, 
                                    harga_pengiriman=harga_pengiriman, 
                                    lama_pengiriman=lama_pengiriman,
                                    total_harga_barang=total_price,
                                    total_price=totalll,
                                    id_log=id_log,
                                    distributor=distributor)
        else:
            flash("Failed to check price.", "error")
            return redirect(url_for('warehouse'))

    except Exception as e:
        flash(f"Error checking price: {str(e)}", "error")
        return redirect(url_for('warehouse'))

@app.route('/confirm_purchase', methods=['POST'])
def confirm_purchase():
    # Extract data from the form
    supplier_name = request.form.get('supplier_name')
    distributor = request.form.get('distributor')
    total_price = request.form.get('total_price')
    id_log = request.form.get('id_log')

    # Create the payload to send to the external API
    formatted_cart = []

    for i in range(len(request.form) // 2):
        id_product = request.form.get(f'cart[{i}][id_product]')
        quantity = request.form.get(f'cart[{i}][quantity]')
        if id_product and quantity:
            formatted_cart.append({
                'id_product': id_product,
                'quantity': int(quantity)  # Ensure quantity is an integer
            })

    payload = {
        "id_supplier": supplier_name,
        "id_log": id_log,
        "distributor": distributor,
        "total_price": total_price,
        "cart": formatted_cart
    }

    try:
        # Send POST request to external API
        if supplier_name == "Supplier 1":
            response = requests.post('http://167.99.238.114:8000/api/place_order', json=payload)
        elif supplier_name == "Supplier 2":
            response = requests.post("http://167.99.238.114:8000/check_price", json=payload)
        else:
            response = requests.post("http://192.241.128.66:8000/api/checkout", json=payload)
        if response.status_code == 200:
            result = response.json()

            # Get no_resi and purchase_id from the API response
            no_resi = result.get('no_resi')
            purchase_id = result.get('purchase_id')

            # Save no_resi and purchase_id to Firestore in the purchased_item collection
            purchased_item_ref = db.collection('purchased_item').document(purchase_id)
            purchased_item_ref.set({
                'no_resi': no_resi,
                'purchase_id': purchase_id,
                'supplier_name': supplier_name,
                'distributor': distributor,
                'total_price': total_price,
                'id_log': id_log,
                'cart': formatted_cart,
                'created_at': firestore.SERVER_TIMESTAMP
            })

            # Update quantity for each product in the items collection
            for item in formatted_cart:
                product_id = item['id_product']
                purchased_quantity = item['quantity']

                # Query to find the item in the 'items' collection by supplier_id and product_id
                items_query = db.collection('items').where('supplier_id', '==', product_id)

                # Get the documents matching the query
                docs = items_query.stream()

                found = False
                for doc in docs:
                    found = True
                    item_data = doc.to_dict()
                    current_quantity = item_data.get('amount', 0)

                    # Update the quantity by subtracting the purchased quantity
                    new_quantity = max(0, current_quantity + purchased_quantity)  # Prevent negative quantity

                    # Update the document with the new quantity
                    doc.reference.update({'amount': new_quantity})

                if not found:
                    # Handle case where the item with supplier_id and product_id doesn't exist
                    flash(f"Item with ID {product_id} and supplier {supplier_name} not found in 'items' collection.", "error")

            flash("Order placed successfully and saved to the warehouse, items updated!", "success")
        else:
            flash(f"Failed to place order. Status code: {response.status_code}", "error")

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")

    return redirect(url_for('warehouse'))


@app.route('/cancel_purchase')
def cancel_purchase():
    flash("Purchase canceled.", "success")
    return redirect(url_for('warehouse'))

# API
@app.route('/api/transaction9', methods=['GET'])
def get_purchases():
    
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

        purchase_data.pop('id', None)
        purchase_data.pop('products', None)
        # Add the detailed products back to the purchase data
        purchase_data['detailed_products'] = detailed_products
        purchase_data['total_transaction_price'] = total_transaction_price
        purchase_list.append(purchase_data)

    # Return the purchase list as JSON response
    return jsonify({"transaction": purchase_list, "status": "success"}), 200

@app.route('/api/transaction9', methods=['POST'])
def post_products():
    data = request.get_json()  # Ambil JSON dari body request
    selected_products = data.get('products', [])
    
    if not selected_products:
        return jsonify({"message": "No products selected!", "status": "error"}), 400
    
    db = firestore.client()
    
    try:
        # Mulai pemrosesan pembelian
        purchase_data = {
            'user': data.get('user', 'anonymous'),
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
        
        # Tambahkan data pembelian ke database
        db.collection(u'purchases').add(purchase_data)
        return jsonify({"message": "Purchase successfully processed and warehouse updated!", "status": "success"}), 200
    
    except Exception as e:
        return jsonify({"message": f"Error processing purchase: {str(e)}", "status": "error"}), 500
    # Track Order

@app.route('/tracking')
def tracking():
    # Ambil pesanan dari Firebase
    db = firestore.client()
    purchases_ref = db.collection(u'purchased_item')
    purchases = purchases_ref.stream()
    
    # Jika tidak ada pesanan ditemukan, set orders ke dict kosong
    orders = {purchase.id: purchase.to_dict() for purchase in purchases} if purchases else {}
    
    return render_template('tracking.html', orders=orders)

@app.route('/api/track/order', methods=['POST'])
def track_order():
    data = request.get_json()
    print(data)

    if not data.get('no_resi') or not data.get('id_distributor'):  # Pastikan no_resi dan id_distributor ada
        return jsonify({"error": "No resi, ID distributor, dan ID Supplier diperlukan"}), 400

    distributor_data = {}
    try:
        if data['id_distributor'] == 'DIS01':
            response = requests.get('http://167.99.238.114:8000/track_order')  # Ganti endpoint
        elif data['id_distributor'] == 'DIS02':
            response = requests.get('http://167.99.238.114:8000/track_order')  # Sesuaikan endpoint jika berbeda
        elif data['id_distributor'] == 'DIS03':
            response = requests.get(f"http://159.223.41.243:8000/api/status/{data['no_resi']}")  # Sesuaikan endpoint jika berbeda
        else:
            return jsonify({"error": "Supplier tidak dikenali"}), 400

        distributor_data = response.json()
        distributor_data['no_resi'] = data['no_resi']
        return jsonify(distributor_data), 200

    except Exception as e:
        return jsonify({"error": f"Gagal menghubungi distributor: {str(e)}"}), 500

def get_data_pemesanan():
    # Fetch orders from Firebase
    db = firestore.client()
    purchases_ref = db.collection(u'purchased_item')
    purchases = purchases_ref.stream()
    
    # Jika tidak ada pesanan ditemukan, set orders ke dict kosong
    orders = {purchase.id: purchase.to_dict() for purchase in purchases} if purchases else {}

    return jsonify(orders), 200


if __name__ == "__main__":
    app.run(debug=True)