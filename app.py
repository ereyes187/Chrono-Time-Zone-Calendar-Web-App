from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user, login_required
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import CheckConstraint
from wtforms import SelectMultipleField
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user, login_required

from datetime import datetime, timedelta
import pytz

#flask --app app run   use this to run app
# http://127.0.0.1:5000/ # link to webaddress

app = Flask(__name__, static_url_path='/static')

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
app.config["SECRET_KEY"] = "mysecret"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    check = session.get('role', None)
    print(check, "this is check")
    if check == 'admin':
        print('admin query')
        return AdminLogin.query.get(int(user_id))
    else:
        print('user query')
        return User.query.get(int(user_id))


app.app_context().push() # without this, I recieve flask error


# databases

class AdminLogin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def get_id(self):
        return str(self.id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    inbox = db.relationship('Message', back_populates='sender', primaryjoin="User.id==Message.sender_id")
    sent = db.relationship('Message', back_populates='recipient', primaryjoin="User.id==Message.recipient_id")
    def __repr__(self):
        return self.email

    @property
    def is_active(self):
        # For simplicity, always consider the teacher account as active
        return True

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        # Replace with your authentication logic
        return True

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timeStart = db.Column(db.String(20), nullable=False)
    timeEnd = db.Column(db.String(20), nullable=False)
    allday = db.Column(db.Boolean, default=False )
    event = db.Column(db.String(20), nullable=False)
    url = db.Column(db.String(100), nullable=True)
    color = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('events', lazy=True))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender = db.relationship('User', back_populates='inbox', primaryjoin="User.id==Message.sender_id")
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient = db.relationship('User', back_populates='sent', primaryjoin="User.id==Message.recipient_id")

class UserView(ModelView):
    form_columns = ["email", "password"]
    column_list = ["id", "email", "password", "inbox", "sent"]

    #form_args = {
    #    'body': {
    #}

class AdminLoginView(ModelView):
    # def is_accessible(self):
        # return current_user.is_authenticated
    pass

class EventView(ModelView):
    pass
    # form_columns = ["date", "time", "event", "user"]
    # column_list = ["date", "time", "event", "user"]

    #form_args = {
    #    'body': {
    #}

class MessageView(ModelView):
    form_columns = ["body", "timestamp", "sender", "recipient"]
    column_list = ["body", "timestamp", "sender", "recipient"]

    #form_args = {
    #    'body': {
    #}

from flask import current_app

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):   #changing index to another name breaks admin permission access
        
        role = session.get('role', None)

        if current_user.is_authenticated:

            if role == 'admin':
                # Print the session role before redirecting
                return super(MyAdminIndexView, self).index()
            else:
                flash('You do not have permission to access this page.')
                return redirect(url_for('login'))

        else:
            flash('You have to login.')
            return redirect(url_for('login'))

admin = Admin(app, index_view=MyAdminIndexView())
 

admin.add_view(UserView(User, db.session))
admin.add_view(EventView(Event, db.session))
admin.add_view(MessageView(Message, db.session))
admin.add_view(AdminLoginView(AdminLogin, db.session))

@app.route('/')
def launch():
 return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
   return render_template('register.html')

@app.route('/run')
def run():
    return "<p>Is indeed running page</p>"

