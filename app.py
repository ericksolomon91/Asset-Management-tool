from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import string
import os
import logging
import pandas as pd
from flask import send_file
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

# Create the Flask app
app = Flask(__name__)

# PostgreSQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myapp_user:password@vm_ip-address/myapp_db' # Update with your database URI!!!!
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_default_secret_key')

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define the SparePart model
class SparePart(db.Model):
    __tablename__ = 'spare_parts' 

    id = db.Column(db.Integer, primary_key=True)  
    part_number = db.Column(db.String(100), nullable=False)
    part_name = db.Column(db.String(100), nullable=False) 
    serial_number = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<SparePart {self.part_number} - {self.serial_number}>"

# Define the ShippedPart model
class ShippedPart(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    part_number = db.Column(db.String(50), nullable=False)
    serial_number = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date_shipped = db.Column(db.DateTime, default=datetime.utcnow)  

    def __repr__(self):
        return f"<ShippedPart {self.part_number} - {self.serial_number}>"

# Define the DeliveryReceipt model
class DeliveryReceipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_number = db.Column(db.String(20), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    part_number = db.Column(db.String(50), nullable=False)
    part_name = db.Column(db.String(100), nullable=False)  
    serial_number = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_status = db.Column(db.String(20), nullable=False, default='PENDING') 

    def __repr__(self):
        return f"DeliveryReceipt('{self.receipt_number}', '{self.customer_name}', '{self.date_created}')"

# Create the application context to create tables
with app.app_context():
    db.create_all()

# Define the SparePartForm class (used for creating and updating spare parts)
class SparePartForm(FlaskForm):
    part_number = StringField('Part Number', validators=[DataRequired()])
    part_name = StringField('Part Name', validators=[DataRequired()])  
    serial_number = StringField('Serial Number', validators=[DataRequired()])
    quantity = IntegerField('Quantity', default=1, validators=[DataRequired()])
    status = SelectField('Status', choices=[('warehouse', 'Warehouse'), ('doa', 'DOA(defect)'), ('returned', 'Returned')], validators=[DataRequired()])
    submit = SubmitField('Add Spare Part')

# Define the DeliveryReceiptForm class (used for creating delivery receipts)
class DeliveryReceiptForm(FlaskForm):
    customer_name = StringField('Customer Name', validators=[DataRequired()])
    part_number = StringField('Part Number', validators=[DataRequired()])
    part_name = StringField('Part Name', validators=[DataRequired()])  
    serial_number = StringField('Serial Number', validators=[DataRequired()])
    quantity = IntegerField('Quantity', default=1, validators=[DataRequired(), NumberRange(min=1)])
    delivery_status = SelectField('Delivery Status', choices=[('PENDING', 'Pending'), ('SENT OUT', 'Sent Out'), ('DELIVERED', 'Delivered')], validators=[DataRequired()])
    submit = SubmitField('Create Delivery Receipt')

@app.route('/import_spare_parts', methods=['POST'])
def import_spare_parts():
    file = request.files['file']
    if file and file.filename.endswith('.csv'):
        try:
            df = pd.read_csv(file)
            for index, row in df.iterrows():
                status = row['status'].upper()
                if status not in ['WAREHOUSE', 'DOA(DEFECT)', 'RETURNED']:
                    status = 'WAREHOUSE' 

                new_part = SparePart(
                    part_number=row['part_number'],
                    part_name=row['part_name'],
                    serial_number=row['serial_number'],
                    quantity=row['quantity'],
                    status=status
                )
                db.session.add(new_part)
            db.session.commit()
            flash('Spare parts imported successfully!', 'success')
        except Exception as e:
            logging.error(f'Error importing spare parts: {e}')
            flash('An error occurred while importing spare parts. Please check the logs.', 'danger')
    else:
        flash('Invalid file format. Please upload a CSV file.', 'danger')
    return redirect(url_for('home'))

@app.route('/export_spare_parts', methods=['GET'])
def export_spare_parts():
    parts = SparePart.query.all()
    data = [{
        'part_number': part.part_number,
        'part_name': part.part_name,
        'serial_number': part.serial_number,
        'quantity': part.quantity,
        'status': part.status
    } for part in parts]
    df = pd.DataFrame(data)
    csv_file = 'spare_parts_list.csv'
    df.to_csv(csv_file, index=False)
    return send_file(csv_file, as_attachment=True)

@app.route('/add_spare_part', methods=['POST'])
def add_spare_part():
    form = SparePartForm()
    if form.validate_on_submit():
        new_part = SparePart(
            part_number=form.part_number.data,
            part_name=form.part_name.data, 
            serial_number=form.serial_number.data,
            quantity=form.quantity.data,
            status=form.status.data
        )
        db.session.add(new_part)
        db.session.commit()

        flash('Spare part added successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('home.html', form=form) 

@app.route('/', methods=['GET', 'POST'])
def home():
    form = SparePartForm()
    parts = SparePart.query.order_by(SparePart.id.desc()).limit(1).all()

    if form.validate_on_submit():
        new_part = SparePart(
            part_number=form.part_number.data,
            part_name=form.part_name.data,
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

    return render_template('home.html', form=form, parts=parts) 

@app.route('/check_spare_parts', methods=['GET'])
def check_spare_parts():
    search_query = request.args.get('search')
    if search_query:
        parts = SparePart.query.filter(
            (SparePart.part_number.ilike(f'%{search_query}%')) |
            (SparePart.part_name.ilike(f'%{search_query}%'))
        ).all()
    else:
        parts = SparePart.query.all()
    
    logging.info(f'Retrieved parts: {parts}')  
    return render_template('check_spare_parts.html', parts=parts)

@app.route('/edit/<int:part_id>', methods=['GET', 'POST'])
def edit(part_id):
    part = SparePart.query.get_or_404(part_id)
    form = SparePartForm()

    if form.validate_on_submit():
        part.part_number = form.part_number.data
        part.part_name = form.part_name.data 
        part.serial_number = form.serial_number.data
        part.quantity = form.quantity.data
        part.status = form.status.data  
        try:
            db.session.commit()
            logging.info(f'Spare part updated: {part}')
            flash('Spare part updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            logging.error(f'Error updating spare part: {e}')
            flash('Error updating spare part. Please try again.', 'danger')
        return redirect(url_for('check_spare_parts')) 

    form.part_number.data = part.part_number
    form.part_name.data = part.part_name  
    form.serial_number.data = part.serial_number
    form.quantity.data = part.quantity
    form.status.data = part.status  
    return render_template('edit.html', form=form, part=part) 

@app.route('/delete/<int:part_id>', methods=['GET', 'POST'])
def delete(part_id):
    part = SparePart.query.get_or_404(part_id)
    try:
        db.session.delete(part)
        db.session.commit()
        logging.info(f'Spare part deleted: {part}')
        flash('Spare part deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error deleting spare part: {e}')
        flash('Error deleting spare part. Please try again.', 'danger')
    return redirect(url_for('check_spare_parts')) 

@app.route('/create_receipt', methods=['GET', 'POST'])
def create_receipt():
    form = DeliveryReceiptForm()
    if form.validate_on_submit():
        receipt_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        # Check if the part exists in the SparePart list
        part = SparePart.query.filter_by(serial_number=form.serial_number.data).first()
        if part and part.quantity > 0:
            new_receipt = DeliveryReceipt(
                receipt_number=receipt_number,
                customer_name=form.customer_name.data,
                part_number=part.part_number,
                part_name=part.part_name, 
                serial_number=part.serial_number,
                quantity=form.quantity.data,
                delivery_status=form.delivery_status.data 
            )
            
            try:
                shipped_part = ShippedPart(
                    part_number=part.part_number,
                    serial_number=part.serial_number,
                    quantity=form.quantity.data
                )
                db.session.add(shipped_part)
                db.session.add(new_receipt) 
                part.status = "SENT-OUT" 
                part.quantity = 0  
                db.session.commit()
                logging.info(f'Delivery Receipt created: {new_receipt}')
                print(f'Delivery Receipt created: {new_receipt}')  
                flash(f"Delivery Receipt {receipt_number} created successfully!", 'success')
            except Exception as e:
                db.session.rollback()
                logging.error(f'Error creating delivery receipt: {e}')
                print(f'Error creating delivery receipt: {e}')  
                flash('Error creating delivery receipt. Please try again.', 'danger')
        else:
            flash('Part not available for shipping.', 'danger')
        return redirect(url_for('view_receipts'))
    
    if request.method == 'GET':
        part_number = request.args.get('part_number')
        part_name = request.args.get('part_name')
        serial_number = request.args.get('serial_number')
        if part_number and part_name and serial_number:
            form.part_number.data = part_number
            form.part_name.data = part_name
            form.serial_number.data = serial_number
            form.quantity.data = 1

    return render_template('create_receipt.html', form=form)

@app.route('/view_receipts')
def view_receipts():
    receipts = DeliveryReceipt.query.all()
    return render_template('view_receipts.html', receipts=receipts)

@app.route('/view_receipt/<int:receipt_id>', methods=['GET'])
def view_receipt(receipt_id):
    receipt = DeliveryReceipt.query.get_or_404(receipt_id)
    return render_template('receipt_template.html', receipt=receipt)

@app.route('/download_receipt/<int:receipt_id>', methods=['GET'])
def download_receipt(receipt_id):
    receipt = DeliveryReceipt.query.get_or_404(receipt_id)
    return render_template('receipt_template.html', receipt=receipt)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
