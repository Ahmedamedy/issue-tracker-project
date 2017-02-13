from flask import Flask, render_template, session, request, redirect, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Issues, Users

engine = create_engine('sqlite:///issue-tracker.db')

Base.metadata.create_all(engine)
DBSession =  sessionmaker(bind=engine)
sessions = DBSession()

@app.route('/')
@app.route('/home')
def home():
    items = sessions.query(Issues).all()
    return render_template('home.html', items=items)


@app.route('/user/new', methods=['GET','POST'])
def newuser():
    if request.method == 'POST':
        newuser = Users(username=request.form['name'], password=request.form['password'], email=request.form['email'])
        sessions.add(newuser)
        sessions.commit()
        return redirect(url_for('home'))
    else:
        return render_template('newuser.html')

@app.route('/user/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        session['Username'] = request.form['name']
        user = sessions.query(Users).filter_by(username =request.form['name'], password=request.form['password']).one()
        session['id'] = user.id
        return redirect(url_for('issues'))
    else:
        return render_template('login.html')
		

@app.route('/issues')
def issues():
    if 'Username' in session:
        username = session['Username']
        items = sessions.query(Issues).all()
        return render_template('issues.html', items=items)
    else:
        return redirect(url_for('home'))
    

@app.route('/user/logout')
def logout():
   session.pop('username', None)
   return redirect(url_for('login'))
            
		
@app.route('/issue/new', methods=['GET','POST'])
def newissue():
    if request.method == 'POST':
        user_id = session['id']
        newuser = Issues(name=request.form['name'], description = request.form['description'], user_id= user_id)
        sessions.add(newuser)
        sessions.commit()
        return redirect(url_for('issues'))
    else:
        return render_template('newissue.html')	
        
if __name__ == '__main__':
    app.secret_key = "secret_key"
    app.debug = True
    app.run(host ='0.0.0.0', port=8000)
