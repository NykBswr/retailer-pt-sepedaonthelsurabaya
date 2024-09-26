from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Ganti dengan key yang aman

USERNAME = "Admin Onthel"
PASSWORD = "kelompok9"

@app.route('/')
def index():
    # cek user
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))  
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))  
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))  
    return render_template('dashboard.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)  
    return redirect(url_for('index')) 

if __name__ == "__main__":
    app.run(debug=True)
