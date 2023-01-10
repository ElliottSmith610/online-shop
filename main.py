from functools import wraps

from flask import *
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
import stripe

from forms import Register, Login, Checkout, AddItem

app = Flask(__name__)
Bootstrap(app)
app.config["SECRET_KEY"] = "Banana"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///online-shop.db"
db = SQLAlchemy(app)

YOUR_DOMAIN = 'http://localhost:5000'
stripe.api_key = 'sk_test_51MOejpBxBcQVHvbytRuQOfCZqP4SMs3WOeCS9tYL8VzKUZZGJXNJnS4wFejUU6WJODH77U9QZfc9BYr3XSJENTft00mlCd3P8L'
product_list = stripe.Product.list()

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            admin = current_user.admin
        except AttributeError:
            return redirect(url_for("home"))
        else:
            if admin:
                return func(*args, **kwargs)
            else:
                return redirect(url_for("home"))

    return wrapper


class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(200), nullable=False)
    l_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    admin = db.Column(db.Boolean, nullable=True)

    ## Any relationships ##
    # link to a cart db? #

    def is_admin(self):
        return {column.name: str(getattr(self, column.name)) for column in self.__table__.columns
                if column.name != "password"}


class Items(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    price = db.Column(db.Float(9), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    def to_dict(self):
        return {column.name: str(getattr(self, column.name)) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    # items_query = db.session.query(Items).all()
    # items = [item.to_dict() for item in items_query]
    return render_template("index.html", items=product_list)


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

        if not Users.query.filter_by(admin=True).first():
            # Sets first user as default admin
            new_user.admin = True
        else:
            new_user.admin = False

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
        user = Users.query.filter_by(email=email).first()
        if not user:
            # Email not found, either incorrect or doesn't exist
            print("Wrong Email")
        elif not check_password_hash(user.password, login_form.password.data):
            # incorrect password
            print("Wrong Pass")
        else:
            print("wewlad")
            login_user(user)
            return redirect(url_for("home"))

    return render_template("login.html", form=login_form)


# @login_required
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/to_cart/<item_name>", methods=["GET", "POST"])
def to_cart(item_name):
    try:
        if not session["cart"]:
            pass
    except KeyError:
        session["cart"] = {}
    if item_name in session["cart"]:
        session["cart"][item_name] += 1
    else:
        session["cart"][item_name] = 1
    session.modified = True
    return redirect(url_for("home"))


@app.route("/from_cart/<item_name>", methods=["GET", "POST"])
def from_cart(item_name):
    session["cart"].pop(item_name)
    session.modified = True
    return redirect(url_for("cart"))


@app.route("/cart", methods=["GET", "POST"])
def cart():
    try:
        _cart = session["cart"]
    except KeyError:
        _cart = None
        total_price = None
    else:
        items_query = db.session.query(Items).all()
        items = [item.to_dict() for item in items_query if item.name in session["cart"]]
        session["total_price"] = 0
        for item in items:
            session["total_price"] += float(item["price"]) * session["cart"][item["name"]]
    return render_template("cart.html", cart=_cart, price=session["total_price"])


@app.route("/create-checkout-session", methods=["GET", "POST"])
def create_checkout_session():
    line_items = []
    for key, value in session["cart"].items():
        for item in product_list:
            if item.name == key:
                _dict = {"price": item.default_price, "quantity": value}
                line_items.append(_dict)
    print(line_items)
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items
            # [
            # {
            #     # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
            #     'price': 'pr_12345',
            #     'quantity': 1,
            # },
            # ]
            ,
            mode='payment',
            success_url=YOUR_DOMAIN + '/success',
            cancel_url=YOUR_DOMAIN + '/cancel',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)


@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/cancel")
def cancel():
    return render_template("cancel.html")


@app.route("/users", methods=["GET", "POST"])
@admin_only
def users():
    user_list_query = db.session.query(Users).all()
    user_list = [user.is_admin() for user in user_list_query]
    return render_template("users.html", users=user_list)


@app.route("/add", methods=["GET", "POST"])
@admin_only
def add_item():
    add_form = AddItem()
    if add_form.validate_on_submit():
        # new_item = Items()
        # new_item.name = add_form.name.data
        # new_item.price = add_form.price.data
        # new_item.description = add_form.description.data
        # image = Image.open(add_form.image.data).convert('RGB')
        # image.save(f"./static/items/{add_form.name.data}.jpg")
        # new_item.img_url = f'items/{add_form.name.data}.jpg'
        # db.session.add(new_item)
        # db.session.commit()

        ## Stripe
        stripe.Product.create(name=add_form.name.data, description=add_form.description.data,
                              metadata={"price": add_form.price.data},
                              default_price_data={"currency": "GBP",
                                                  "unit_amount_decimal": round(add_form.price.data * 100), })
        global product_list
        product_list = stripe.Product.list()
        return redirect(url_for('add_item'))
    return render_template("login.html", form=add_form)


if __name__ == "__main__":
    app.run(debug=True)
