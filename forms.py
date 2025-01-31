from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class SparePartForm(FlaskForm):
    part_number = StringField('Part Number', validators=[DataRequired()])
    serial_number = StringField('Serial Number', validators=[DataRequired()])
    quantity = IntegerField('Quantity', default=1, validators=[DataRequired()])
    status = SelectField('Status', choices=[('available', 'Available'), ('unavailable', 'Unavailable')], validators=[DataRequired()])
    submit = SubmitField('Add Spare Part')

class DeliveryReceiptForm(FlaskForm):
    receipt_number = StringField('Receipt Number', validators=[
        DataRequired(message='Receipt Number is required.'),
        Length(max=20, message='Receipt Number must be 20 characters or less.')
    ])
    customer_name = StringField('Customer Name', validators=[
        DataRequired(message='Customer Name is required.'),
        Length(max=100, message='Customer Name must be 100 characters or less.')
    ])
    part_number = StringField('Part Number', validators=[
        DataRequired(message='Part Number is required.'),
        Length(max=50, message='Part Number must be 50 characters or less.')
    ])
    serial_number = StringField('Serial Number', validators=[
        DataRequired(message='Serial Number is required.'),
        Length(max=50, message='Serial Number must be 50 characters or less.')
    ])
    quantity = IntegerField('Quantity', default=1, validators=[
        DataRequired(message='Quantity is required.'),
        NumberRange(min=1, message='Quantity must be at least 1.')
    ])
    delivery_status = SelectField('Delivery Status', choices=[
        ('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered')
    ], validators=[DataRequired()])
    submit = SubmitField('Create Delivery Receipt')
