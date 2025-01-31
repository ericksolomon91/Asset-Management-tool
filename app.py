from flask import Flask, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
import random
import string
import os
import logging
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired

# Create the Flask app
app = Flask(__name__)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# PostgreSQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myapp_user:password@10.10.128.203/myapp_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking for performance
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_default_secret_key')  # Secret key for flash messages

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define the SparePart model
class SparePart(db.Model):
    __tablename__ = 'spare_parts'  # Explicitly set the table name

    id = db.Column(db.Integer, primary_key=True)  # Unique identifier
    part_number = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<SparePart {self.part_number} - {self.serial_number}>"

# Define the ShippedPart model
class ShippedPart(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier
    part_number = db.Column(db.String(50), nullable=False)
    serial_number = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date_shipped = db.Column(db.DateTime, default=datetime.utcnow)  # Track when it was shipped

    def __repr__(self):
        return f"<ShippedPart {self.part_number} - {self.serial_number}>"

# Define the DeliveryReceipt model
class DeliveryReceipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_number = db.Column(db.String(20), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    part_number = db.Column(db.String(50), nullable=False)
    serial_number = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_status = db.Column(db.String(20), nullable=False, default='pending')  # Track delivery status

    def __repr__(self):
        return f"DeliveryReceipt('{self.receipt_number}', '{self.customer_name}', '{self.date_created}')"

# Create the application context to create tables
with app.app_context():
    db.create_all()

# Define the SparePartForm class (used for creating and updating spare parts)
class SparePartForm(FlaskForm):
    part_number = StringField('Part Number', validators=[DataRequired()])
    serial_number = StringField('Serial Number', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('in stock', 'In Stock'),
        ('out for delivery', 'Out for Delivery'),
        ('returned', 'Returned'),
        ('dead on arrival', 'Dead on Arrival')
    ], validators=[DataRequired()])
    submit = SubmitField('Add Spare Part')

# Define the DeliveryReceiptForm class (used for creating delivery receipts)
class DeliveryReceiptForm(FlaskForm):
    customer_name = StringField('Customer Name', validators=[DataRequired()])
    part_number = StringField('Part Number', validators=[DataRequired()])
    serial_number = StringField('Serial Number', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    delivery_status = SelectField('Delivery Status', choices=[
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned')
    ], validators=[DataRequired()])
    submit = SubmitField('Create Delivery Receipt')

@app.route('/add_spare_part', methods=['POST'])
def add_spare_part():
    form = SparePartForm()
    if form.validate_on_submit():
        new_part = SparePart(
            part_number=form.part_number.data,
            serial_number=form.serial_number.data,
            quantity=form.quantity.data,
            status=form.status.data
        )
        db.session.add(new_part)
        db.session.commit()

        flash('Spare part added successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('add_spare_part.html', form=form)

@app.route('/', methods=['GET', 'POST'])
def home():
    form = SparePartForm()

    if form.validate_on_submit():
        new_part = SparePart(
            part_number=form.part_number.data,
            serial_number=form.serial_number.data,
            quantity=form.quantity.data,
            status=form.status.data
        )
        try:
            db.session.add(new_part)
            db.session.commit()

            flash('Spare part added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error adding spare part. Please try again.', 'danger')

        return redirect(url_for('home'))

    return render_template('home.html', form=form)  # Show only recent parts

@app.route('/check_spare_parts')
def check_spare_parts():
    parts = SparePart.query.all()
    logging.info(f'Retrieved parts: {parts}')  # Log the retrieved parts
    return render_template('check_spare_parts.html', parts=parts)

@app.route('/edit/<int:part_id>', methods=['GET', 'POST'])
def edit(part_id):
    part = SparePart.query.get_or_404(part_id)
    form = SparePartForm()

    if form.validate_on_submit():
        part.part_number = form.part_number.data
        part.serial_number = form.serial_number.data
        part.quantity = form.quantity.data
        part.status = form.status.data  # Update the status
        try:
            db.session.commit()
            logging.info(f'Spare part updated: {part}')
            flash('Spare part updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            logging.error(f'Error updating spare part: {e}')
            flash('Error updating spare part. Please try again.', 'danger')
        return redirect(url_for('check_spare_parts'))  # Redirect to the spare parts list

    form.part_number.data = part.part_number
    form.serial_number.data = part.serial_number
    form.quantity.data = part.quantity
    form.status.data = part.status  # Set the current status in the form
    return render_template('edit.html', form=form, part=part)  # Pass the part object to the template

@app.route('/delete/<int:part_id>', methods=['GET', 'POST'])
def delete(part_id):
    part = SparePart.query.get_or_404(part_id)
    try:
        # Now delete the SparePart
        db.session.delete(part)
        db.session.commit()
        logging.info(f'Spare part deleted: {part}')
        flash('Spare part deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error deleting spare part: {e}')
        flash('Error deleting spare part. Please try again.', 'danger')
    return redirect(url_for('check_spare_parts'))  # Redirect to check_spare_parts page

@app.route('/create_receipt', methods=['GET', 'POST'])
def create_receipt():
    form = DeliveryReceiptForm()
    if form.validate_on_submit():
        # Generate a random receipt number
        receipt_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        # Check if the part exists in the SparePart list
        part = SparePart.query.filter_by(serial_number=form.serial_number.data).first()
        if part and part.quantity > 0:
            # Create new delivery receipt object
            new_receipt = DeliveryReceipt(
                receipt_number=receipt_number,
                customer_name=form.customer_name.data,
                part_number=part.part_number,
                serial_number=part.serial_number,
                quantity=form.quantity.data,
                delivery_status=form.delivery_status.data  # Get the delivery status from the form
            )
            
            try:
                # Move the part to the ShippedPart list
                shipped_part = ShippedPart(
                    part_number=part.part_number,
                    serial_number=part.serial_number,
                    quantity=form.quantity.data
                )
                db.session.add(shipped_part)
                db.session.add(new_receipt)  # Add the new receipt to the session
                part.quantity -= form.quantity.data  # Decrease the quantity in SparePart
                db.session.commit()
                logging.info(f'Delivery Receipt created: {new_receipt}')
                print(f'Delivery Receipt created: {new_receipt}')  # Debugging statement
                flash(f"Delivery Receipt {receipt_number} created successfully!", 'success')
            except Exception as e:
                db.session.rollback()
                logging.error(f'Error creating delivery receipt: {e}')
                print(f'Error creating delivery receipt: {e}')  # Debugging statement
                flash('Error creating delivery receipt. Please try again.', 'danger')
        else:
            flash('Part not available for shipping.', 'danger')
        return redirect(url_for('view_receipts'))

    return render_template('create_receipt.html', form=form)

@app.route('/view_receipts')
def view_receipts():
    receipts = DeliveryReceipt.query.all()
    return render_template('view_receipts.html', receipts=receipts)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
