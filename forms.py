from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SelectField, SubmitField, FloatField, FileField
from wtforms.validators import DataRequired
from country_list import countries_for_language
countries_dict = dict(countries_for_language("en"))
countries = [(key, value) for key, value in countries_dict.items()]


class Register(FlaskForm):
    f_name = StringField("First Name", validators=[DataRequired()])
    l_name = StringField("Last Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class Login(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class Checkout(FlaskForm):
    email = EmailField("Email")
    country = SelectField("Country", choices=countries, validators=[DataRequired()])
    f_name = StringField("First Name", validators=[DataRequired()])
    l_name = StringField("Last Name", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    postcode = StringField("Postcode", validators=[DataRequired()])


class AddItem(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    price = FloatField("Price", validators=[DataRequired()])
    image = FileField("Image")
    submit = SubmitField("Submit")
