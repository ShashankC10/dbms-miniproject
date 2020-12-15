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
start=""
destination=""
trainno=0
date1=datetime.datetime(1,1,1).strftime("%Y-%m-%d")
seatno=0
passengerno=0


@ui.route('/',methods=['GET','POST'])
def index():
    global start,destination
    if request.method=='POST':
        details=request.form
        start=details['start']
        destination=details['destination']
        return redirect('/selection')
    cur=mysql.connection.cursor()
    return render_template("task1.html")


@ui.route('/selection',methods=['GET','POST'])
def selection():
    global start,destination,trainno,date1
    if request.method=='POST':
        details=request.form
        trainno=details['trainno']
        date1=details['j_date']
        return redirect('/seats')
    cur=mysql.connection.cursor()
    result=cur.execute("select * from trainroute where route_no=(select route_no from route where start=%s and destination=%s)",(start,destination))
    if result>0:
        routedetails=cur.fetchall()
        return render_template('route.html',routedetails=routedetails)

@ui.route('/seats',methods=['GET','POST'])
def seatssel():
    global start,destination,trainno,date1,seatno,passengerno
    if request.method=='POST':
        details=request.form
        seatno=details['seatno']
        passengerno=details['passengerno']
        return redirect('/reserve')
    dt = str(datetime.datetime.strptime(date1, '%Y-%m-%d').date())
    cur=mysql.connection.cursor()
    seatsavailable=cur.execute("select t.trainno,s.seat_no,t.j_date from trainschedule t, seats s where t.trainno=%s and t.j_date=%s and s.seat_no not in(select r.seat_no from reservation r where r.train_no=%s and r.j_date=%s)",(trainno,dt,trainno,dt))
    if seatsavailable>0:
        seatavail=cur.fetchall()
        return render_template("seatdisp.html",seatavail=seatavail)
    

@ui.route('/reserve',methods=['GET','POST'])
def reserveseat():
    global start,destination,trainno,date1,seatno,passengerno,routeno
    dt = str(datetime.datetime.strptime(date1, '%Y-%m-%d').date())
    cur=mysql.connection.cursor()
    cur.execute("select route_no from route where start=%s and destination=%s",(start,destination))
    tb=cur.fetchone()
    for i in tb:
        routeno=str(i)
    if request.method=='POST':
        
        return "success"
    
    
    cur.execute("INSERT INTO railway_ticket_management.reservation (passenger_id, train_no, seat_no, j_date,route_no) VALUES (%s,%s,%s,%s,%s)",(passengerno,trainno,seatno,dt,routeno))
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
        passengername=details['name']
        phno=details['phno']
        address=details['address']
        age=details['age']
        gender=details['gender']
        cur.execute("INSERT INTO `railway_ticket_management`.`passenger` (`name`, `phonenumber`, `address`, `age`, `Gender`) VALUES (%s,%s,%s,%s,%s)",(passengername,phno,address,age,gender))
        mysql.connection.commit()
        cur.execute("select * from passenger")
        abc=cur.fetchall()
        for i in abc:
            a=1
            
        return "Your passenger id is:"+str(i[0])
    return render_template("registration.html")


if __name__=='__main__':
    ui.run(debug=True)