# main.py (Updated to fully support admin panel, car CRUD, and product submissions)

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from forms import CarForm
from models import db, Car, User, Submission, Cart, CarImage
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.template_filter('format_price')
def format_price(value):
    return f"{value:,.2f}"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()




@app.route('/')
def index():
    name = request.args.get('name', '').lower()
    brand = request.args.get('brand', '').lower()
    year = request.args.get('year')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    query = Car.query

    if name:
        query = query.filter(Car.name.ilike(f"%{name}%"))
    if brand:
        query = query.filter(Car.brand.ilike(f"%{brand}%"))
    if year and year.isdigit():
        query = query.filter(Car.year == int(year))
    if min_price and min_price.replace('.', '', 1).isdigit():
        query = query.filter(Car.price >= float(min_price))
    if max_price and max_price.replace('.', '', 1).isdigit():
        query = query.filter(Car.price <= float(max_price))

    cars = query.all()
    return render_template('index.html', cars=cars)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        flash('Message sent successfully!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html') 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form.get('name')
        role = 'editor'
        if not User.query.first():
            role = 'admin'
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('dashboard.html', users=users)

@app.route('/submit_product', methods=['GET', 'POST'])
@login_required
def submit_product():
    form = CarForm()
    if form.validate_on_submit():
        submission = Submission(
            name=form.name.data,
            price=form.price.data,
            description=form.description.data,
            image=form.image.data
        )
        db.session.add(submission)
        db.session.commit()
        flash('Car submitted for approval', 'success')
        return redirect(url_for('submit_product'))
    return render_template('submit_products.html', form=form)

@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    cars = Car.query.all()
    submissions = Submission.query.all()
    return render_template('admin.html', cars=cars, submissions=submissions)

from flask import current_app  # Needed for app context if logging or config is used


from werkzeug.utils import secure_filename
import os
from werkzeug.utils import secure_filename
import os

@app.route('/admin/add_car', methods=['GET', 'POST'])
@login_required
def add_car():
    
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        print("Form submitted.")
        name = request.form['name']
        price = request.form['price']
        year = request.form['year']
        description = request.form['description']
        
        # Create new car entry
        new_car = Car(
            name=name,
            price=price,
            year=year,
            description=description
        )
        db.session.add(new_car)
        db.session.flush()  # Assign ID before adding images

        # Handle image uploads
        upload_folder = os.path.join('static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        image_files = request.files.getlist('image')  # Name="image" in the form

        for idx, file in enumerate(image_files):
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)

                new_image = CarImage(
                    image_url=f"uploads/{filename}",
                    car_id=new_car.id,
                    position=idx
                )
                db.session.add(new_image)

        db.session.commit()
        flash('Car added successfully with images', 'success')
        return redirect(url_for('admin'))

    return render_template('add.html')  # Add template if not already

     

@app.route('/admin/edit_car/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_car(id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    car = Car.query.get_or_404(id)
    form = CarForm(obj=car)

    if form.validate_on_submit():
        car.name = form.name.data
        car.price = form.price.data
        car.year = form.year.data
        car.description = form.description.data

        # Handle uploaded images if any
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file.filename:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    new_image = CarImage(image_url=url_for('static', filename='uploads/' + filename), car_id=car.id)
                    db.session.add(new_image)

        db.session.commit()
        flash('Car updated successfully', 'success')
        return redirect(url_for('admin'))

    return render_template('edit_car.html', form=form, car=car)


@app.route('/admin/delete_car/<int:id>', methods=['POST'])
@login_required
def delete_car(id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    car = Car.query.get_or_404(id)
    db.session.delete(car)
    db.session.commit()
    flash('Car deleted successfully', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/approve_submission/<int:id>', methods=['POST'])
@login_required
def approve_submission(id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    submission = Submission.query.get_or_404(id)
    new_car = Car(
        name=submission.name,
        price=submission.price,
        description=submission.description,
        image=submission.image
    )
    db.session.add(new_car)
    db.session.delete(submission)
    db.session.commit()
    flash('Submission approved and added to cars', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/delete_submission/<int:id>', methods=['POST'])
@login_required
def delete_submission(id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    submission = Submission.query.get_or_404(id)
    db.session.delete(submission)
    db.session.commit()
    flash('Submission deleted successfully', 'success')
    return redirect(url_for('admin'))

@app.route('/product/<int:id>')
def product(id):
    car = Car.query.get_or_404(id)
    return render_template('products.html', car=car)

@app.route('/cart/add/<int:car_id>', methods=['POST'])
@login_required
def add_to_cart(car_id):
    car = Car.query.get_or_404(car_id)
    cart_item = Cart(user_id=current_user.id, car_id=car_id)
    db.session.add(cart_item)
    db.session.commit()
    flash('Car added to cart', 'success')
    return redirect(url_for('product', id=car_id))

@app.route('/cart')
@login_required
def view_cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    cars = [Car.query.get(item.car_id) for item in cart_items]
    return render_template('carts.html', cars=cars)

@app.route('/api/cars')
def get_cars():
    cars = Car.query.all()
    return jsonify([{
        'id': car.id,
        'name': car.name,
        'price': car.price,
        'description': car.description,
        'image': car.image
    } for car in cars])

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
