from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

# Initialize the Flask application
app = Flask(__name__)
# Set the secret key for session management
app.config['SECRET_KEY'] = 'your_secret_key'
# Configure the SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# Initialize SQLAlchemy for database management
db = SQLAlchemy(app)
# Initialize Flask-Login for user session management
login_manager = LoginManager()
login_manager.init_app(app)
# Set the login view for Flask-Login
login_manager.login_view = 'login'
# Initialize Flask-Bcrypt for password hashing
bcrypt = Bcrypt(app)

# Define the User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Define the user loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define the registration form using Flask-WTF
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    email = StringField(validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    # Custom validator to check if the username already exists
    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("That username already exists. Please choose a different one.")

# Define the login form using Flask-WTF
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

# Define the home route
@app.route('/')
def home():
    return render_template('index.html')

# Define the registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Hash the user's password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # Create a new user instance
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        # Log the user in
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html', form=form)

# Define the login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Query the user from the database
        user = User.query.filter_by(username=form.username.data).first()
        # Check if the user exists and the password is correct
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Log the user in
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

# Define the dashboard route (protected)
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

# Define the logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Run the application
if __name__ == '__main__':
    app.run(debug=True)