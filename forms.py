from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, MultipleFileField, SubmitField
from wtforms.validators import DataRequired
from wtforms import IntegerField
year = IntegerField('Year', validators=[DataRequired()])
from flask_wtf.file import FileAllowed




class CarForm(FlaskForm):
    name = StringField('Car Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    images = MultipleFileField('Upload Images')
    submit = SubmitField('Submit')
    submit = SubmitField('Add Car')
    images = MultipleFileField('Car Images', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])





