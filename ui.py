from flask import Flask,render_template,request,redirect
from flask_mysqldb import MySQL
import yaml
import datetime
ui=Flask(__name__)
mysql=MySQL(ui)

db=yaml.load(open('db.yaml'))

#for confidentiality of database credentials
ui.config['MYSQL_HOST']=db['mysql_host']
ui.config['MYSQL_USER']=db['mysql_user']
ui.config['MYSQL_PASSWORD']=db['mysql_password']
ui.config['MYSQL_DB']=db['mysql_db']
mail_id=""
start=""
destination=""
trainno=0
date1=datetime.datetime(1,1,1).strftime("%Y-%m-%d")
seatno=0

@ui.route('/',methods=['GET','POST'])
def index():
    cur=mysql.connection.cursor()
    global mail_id
    if request.method=='POST':
        details=request.form
        mail_id1=str(details['email'])
        password=details['password']
        print((mail_id1))
        authenticate=cur.execute("select mail_id,password from user where mail_id=%s",[mail_id1])
        if authenticate>0:
            password1=cur.fetchone()
            password_orig=password1[1]
            if password==password_orig:
                mail_id=mail_id1
                return redirect('/places')
    
    return render_template("home.html")

@ui.route('/places',methods=['GET','POST'])
def startdest():
    global start,destination
    if request.method=='POST':
        details=request.form
        start=details['start']
        destination=details['destination']
        return redirect('/selection')
    return render_template('task1.html')

@ui.route('/selection',methods=['GET','POST'])
def selection():
    global start,destination,trainno,date1
    if request.method=='POST':
        details=request.form
        trainno=details['trainno']
        date1=details['j_date']
        return redirect('/seats')
    cur=mysql.connection.cursor()
    result=cur.execute("select * from trainroute where route_no=(select route_no from route where start=%s and destination=%s)",([start],[destination]))
    if result>0:
        routedetails=cur.fetchall()
        return render_template('route.html',routedetails=routedetails)

@ui.route('/seats',methods=['GET','POST'])
def seatssel():
    global start,destination,trainno,date1,seatno
    if request.method=='POST':
        details=request.form
        seatno=details['seat']
        return redirect('/reserve')
    dt = str(datetime.datetime.strptime(date1, '%Y-%m-%d').date())
    cur=mysql.connection.cursor()
    seatsavailable=cur.execute("select t.trainno,s.seat_no,t.j_date from trainschedule t, seats s where t.trainno=%s and t.j_date=%s and s.seat_no not in(select r.seat_no from reservation r where r.train_no=%s and r.j_date=%s)",(trainno,dt,trainno,dt))
    if seatsavailable>0:
        seatavail=cur.fetchall()
        return render_template("seatdisp.html",seatavail=seatavail)
    

@ui.route('/reserve',methods=['GET','POST'])
def reserveseat():
    global start,destination,trainno,date1,seatno,mail_id,routeno
    dt = str(datetime.datetime.strptime(date1, '%Y-%m-%d').date())
    cur=mysql.connection.cursor()
    cur.execute("select route_no from route where start=%s and destination=%s",(start,destination))
    tb=cur.fetchone()
    for i in tb:
        routeno=str(i)
    if request.method=='POST':
        
        return redirect('/places')
    
    
    cur.execute("INSERT INTO railway_ticket_management.reservation (mail_id, train_no, seat_no, j_date,route_no) VALUES (%s,%s,%s,%s,%s)",(mail_id,trainno,seatno,dt,routeno))
    mysql.connection.commit()
    currec=cur.execute("select * from reservation r where train_no=%s and seat_no=%s and j_date=%s",(trainno,seatno,dt))
    if currec>0:
        seatbooked=cur.fetchall()
        return render_template("reservation.html",seatbooked=seatbooked)

@ui.route('/registration',methods=['GET','POST'])
def register():
    cur=mysql.connection.cursor()

    if request.method=='POST':
        details=request.form
        username=details['name']
        mail_id=str(details['email'])
        password=details['password']
        phno=details['phno']
        address=details['address']
        age=str(details['age'])
        cur.execute("INSERT INTO `railway_ticket_management`.`user` (`mail_id`, `name`, `age`, `phno`, `password`, `address`) VALUES (%s, %s, %s, %s, %s, %s)",(mail_id,username,age,phno,password,address))
        mysql.connection.commit()
            
        return redirect('/')
    return render_template("registration.html")

@ui.route('/cancel',methods=['GET','POST'])
def cancellation():
    global mail_id
    cur=mysql.connection.cursor()
    if request.method=='POST':
        details=request.form
        seat=str(details['seat'])
        trainno=str(details['trainno'])
        date1=details['j_date']
        route=str(details['route'])
        dt = str(datetime.datetime.strptime(date1, '%Y-%m-%d').date())
        cur.execute("delete from reservation where seat_no=%s and train_no=%s and route_no=%s and j_date=%s",(seat,trainno,route,dt))
        mysql.connection.commit()
        return redirect('/places')
    tups=cur.execute("select * from reservation where mail_id=%s",[mail_id])
    if tups>0:
        seatsbooked=cur.fetchall()
    return render_template("cancellation.html",seats=seatsbooked)
if __name__=='__main__':
    ui.run(debug=True)