# Function to register a new user // can only register new students or teachers
@app.route('/register_backend', methods=['POST'])
def register_backend():

    name = request.form.get('new_name')
    email = request.form.get('new_email')
    password = request.form.get('new_password')

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        flash('Email is already registered, login:', 'login')
        return redirect(url_for("login"))

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    new_user = User(name = name, email=email, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    flash('Account created successfully!')
    return render_template('login.html')


@app.route("/login_backend", methods=["POST"])
def login_backend():

    Email = request.form['email']
    Password = request.form['password']

    if Email.endswith('@admin'):
        user = AdminLogin.query.filter_by(email=Email).first()
    else:
        user = User.query.filter_by(email=Email).first()

    # Check if the email ends with "@type" and assign role at login
    if user is not None:
        if not user.password.startswith('$pbkdf2'):

            if (user.password == Password):
                print("passed commited!")
                hashed_password = generate_password_hash(Password, method='pbkdf2:sha256')
                user.password = hashed_password
                db.session.commit()

        if check_password_hash(user.password, Password):

            if Email.endswith('@admin'):
                session['role'] = 'admin'
                login_user(user, remember=True)

                return redirect(url_for('admin.index'))

            else:
                session['role'] = 'student'
                session['id'] = user.id

                print(current_user)
                print(user.id)

                login_user(user, remember=True)


            return redirect(url_for('dashboard', id = user.id))

        else:
            flash('Password is incorrect: try again')
            return redirect(url_for("login"))

    else:
        flash('Email not found or invalid login credentials')
        return redirect(url_for("login"))


@app.route('/dashboard/<id>')
@login_required
def dashboard(id):
    # print(type(id), type(current_user.id) ) //id is a string, has to be passed as int() to work
    if current_user.id != int(id):
        abort(403)

    # check = session.get('id', None)

    # if id != check:
    #     flash('You do not have access to this page.')
    #     return abort(403) # Abort the request with a 403 Forbidden error

    return render_template('dashboard.html', user_id=id)


@app.route('/dashboard/calendar/<id>')
@login_required
def calendar(id):
    if current_user.id != int(id):
        abort(403)

    # check = session.get('id', None)

    # if id != check:
    #     flash('You do not have access to this page.')
    #     return abort(403) # Abort the request with a 403 Forbidden error

    return render_template('calendar.html', user_id=id)


@app.route('/dashboard/eventform/<id>')
@login_required
def eventform(id):
    if current_user.id != int(id):
        abort(403)

    # check = session.get('id', None)

    # if id != check:
    #     flash('You do not have access to this page.')
    #     return abort(403) # Abort the request with a 403 Forbidden error

    return render_template('event_form.html', user_id=id)



@app.route('/eventform_backend/<id>', methods=['POST'])
def eventform_backend(id):

    user = User.query.filter_by(id=id).first()

    if request.method == 'POST':
        event_name = request.form['event_name']

        event_start_date = request.form['event_start_date']
        event_start_time = request.form['event_start_time']

        event_end_date = request.form['event_end_date']
        event_end_time = request.form['event_end_time']

        url = request.form['url']
        color = request.form['color']

        # Check if the checkbox is checked using request.form.get
        is_all_day = request.form.get('checkButton') is not None

        timezone = request.form['timezone']

        start__ = datetime.strptime(f"{event_start_date} {event_start_time}", "%Y-%m-%d %H:%M")
        end__ = datetime.strptime(f"{event_end_date} {event_end_time}", "%Y-%m-%d %H:%M")

        if end__ < start__:
            flash('End date cannot be before start date.')
            print("Error: End date cannot be before the start date.")
            return render_template('event_form.html', user_id=id)

        print("inputed time: ",event_start_date, event_start_time)

        if timezone == 'new_york':
            # Convert the event_start_time to a datetime object
            start_datetime = datetime.strptime(f"{event_start_date} {event_start_time}", "%Y-%m-%d %H:%M")
            end_datetime = datetime.strptime(f"{event_end_date} {event_end_time}", "%Y-%m-%d %H:%M")

            # Subtract 3 hours from the datetime objects
            start_datetime -= timedelta(hours=3)
            end_datetime -= timedelta(hours=3)

            # Update event_start_date, event_start_time, and event_end_time with the modified values
            event_start_date = start_datetime.strftime("%Y-%m-%d")
            event_end_date = end_datetime.strftime("%Y-%m-%d")
            event_start_time = start_datetime.strftime("%H:%M")
            event_end_time = end_datetime.strftime("%H:%M")

            print("modified time: ", event_start_date, event_start_time, event_end_date, event_end_time)

        if timezone == 'tokyo':
            # Convert the event_start_time to a datetime object
            start_datetime = datetime.strptime(f"{event_start_date} {event_start_time}", "%Y-%m-%d %H:%M")
            end_datetime = datetime.strptime(f"{event_end_date} {event_end_time}", "%Y-%m-%d %H:%M")

            # Subtract 17 hours from the datetime objects
            start_datetime -= timedelta(hours=17)
            end_datetime -= timedelta(hours=17)

            # Normalize the datetime objects to ensure they are in the correct range
            start_datetime = start_datetime.replace(hour=int(start_datetime.strftime("%H")), minute=int(start_datetime.strftime("%M")))
            end_datetime = end_datetime.replace(hour=int(end_datetime.strftime("%H")), minute=int(end_datetime.strftime("%M")))

            # Update event_start_date, event_start_time, and event_end_time with the modified values
            event_start_date = start_datetime.strftime("%Y-%m-%d")
            event_end_date = end_datetime.strftime("%Y-%m-%d")
            event_start_time = start_datetime.strftime("%H:%M")
            event_end_time = end_datetime.strftime("%H:%M")

            print("modified time: ", event_start_date, event_start_time, event_end_date, event_end_time)


        # print(type(event_end_time), type(event_end_date))

        # print(is_all_day)
        # print(type(is_all_day)) # is a bool value

        # print(event_name, event_start_date, event_start_time)
        # print(event_end_date, event_end_time)
        # print(url, color)

        timeStart = event_start_date + 'T' + event_start_time

        if event_end_date != None and event_end_time != None :
            timeEnd = event_end_date + 'T' + event_end_time

        elif event_end_date != None and event_end_time == None:
            timeEnd = event_end_date

        else:
            timeEnd = ''

        print(timeStart)
        print(timeEnd)


            
        if is_all_day == False:
            new_event = Event(timeStart=timeStart, timeEnd=timeEnd, event=event_name, url=url, color=color, user_id=id)
        else:
            new_event = Event(timeStart=timeStart, timeEnd=timeEnd, allday=is_all_day, event=event_name, url=url, color=color, user_id=id)
        
        db.session.add(new_event)
        db.session.commit()
        flash('Event created successfully!')

        return redirect(url_for('calendar', id=id))

    return render_template('event_form.html', user_id=id)


@app.route('/get_events/<user_id>', methods=['GET'])
def get_events(user_id):
    events = Event.query.filter_by(user_id=user_id).all()
    event_list = []

    for event in events:
        event_list.append({
            'title': event.event,
            'start': event.timeStart,
            'end': event.timeEnd,
            'url': event.url,
            'color': event.color,
            'allDay' : event.allday,
        })

    return jsonify(event_list)


@app.route('/get_display/<id>', methods=['GET'])
def get_display(id):
    events = Event.query.filter_by(user_id=id).all()

    events_data = [{'id': event.id, 'name': event.event} for event in events]
    return jsonify({'events': events_data})


@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get(event_id)

    if event:
        db.session.delete(event)
        db.session.commit()

        flash('event deleted successfully')
        return jsonify({'message': 'Event deleted successfully'})
    else:
        return jsonify({'message': 'Event not found'}), 404



@app.route('/dashboard/messages/<id>')
@login_required
def messages(id):
    if current_user.id != int(id):
        abort(403)

    # check = session.get('id', None)

    # if id != check:
    #     flash('You do not have access to this page.')
    #     return abort(403) # Abort the request with a 403 Forbidden error


    user = User.query.get(id)
    sent_messages = Message.query.filter_by(sender_id=id).all()
    received_messages = Message.query.filter_by(recipient_id=id).all()
    if user:
        return render_template('messages.html', user_id=user.id , user_email=user.email, received_messages=received_messages, sent_messages=sent_messages, users=User.query.all())
    return "User not found."


@app.route('/dashboard/messages/<id>/<convo_id>', methods=['GET', 'POST'])
@login_required
def open_convo(id, convo_id):
    if current_user.id != int(id):
        abort(403)

    # check = session.get('id', None)

    # if id != check:
    #     flash('You do not have access to this page.')
    #     return abort(403) # Abort the request with a 403 Forbidden error

    user = User.query.get(id)
    sent_messages = Message.query.filter_by(sender_id=id).all()
    received_messages = Message.query.filter_by(recipient_id=id).all()
    return render_template('open_convo.html', user_id=user.id, user_email=user.email, convo_id=convo_id, received_messages=received_messages, sent_messages=sent_messages, users=User.query.all())


@app.route('/dashboard/messages/<id>/<convo_id>/reply', methods=['GET', 'POST'])
@login_required
def reply(id, convo_id):
    if request.method == 'POST':
        reply_text = request.form.get('reply')
        # print(id, convo_id)
        convo_user = User.query.filter_by(email=convo_id).first()

        new_msg = Message(body=reply_text, sender_id=id, recipient_id=convo_user.id)
        db.session.add(new_msg)
        db.session.commit()

        return redirect(url_for("open_convo", id=id, convo_id=convo_id))


# Routes for sending and viewing messages
@app.route('/dashboard/messages/<id>/send_message', methods=['GET', 'POST'])
@login_required
def send_message(id):
    user = User.query.get(id)
    email = request.form.get('email')
    body = request.form.get('body')

    existing_user = User.query.filter_by(email=email).first()

    if existing_user is None:
        flash('Email address does not exist in our database')
        return redirect(url_for("messages", id=user.id))
    if existing_user.email == user.email:
        flash('Can not send message to self')
        return redirect(url_for("messages", id=user.id))

    new_msg = Message(body=body, sender_id=id, recipient_id=existing_user.id)

    db.session.add(new_msg)
    db.session.commit()

    return redirect(url_for("open_convo", id=user.id, convo_id=existing_user))



@app.route('/logout')
@login_required
def logout():

    logout_user()
    session['id'] = None
    session['role'] = None

    flash('You have been successfully logged out.')
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)


# Notes 

#install//

# pip install blinker==1.6.2 click==8.1.6 Flask==2.3.2 Flask-Admin==1.6.1 Flask-SQLAlchemy==3.0.5 greenlet==2.0.2 itsdangerous==2.1.2 Jinja2==3.1.2 MarkupSafe==2.1.3 SQLAlchemy==2.0.19 typing_extensions==4.7.1 Werkzeug==2.3.6 WTForms==3.0.1 flask_login==23.2.1
# pip install flask-bcrypt
# pip install pytz


### how to delete or create db. type into terminal
#  flask shell
# >>>
# >>> from app import db
# >>> db.drop_all()
# >>> db.create_all()
# >>> exit()

# flask --app app run   use this to run app


### how to add in to database using terminal.
#>>> from app import app      use this to avoid error
#>>> from app import db
#>>> from app import User
#>>> user1 = User(studentName="student1",email="somethin@gmail" ,password="something",role="student")
#>>> db.session.add(user1)
#>>> db.session.commit()
#>>> user1 = User(studentName="student1",email="somethin@gmail" ,password="something",role="student")
#>>> db.session.add(user1)
#>>> db.session.commit()
