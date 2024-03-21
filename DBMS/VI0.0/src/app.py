from flask import Flask, render_template, request, redirect, session, make_response,url_for,flash
import mysql.connector  
import bcrypt
import datetime as dt
from datetime import date
import uuid

app = Flask(__name__)
app.secret_key = 'boost_is_the_secrect_to_my_energy'


mydb = mysql.connector.connect(                         #database connector
    host="localhost",
    user="root",
    password="GAGANKUMAR",
    port='3306',
    database="DBMS"  # Specify the database name here
)

# Login Table 
def create_user_reg():
    cursor = mydb.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                   userid INT AUTO_INCREMENT PRIMARY KEY,
                   username VARCHAR(225) NOT NULL,
                   password VARCHAR(225) NOT NULL)""")
    cursor.close()

# User info table
def create_user_info():
    cursor = mydb.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS user_info(
                    userid INT,
                    name VARCHAR(30) NOT NULL,
                    contact VARCHAR(50) NOT NULL,
                    FOREIGN KEY (userid) REFERENCES users(userid))""")
    cursor.close()

# Vehicle info table
def create_vehicle_info():
    cursor = mydb.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS vehicle_info(
                    vid INT AUTO_INCREMENT PRIMARY KEY,
                    userid INT,
                    VechNum VARCHAR(50) NOT NULL,
                    make_date DATE,
                    model VARCHAR(225) NOT NULL,
                    FOREIGN KEY (userid) REFERENCES users(userid))""")
    cursor.close()

# Insurance info table
def create_insurace_info():
    cursor = mydb.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS insurance_info(
                    iid INT AUTO_INCREMENT PRIMARY KEY,
                    userid INT,
                    vid INT,
                    months INT(3) NOT NULL,
                    expireDate DATE,
                    amount INT(10) NOT NULL,
                    provider VARCHAR(225) NOT NULL,
                    FOREIGN KEY (userid) REFERENCES users(userid),
                    FOREIGN KEY (vid) REFERENCES vehicle_info(vid))""")
    cursor.close()



#registration route
@app.route('/')
@app.route('/register', methods=['GET', 'POST'])
def register():
    create_user_reg()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            return 'Passwords do not match'

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor = mydb.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s , %s)", (username, hashed_password))
        mydb.commit()  # Commit changes to the database        
        cursor.close()

        return redirect('/info')
        flash('User registered successfully')
    return render_template('register.html')


#login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s ", (username,))

        user = cursor.fetchone()
        cursor.close()

        if user:
            if bcrypt.checkpw(password, user[2].encode('utf-8')):
                session['username'] = username
                flash('Logged in successfully')
                return redirect('/home')
            else:
                return 'Invalid username or password'

    return render_template('login.html')


#Info/register route
@app.route('/info', methods=['GET', 'POST'])
def info():
    create_user_info()
    create_vehicle_info()
    create_insurace_info()
   
    if request.method == "POST":
        cursor=mydb.cursor()
        #extract user info 
        
        name = request.form.get('name')
        contact = request.form.get('contact')
       
        #Insert User info
        
        cursor.execute("INSERT INTO user_info(userid,name,contact) VALUES(LAST_INSERT_ID(),%s,%s)",(name,contact))               
        #Extract Vehicle info
        
        VN=request.form.get('vehicleNumber')
        Mfd=request.form.get('manufactureDate')
        model=request.form.get('model')
        #Insert Vechicle info
        cursor.execute("INSERT INTO vehicle_info(userid,VechNum,make_date,model) VALUES(LAST_INSERT_ID(),%s,%s,%s)",(VN,Mfd,model))
        
       #Extract insurance info
        
        months=request.form.get('duration')
        amount=request.form.get('amount')
        policy=request.form.get('policyProvider')
        exp=request.form.get('expireDate')
        #Insert Insurance info
        cursor.execute("INSERT INTO insurance_info(userid,vid,months,expireDate,amount,provider) VALUES(LAST_INSERT_ID(),LAST_INSERT_ID(),%s,%s,%s,%s)",(months,exp,amount,policy))
        mydb.commit() 
        cursor.close()

        return redirect('/login')   

    return render_template('info.html')

#Home Page route
@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html')
    return redirect('/login')

#Profile page where all information are displayed
@app.route('/profile',methods=['GET', 'POST'])
def profile():

    if 'username' in session:
        username = session.get('username')
        print(username)
        with mydb.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT userid FROM users WHERE username = %s", (username,))
            user_id_row = cursor.fetchone()
            print(user_id_row)
            if user_id_row:
                user_id = user_id_row['userid']
                int(user_id)
                print(user_id)
                cursor.execute("SELECT * FROM user_info WHERE userid = %s", (user_id,))
                row_user = cursor.fetchone()
                print(row_user)
                cursor.execute("SELECT * FROM vehicle_info WHERE userid = %s", (user_id,))
                row_vehicle = cursor.fetchall()
                print(row_vehicle)
                cursor.execute("SELECT * FROM insurance_info WHERE userid = %s", (user_id,))
                row_insurance = cursor.fetchall()
                print(row_insurance)
                cursor.execute("SELECT expireDate FROM insurance_info WHERE userid=%s",(user_id,))
                indate_row = cursor.fetchall()
                
                today = date.today()
                for idate in indate_row:
                    if idate:
                            indate = idate['expireDate']
                            today = date.today()
                            if indate <= today:
                                flash('Your insurance has expired. Please update your insurance information !!!')

                

    return render_template('profile.html', row_user=row_user, row_vehicle=row_vehicle, row_insurance=row_insurance)

    
