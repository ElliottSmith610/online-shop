from flask import *
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from forms import Register, Login, Checkout

app = Flask(__name__)
Bootstrap(app)
app.config["SECRET_KEY"] = "Banana"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///online-shop.db"
db = SQLAlchemy(app)


class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(200), nullable=False)
    l_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    ## Any relationships ##
    # link to a cart db? #


class Items(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    form = Checkout()
    return render_template("index.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    register_form = Register()
    if register_form.validate_on_submit():
        new_user = Users()
        new_user.f_name = register_form.f_name.data
        new_user.l_name = register_form.l_name.data
        new_user.email = register_form.email.data
        new_password = generate_password_hash(
            register_form.password.data,
            method="pbkdf2:sha256",
            salt_length=8,
            )
        new_user.password = new_password
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("login.html", form=register_form)


@app.route("/login", methods=["GET", "POST"])
def login():
    login_form = Login()
    if login_form.validate_on_submit():

        email = login_form.email.data
        if Users.query.filter_by(email=email).first():
            print("Yay")
        else:
            print("Nay")

    return render_template("login.html", form=login_form)


# @login_required
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/cart", methods=["GET", "POST"])
def cart():
    pass


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    pass


if __name__ == "__main__":
    app.run(debug=True)
