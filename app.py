from flask import Flask, render_template, Response
from main import Video
from flask import Flask , flash , redirect , url_for, session, logging
from flask.globals import request
#from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField , validators,SubmitField, RadioField, SelectField, IntegerField
from passlib.hash import sha256_crypt
from functools import wraps
from wtforms import validators, ValidationError
import qrcode 
import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas








app=Flask(__name__)



# Confing MYSQL

app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] ='root'
app.config['MYSQL_PASSWORD'] ='1234'
app.config['MYSQL_DB'] ='qr_atendencedb'
app.config['MYSQL_CURSORCLASS'] ='DictCursor'

#init MYSQL
mysql = MySQL(app)



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/atendence')
def weather_dashboard():
    filename = 'Attendence.csv'
    data = pandas.read_csv(filename, header=0)
    #myData = data.values
    myData= data.values
    return render_template('atendence.html', myData=myData)

# About
@app.route('/about')
def about():
    return render_template ('about.html')



# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password',[
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])

    confirm = PasswordField('Confirm Password')
# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()
        # Execute query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        #Commit to DB
        mysql.connection.commit()

        # close connection
        cur.close()

        flash('You are now registered and can log in','success')
        redirect(url_for('index'))
    return render_template('register.html', form=form)



#User login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method== 'POST':
        #Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        #Create cursor
        cur = mysql.connection.cursor()

        #Get user by username
        result = cur.execute("SELECT * FROM users WHERE username =%s", [username])

        if result > 0:
            #Get stored hash
            data = cur.fetchone()
            password = data['password']

            #Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in']= True
                session['username']= username

                flash('You are now logges in', 'success')
                return  redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')
# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


#Dashboard
@app.route('/atendence')
@is_logged_in
def atendence():
 #Create cursor
        cur = mysql.connection.cursor()

        #Get articles 
        result = cur.execute("SELECT * FROM add_student")

        add_student = cur.fetchall()
        

        if result > 0:
            return render_template('atendence.html',add_student=add_student)
        else:
            msg = 'No Atendences Found'
            return render_template('dashboard.html', msg=msg)

        # Close connection
        cur.close()

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

#Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    #Create cursor
    cur = mysql.connection.cursor()

    #Get articles 
    result = cur.execute("SELECT * FROM add_student")

    add_student = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html',add_student=add_student)
    else:
        msg = 'No Students Found'
        return render_template('dashboard.html', msg=msg)

    # Close connection
    cur.close()

# Student Register Form Class
class stu_RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    Gender = RadioField('Gender', choices = [('M','Male'),('F','Female')])  
    Address = TextAreaField("Address") 
    Age = IntegerField("Age")  
    language = SelectField('Programming Languages', choices = [('java', 'Java'),('py', 'Python')])   
    email = StringField('Email', [validators.Length(min=6, max=50)])
   
    

    
    
@app.route('/add_student', methods=['GET', 'POST'])
@is_logged_in
def add_student():
    form = stu_RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
            name = form.name.data
            email = form.email.data
            Gender = form.Gender.data
            Age = form.Age.data
            language = form.language.data
           

            # Create cursor
            cur = mysql.connection.cursor()
            # Execute query
            cur.execute("INSERT INTO add_student (name, email, gender, age, language ) VALUES(%s, %s, %s, %s, %s)", (name, email, Gender, Age , language))

            #Commit to DB
            mysql.connection.commit()

            # close connection
            cur.close()
            img = qrcode.make(email)
            img.save(email +'.'+'jpg')



            subject = "An email with attachment from #System"
            body = "This is an email with attachment sent from Student Managment Systems"
            sender_email = ""
            receiver_email = email
            password = ""


            # Create a multipart message and set headers
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email
            message["Subject"] = subject
            message["Bcc"] = receiver_email  # Recommended for mass emails

            # Add body to email
            message.attach(MIMEText(body, "plain"))

            filename = email +'.'+'jpg'  # In same directory as script

            # Open PDF file in binary mode
            with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

                # Encode file in ASCII characters to send by email    
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
                 )

            # Add attachment to message and convert message to string
            message.attach(part)
            text = message.as_string()

            # Log in to server using secure context and send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, text)

            

            flash('You are now registered and sent a QR code to you. Check your email box','success')
            return redirect(url_for('dashboard'))
    return render_template('add_student.html', form=form)

class stu_edit(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    Gender = RadioField('Gender', choices = [('M','Male'),('F','Female')])  
    
    Age = IntegerField("Age")  
    language = SelectField('Programming Languages', choices = [('java', 'Java'),('py', 'Python')])   
    email = StringField('Email', [validators.Length(min=6, max=50)])

@app.route('/edit_student/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_student(id):
    #Creat cursar

    cur = mysql.connection.cursor()
    #Get user by id
    result= cur.execute("SELECT * FROM add_student WHERE id =%s", [id])

    add_student = cur.fetchone()


    form = stu_edit(request.form)

    form.name.data = add_student['name']
    form.Gender.data =  add_student['gender']
   
    form.Age.data = add_student['age']
    form.language.data =  add_student['language']
    form.email.data =  add_student['email']


    if request.method == 'POST' and form.validate():
        name = request.form['name']
        gender = request.form['Gender']
        
        age = request.form['Age']
        language = request.form['language']
        email = request.form['email']

        # Create Cursor
        cur = mysql.connection.cursor()
        app.logger.info(name)
        
        

        # Execute

        cur.execute("UPDATE add_student SET name= %s, email=%s , gender=%s, age=%s, language=%s WHERE id = %s", (name, email,gender, age, language ,id))

        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('Student Update', 'succes')

        return redirect(url_for('dashboard'))
    return render_template('edit_student.html', form=form)

#Delete
@app.route('/delete_student/<string:id>', methods= ['POST'])
@is_logged_in
def delete_article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    #Execute

    cur.execute("DELETE FROM add_student WHERE id = %s",[id])

    # Commit to DB
    mysql.connection.commit()

    #Close connection
    cur.close()

    flash('Article Deleted','success')

    return redirect(url_for('dashboard'))     

@app.route('/QR')
def index():
    return render_template('QR.html')

def gen(camera):
    while True:
        frame=camera.get_frame()
        yield(b'--frame\r\n'
       b'Content-Type:  image/jpeg\r\n\r\n' + frame +
         b'\r\n\r\n')

@app.route('/video')

def video():
    return Response(gen(Video()),
    mimetype='multipart/x-mixed-replace; boundary=frame')




if __name__ == '__main__':
   app.secret_key='secret123'
   app.run(debug=True)
