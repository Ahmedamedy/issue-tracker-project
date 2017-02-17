from flask import Flask, render_template, session, request, redirect, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, Issues, Users, CompanyUsers

engine = create_engine('sqlite:///issue-tracker.db')

Base.metadata.create_all(engine)
DBSession =  sessionmaker(bind=engine)
sessions = DBSession()

@app.route('/')
@app.route('/home')
def home():
    items = sessions.query(Issues).all()
    return render_template('home.html', items=items)


@app.route('/user/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        newuser = Users(username=request.form['name'], password=request.form['password'], email=request.form['email'])
        sessions.add(newuser)
        sessions.commit()
        return redirect(url_for('login'))
    else:
        return render_template('sign.html')

@app.route('/user/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
            if sessions.query(Users).filter_by(username =request.form['name'], password=request.form['password']).count() < 1:
                flash("Wrong Username or Password")
                return redirect(url_for('login'))
            else:
                session['username'] = request.form['name']
                user = sessions.query(Users).filter_by(username =request.form['name'], password=request.form['password']).one()
                session['id'] = user.id
                return redirect(url_for('issues'))
    else:
        return render_template('sign.html')
		

@app.route('/issues')
def issues():
    if 'username' in session:
        username = session['username']
	id = session['id']
        items = sessions.query(Issues).filter_by(user_id=id)
        return render_template('issues.html', items=items)
    else:
        return redirect(url_for('home'))
    

@app.route('/user/logout')
def logout():
   session.pop('username', None)
   return redirect(url_for('home'))
            
		
@app.route('/issue/new', methods=['GET','POST'])
def newissue():
    if request.method == 'POST':
        user_id = session['id']
        newuser = Issues(name=request.form['name'], description = request.form['description'], priority = request.form['priority'], department = request.form['department'],  assignned = False, opened = False, resolved = False,user_id= user_id)
        sessions.add(newuser)
        sessions.commit()
	flash("Issue Reported")
        return redirect(url_for('issues'))
    else:
        return render_template('newissue.html')	
		
@app.route('/admin/login', methods=['GET','POST'])
def adminlogin():
    if request.method == 'POST':
            if sessions.query(CompanyUsers).filter_by(username =request.form['username'], password=request.form['password'], designation=request.form['designation']).count() < 1:
                flash("Wrong Username or Password")
                return redirect(url_for('adminlogin'))
            else:
                session['username'] = request.form['username']
                user = sessions.query(CompanyUsers).filter_by(username =request.form['username'], password=request.form['password'], designation=request.form['designation']).one()
                session['id'] = user.id
				
                return redirect(url_for('adminissues'))
    else:
        return render_template('adminlogin.html')


@app.route('/admin/issues')
def adminissues():
    if 'username' in session:
        username = session['username']
        user_id = session['id']
	user = sessions.query(CompanyUsers).filter_by(id = user_id).one()
        items = sessions.query(Issues).filter_by(department=user.department)
        personel = sessions.query(CompanyUsers).filter_by(department=user.department, designation="personel")
        return render_template('adminissues.html', items=items, user = user, personel=personel)
    else:
        return redirect(url_for('home'))

@app.route('/admin/issues/opened')
def openedissues():
    if 'username' in session:
        username = session['username']
        user_id = session['id']
	user = sessions.query(CompanyUsers).filter_by(id = user_id).one()
        items = sessions.query(Issues).filter_by(department=user.department, opened = 0)
        personel = sessions.query(CompanyUsers).filter_by(department=user.department, designation="personel")
        return render_template('openedissues.html', items=items, user = user, personel=personel)
    else:
        return redirect(url_for('home'))
    
@app.route('/admin/issues/closed')
def closedissues():
    if 'username' in session:
        username = session['username']
        user_id = session['id']
	user = sessions.query(CompanyUsers).filter_by(id = user_id).one()
        items = sessions.query(Issues).filter_by(department=user.department, opened= 1)
        personel = sessions.query(CompanyUsers).filter_by(department=user.department, designation="personel")
        return render_template('closedissues.html', items=items, user = user, personel=personel)
    else:
        return redirect(url_for('home'))

@app.route('/admin/issues/high')
def highissues():
    if 'username' in session:
        username = session['username']
        user_id = session['id']
	user = sessions.query(CompanyUsers).filter_by(id = user_id).one()
        items = sessions.query(Issues).filter_by(department=user.department, priority = "High")
        personel = sessions.query(CompanyUsers).filter_by(department=user.department, designation="personel")
        return render_template('openedissues.html', items=items, user = user, personel=personel)
    else:
        return redirect(url_for('home'))

@app.route('/admin/issues/critical')
def criticalissues():
    if 'username' in session:
        username = session['username']
        user_id = session['id']
	user = sessions.query(CompanyUsers).filter_by(id = user_id).one()
        items = sessions.query(Issues).filter_by(department=user.department, priority = "Critial")
        personel = sessions.query(CompanyUsers).filter_by(department=user.department, designation="personel")
        return render_template('openedissues.html', items=items, user = user, personel=personel)
    else:
        return redirect(url_for('home'))
    

@app.route('/admin/comment/issue/<int:item_id>', methods=['GET','POST'])
def commentissue(item_id):
    editeditem = sessions.query(Issues).filter_by(id=item_id).one()
    if request.method == 'POST':
        remarks = request.form['remarks']
        editeditem.adminremarks = remarks
        sessions.add(editeditem)
        sessions.commit()
        flash("Comment Added")
        username = session['username']
        user_id = session['id']
	user = sessions.query(CompanyUsers).filter_by(id = user_id).one()
        items = sessions.query(Issues).filter_by(assignned=user.username)
        personel = sessions.query(CompanyUsers).filter_by(department=user.department, designation="personel")
        return redirect(url_for('adminissues'))
    else:
        username = session['username']
        user_id = session['id']
	user = sessions.query(CompanyUsers).filter_by(id = user_id).one()
        items = sessions.query(Issues).filter_by(department=user.department)
        personel = sessions.query(CompanyUsers).filter_by(department=user.department, designation="personel")
        return render_template('commentissue.html', item_id=item_id, i=editeditem, user = user, personel=personel )


    
@app.route('/admin/assign/issue/<int:item_id>', methods=['GET','POST'])
def assignissue(item_id):
    editeditem = sessions.query(Issues).filter_by(id=item_id).one()
    if request.method == 'POST':
        assignned = request.form['assign']
        editeditem.assignned = assignned
        sessions.add(editeditem)
        sessions.commit()
        flash("Issue Assigned")
        username = session['username']
        user_id = session['id']
	user = sessions.query(CompanyUsers).filter_by(id = user_id).one()
        items = sessions.query(Issues).filter_by(department=user.department)
        personel = sessions.query(CompanyUsers).filter_by(department=user.department, designation="personel")
        return redirect(url_for('adminissues'))
    else:
        username = session['username']
        user_id = session['id']
	user = sessions.query(CompanyUsers).filter_by(id = user_id).one()
        items = sessions.query(Issues).filter_by(department=user.department)
        personel = sessions.query(CompanyUsers).filter_by(department=user.department, designation="personel")
        return render_template('assignissue.html', item_id=item_id, i=editeditem, user = user, personel=personel )




@app.route('/admin/update/issue/<int:item_id>', methods=['GET','POST'])
def updateissue(item_id):
    editeditem = sessions.query(Issues).filter_by(id=item_id).one()
    if request.method == 'POST':
        resolved = request.form['resolved']
        editeditem.resolved = resolved
        sessions.add(editeditem)
        sessions.commit()
        flash("Issue updated")
        username = session['username']
        user_id = session['id']
	user = sessions.query(CompanyUsers).filter_by(id = user_id).one()
        items = sessions.query(Issues).filter_by(department=user.department)
        personel = sessions.query(CompanyUsers).filter_by(department=user.department)
        return redirect(url_for('adminissues'))
    else:
        username = session['username']
        user_id = session['id']
	user = sessions.query(CompanyUsers).filter_by(id = user_id).one()
        items = sessions.query(Issues).filter_by(department=user.department)
        personel = sessions.query(CompanyUsers).filter_by(department=user.department)
        return render_template('updateissue.html', item_id=item_id, i=editeditem, user = user, personel=personel )

@app.route('/staff/logout')
def stafflogout():
   session.pop('username', None)
   return redirect(url_for('stafflogin'))
   
		
@app.route('/staff/login', methods=['GET','POST'])
def stafflogin():
    if request.method == 'POST':
            if sessions.query(CompanyUsers).filter_by(username =request.form['username'], password=request.form['password']).count() < 1:
                flash("Wrong Username or Password")
                return redirect(url_for('stafflogin'))
            else:
                session['username'] = request.form['username']
                user = sessions.query(CompanyUsers).filter_by(username =request.form['username'], password=request.form['password']).one()
                if user.designation == "admin":
                    session['username'] = request.form['username']
                    user = sessions.query(CompanyUsers).filter_by(username =request.form['username'], password=request.form['password']).one()
                    session['id'] = user.id		
                    return redirect(url_for('adminissues'))
                else:
                    session['id'] = user.id
                    return redirect(url_for('staffissues'))             
    else:
        return render_template('stafflogin.html')


@app.route('/staff/issues')
def staffissues():
    if 'username' in session:
        username = session['username']
        user_id = session['id']
	user = sessions.query(CompanyUsers).filter_by(id = user_id).one()
        items = sessions.query(Issues).filter_by(assignned=user.username)
        return render_template('staffissues.html', items=items)
    else:
        return redirect(url_for('stafflogin'))

@app.route('/staff/update/issue/<int:item_id>', methods=['GET','POST'])
def staffupdateissue(item_id):
    editeditem = sessions.query(Issues).filter_by(id=item_id).one()
    if request.method == 'POST':
        comments = request.form['comments']
        editeditem.remarks = comments
        sessions.add(editeditem)
        sessions.commit()
        flash("Issue Updated")
        username = session['username']
        user_id = session['id']
	user = sessions.query(CompanyUsers).filter_by(id = user_id).one()
        items = sessions.query(Issues).filter_by(department=user.department)
        personel = sessions.query(CompanyUsers).filter_by(department=user.department)
        return redirect(url_for('staffissues'))
    else:
        username = session['username']
        user_id = session['id']
	user = sessions.query(CompanyUsers).filter_by(id = user_id).one()
        return render_template('staffupdateissue.html', item_id=item_id, i=editeditem )




if __name__ == '__main__':
    app.secret_key = "secret_key"
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)
