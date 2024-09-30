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

    for item in items:
        item_data = item.to_dict()
        item_name = item_data.get('name')
        supplier_name = item_data.get('supplier')

        # Check if it's a wheel or frame and categorize based on supplier
        if supplier_name == 'Supplier 1':
            wheel_list.append(item_name)
        elif supplier_name == 'Supplier 2':
            frame_list.append(item_name)

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
                        frame_list=frame_list)

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
            u'frame': frame
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

    return render_template('dashboard.html', username=session.get('username'), purchases=purchase_list)
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
    
    # Mendefinisikan informasi untuk kedua supplier
    suppliers = [
        {
            'name': 'Supplier 1',
            'url': 'http://167.99.238.114:8000/products',
            'key_name': 'nama_produk',
            'key_price': 'harga',
            'key_id': 'id_produk'
        },
        {
            'name': 'Supplier 2',
            'url': 'https://suplierman.pythonanywhere.com/products/api/products',
            'key_name': 'nama_produk',
            'key_price': 'harga',
            'key_id': 'id_produk'
        }
        # {
        #     'name': 'Supplier 3',
        #     'url': 'https://suplierman.pythonanywhere.com/products/api/products',
        #     'key_name': 'nama_produk',
        #     'key_price': 'harga',
        #     'key_id': 'id_produk'
        # }
    ]
    
    # Fungsi untuk memproses setiap supplier
    def process_supplier(supplier):
        supplier_name = supplier['name']
        url = supplier['url']
        key_name = supplier['key_name']
        key_price = supplier['key_price']
        key_id = supplier['key_id']
        
        response = requests.get(url)
        if response.status_code == 200:
            items_api = response.json()
            print(f"Successfully retrieved products from {supplier_name}.")
        else:
            print(f"Failed to retrieve products from {supplier_name}. Status code: {response.status_code}", "error")
            return []
        
        # Mengambil daftar produk dari Firestore untuk supplier ini
        items_db = [item.to_dict() for item in items_ref.where('supplier', '==', supplier_name).stream()]
        
        # Buat set supplier_id dari API untuk memudahkan pencarian
        supplier_ids_api = set()
        new_items = []
        
        for item_api in items_api:
            product_name = item_api.get(key_name)
            product_price = item_api.get(key_price)
            supplier_id = item_api.get(key_id)
            
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
        
        # Mengidentifikasi produk yang ada di Firestore tetapi tidak ada di API
        supplier_ids_db = set(item['supplier_id'] for item in items_db)
        ids_to_delete = supplier_ids_db - supplier_ids_api
        
        # Hapus produk yang tidak ada di API
        for item in items_db:
            if item['supplier_id'] in ids_to_delete:
                try:
                    # Cari dokumen berdasarkan ID Firestore
                    doc_ref = items_ref.where('supplier_id', '==', item['supplier_id']).where('supplier', '==', supplier_name).stream()
                    for doc in doc_ref:
                        doc.reference.delete()
                        print(f"Deleted product from {supplier_name}: {item['name']} (ID: {item['supplier_id']})")
                except Exception as e:
                    flash(f"Error deleting product '{item['name']}' from {supplier_name}: {str(e)}", "error")
        
        return new_items
    
    # Memproses kedua supplier dan menyimpan daftar produk baru masing-masing
    new_items_supplier1 = process_supplier(suppliers[0])
    new_items_supplier2 = process_supplier(suppliers[1])
    # new_items_supplier3 = process_supplier(suppliers[2])
    
    # Fetch the updated list of items from Firestore
    updated_items = [item.to_dict() for item in items_ref.stream()]
    
    # Memisahkan daftar item berdasarkan supplier
    items_supplier1 = [item for item in updated_items if item.get('supplier') == 'Supplier 1']
    items_supplier2 = [item for item in updated_items if item.get('supplier') == 'Supplier 2']
    # items_supplier3 = [item for item in updated_items if item.get('supplier') == 'Supplier 3']
    
    # Render the warehouse page dengan daftar item yang diperbarui
    return render_template(
        'warehouse.html',
        username=session.get('username'),
        supplier1_new_items=new_items_supplier1,
        supplier2_new_items=new_items_supplier2,
        # supplier3_new_items=new_items_supplier3,
        items_supplier1=items_supplier1,
        items_supplier2=items_supplier2,
        # items_supplier3=items_supplier3
    )
@app.route('/warehouse/addItems/', methods=['POST'])
def addItems():
    if 'logged_in' not in session:
        return redirect(url_for('signin'))
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
if __name__ == "__main__":
    app.run(debug=True)