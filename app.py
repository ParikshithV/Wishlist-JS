from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, insert, Unicode, DateTime
from datetime import datetime
import pytz
import time


import requests
from bs4 import BeautifulSoup

tz = pytz.timezone('Asia/Kolkata')
datetime_ind = datetime.now(tz)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wishlist.db'
app.secret_key = '696969'
db = SQLAlchemy(app)

meta = MetaData()

engine = create_engine('sqlite:///wishlist.db', echo = True)

class Wishlist(db.Model):
    name = db.Column(db.String, primary_key=True)
    link = db.Column(db.String)    #add nullable=False
    site_name = db.Column(db.String)
    image = db.Column(db.Unicode)
    price = db.Column(db.String, default=0)
    date_added = db.Column(db.DateTime, default=datetime_ind)

    def __repr__(self):
        return '<Item %r>' % self.id

class Users(db.Model):
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)    

    def __repr__(self):
        return '<Item %r>' % self.id


@app.route('/', methods=['POST','GET'])
def index():
    if 'username' in session:
        tables_dict = {table.__tablename__: table for table in db.Model.__subclasses__()}
        def table_object(table_name):
            return tables_dict.get(table_name)

        username = session['username']
        class Model(db.Model):
            __tablename__=username
            __table_args__ = {'extend_existing': True} 
            name = db.Column(db.String, primary_key=True)
            link = db.Column(db.String)    #add nullable=False
            site_name = db.Column(db.String)
            image = db.Column(db.Unicode)
            price = db.Column(db.String, default=0)
            date_added = db.Column(db.DateTime, default=datetime_ind)
        
        if request.method == 'POST':

            item_name = request.form['content']
            if 'streetstylestore' in item_name :
                try:
                    req = requests.get(item_name)
                    soup = BeautifulSoup(req.content,'html.parser')
                    price = soup.find('span',id="our_price_display").string
                    name = soup.find('h2', class_ = "product-name").string
                    image = soup.find_all('img')
                    image_link = image[2]['src']
                    time.sleep(3)
                    new_item = Model(name=name, link=item_name, site_name='SSS', image=image_link, price=price)

                    db.session.add(new_item)
                    db.session.commit()
                    return redirect('/')
                except:
                    return redirect('/')

            if 'bewakoof' in item_name :
                try:
                    req = requests.get('https://www.bewakoof.com/p/navy-blue-plain-full-sleeve-round-neck-men-t-shirt')
                    soup = BeautifulSoup(req.content,'html.parser')
                    price = soup.find('span', id = "testNetProdPrice").string
                    name = soup.find('h1', id = "testProName").string
                    image = soup.find_all('img')
                    image_link = image[2]['src']
                    time.sleep(3)
                    new_item = Model(name=name, link=item_name, site_name='Bewakoof', image=image_link, price=price)

                    db.session.add(new_item)
                    db.session.commit()
                    return redirect('/')
                except:
                    return redirect('/')


        
        else:
            items = Model.query.order_by(Model.date_added).all()
            return render_template('index.html', items=items)
    else:
        return redirect('/signin')

@app.route('/register', methods=['POST','GET'])
def register():

    usersdb = create_engine('sqlite:///wishlist.db', echo = True)
    meta = MetaData()

    users = Table(
        'users', meta, 
        Column('username', String, primary_key = True), 
        Column('password', String),
    )
    
    meta.create_all(usersdb)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Table(
            username, meta, 
            Column('name', String, primary_key=True),
            Column('link', String),    #add nullable=False
            Column('site_name', String),
            Column('image', Unicode),
            Column('price', String, default=0),
            Column('date_added', DateTime, default=datetime_ind),
        )
        meta.create_all(usersdb)

        try:
            if(bool(db.session.query(Users).filter_by(username=username).first())):
                return 'Try different username<br><a href="/register">Try again</a>'
            else:
                new_user = Users(username=username, password=password)

                db.session.add(new_user)
                db.session.commit()
                return render_template('signin.html')
            
        except:
            return 'Error in registration <br><a href="/register">Try again</a>'      
    else:
        return render_template('register.html')

@app.route('/signin', methods=['POST','GET'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if(bool(db.session.query(Users).filter_by(username=username).first())):
            if(bool(db.session.query(Users).filter_by(password=password).first())):
                session['username'] = username
                return redirect('/')
            else:
                return 'Wrong password <br><a href="/signin">Try again</a>'
        else:
            return 'User does not exist <br><a href="/signin">Try again</a>'
    else:
        return render_template('signin.html')
    
            

@app.route('/delete/<string:name>')
def delete(name):
    if 'username' in session:
        tables_dict = {table.__tablename__: table for table in db.Model.__subclasses__()}
        def table_object(table_name):
            return tables_dict.get(table_name)

        username = session['username']

        class Model(db.Model):
            __tablename__=username
            __table_args__ = {'extend_existing': True} 
            name = db.Column(db.String, primary_key=True)
            link = db.Column(db.String)    #add nullable=False
            site_name = db.Column(db.String)
            image = db.Column(db.Unicode)
            price = db.Column(db.String, default=0)
            date_added = db.Column(db.DateTime, default=datetime_ind)

        item_to_delete = Model.query.get_or_404(name)

        try:
            # Model.query.filter_by(name=name).delete()
            db.session.delete(item_to_delete)
            db.session.commit()
            return redirect('/')
        except:
            return 'Error deleting data'
    else:
        return redirect('/')      


@app.route('/update/<string:link>', methods=['GET', 'POST'])
def update(link):
    if 'username' in session:
        username = session['username']
        class Model(db.Model):
            __tablename__=username
            __table_args__ = {'extend_existing': True} 
            name = db.Column(db.String, primary_key=True)
            link = db.Column(db.String)    #add nullable=False
            site_name = db.Column(db.String)
            image = db.Column(db.Unicode)
            price = db.Column(db.String, default=0)
            date_added = db.Column(db.DateTime, default=datetime_ind)


        req = requests.get(link)
        soup = BeautifulSoup(req.content,'html.parser')
        price = soup.find('span',id="our_price_display").string


        session.query().\
        filter(Model.link == link).\
        update({"price": price})
        session.commit()


    else:
        return redirect('/signin')   


if __name__ == "__main__":
    app.run(debug=True)