#Update user information
@app.route('/UserUpdate',methods=['GET', 'POST'])
def UserUpdate():
    if 'username' in session:
        if request.method=="POST":
            username = session.get('username')
            with mydb.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT userid FROM users WHERE username = %s", (username,))
                user_id_row = cursor.fetchone()
                if user_id_row:
                    user_id = user_id_row['userid']
                    name=request.form.get('name')
                    contact=request.form.get('contact')
                    cursor.execute("UPDATE user_info SET name=%s,contact=%s WHERE userid=%s",(name,contact,user_id))
                    mydb.commit() 
                    cursor.close()
                    flash('User Information Updated !!!')
                    return redirect('/profile')
        
        return render_template('UserUpdate.html')
#Update Vehicle Information   
@app.route('/VehicleUpdate',methods=['GET', 'POST'])
def VehicleUpdate():
    if 'username' in session:
        if request.method=="POST":
            username = session.get('username')
            with mydb.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT userid FROM users WHERE username = %s", (username,))
                user_id_row = cursor.fetchone()
                if user_id_row:
                    user_id = user_id_row['userid']
                    vnum=request.form.get('vehicleNumber')
                    Mfd=request.form.get('manufactureDate')
                    model=request.form.get('model')
                    cursor.execute("UPDATE vehicle_info SET VechNum=%s,make_date=%s,model=%s WHERE userid=%s",(vnum,Mfd,model,user_id))
                    mydb.commit() 
                    cursor.close()
                    flash('Vehicle Information Updated !!!')
                    return redirect('/profile')
        
        return render_template('VehicleUpdate.html')
    
#Update Insurance Inforamtion
@app.route('/InsuranceUpdate',methods=['GET', 'POST'])
def InsuranceUpdate():
    if 'username' in session:
        if request.method=="POST":
            username = session.get('username')
            with mydb.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT userid FROM users WHERE username = %s", (username,))
                user_id_row = cursor.fetchone()
                if user_id_row:
                    user_id = user_id_row['userid']
                    months=request.form.get('duration')
                    amount=request.form.get('amount')
                    policy=request.form.get('policyProvider')
                    exp=request.form.get('expireDate')
                    cursor.execute("UPDATE insurance_info SET months=%s,expireDate=%s,amount=%s,provider=%s WHERE userid=%s",(months,exp,amount,policy,user_id))
                    mydb.commit() 
                    cursor.close()
                    flash('Insurance Information Updated !!!')
                    return redirect('/profile')
        
        return render_template('InsuranceUpdate.html')

#Add new Vehicle       
@app.route('/NewVehicle',methods=['GET', 'POST'])            
def NewVehicle():
      if 'username' in session:
        if request.method=="POST":
            username = session.get('username')
            with mydb.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT userid FROM users WHERE username = %s", (username,))
                user_id_row = cursor.fetchone()
                if user_id_row:
                    user_id = user_id_row['userid']
                    vnum=request.form.get('vehicleNumber')
                    Mfd=request.form.get('manufactureDate')
                    model=request.form.get('model')
                    months=request.form.get('duration')
                    amount=request.form.get('amount')
                    policy=request.form.get('policyProvider')
                    exp=request.form.get('expireDate')
                    cursor.execute("""INSERT INTO vehicle_info(userid,VechNum,make_date,model) VALUES(%s,%s,%s,%s)
                                   """,(user_id,vnum,Mfd,model))
                    cursor.execute("""INSERT INTO insurance_info(userid,vid,months,expireDate,amount,provider) 
                                   VALUES(%s,LAST_INSERT_ID(),%s,%s,%s,%s)""",(user_id,months,exp,amount,policy))
                    mydb.commit() 
                    cursor.close()
                    flash('New Vehicle Added !')
                    return redirect('/profile')
        return render_template('NewVehicle.html')

#delete the user
@app.route('/DeleteUser',methods=['GET', 'POST'])
def DeleteUser():
      if 'username' in session:
        if request.method=="POST":
            username = session.get('username')
            with mydb.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT userid FROM users WHERE username = %s", (username,))
                user_id_row = cursor.fetchone()
                if user_id_row:
                     user_id = user_id_row['userid']
                     username = request.form['username']
                     password = request.form['password'].encode('utf-8')
                     cursor = mydb.cursor()
                     cursor.execute("SELECT * FROM users WHERE username = %s ", (username,))
                     user = cursor.fetchone()
                     if user:
                        if bcrypt.checkpw(password, user[2].encode('utf-8')):
                            session['username'] = username
                            cursor.execute("""DELETE FROM insurance_info WHERE userid=%s""",(user_id,))
                            cursor.execute("""DELETE FROM vehicle_info WHERE userid=%s""",(user_id,))
                            cursor.execute("""DELETE FROM user_info WHERE userid=%s""",(user_id,))
                            cursor.execute("""DELETE FROM users WHERE userid=%s""",(user_id,))
                            mydb.commit() 
                            cursor.close()
                            return redirect('/login')
                        
        return render_template('DeleteUser.html')
                     

                    




@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login')+ '?_={}'.format(uuid.uuid4()))



if __name__ == '__main__':
    app.run(debug=True)

