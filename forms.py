from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

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
