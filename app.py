import datetime
import os
from flask import Flask, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

sparkx_db = os.getenv('SPARKXBIRTHDAYAPP_DATABASE_URI')
engine = create_engine(sparkx_db)

db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    today = datetime.datetime.today()
    todayString = f"{today.year}-{today.month}-{today.day}"
    today = datetime.datetime.strptime(todayString, "%Y-%m-%d")
    month = today.month
    day = today.day
    sparkx = db.execute("SELECT id, fname, lname, TO_CHAR(dob , 'Month') AS MONTH, TO_CHAR(dob, 'DD') AS DAY FROM sparkx WHERE EXTRACT(MONTH FROM dob) = :month AND EXTRACT(DAY FROM dob) = :day ORDER BY EXTRACT(MONTH FROM dob), DAY ASC", {"month": month, "day" : day}).fetchall()
    return render_template("index.html", sparkx = sparkx)

@app.route("/add-sparkx", methods=["GET", "POST"])
def addSparkx():
    fName = ""
    lName = ""

    addSuc = False
    if request.method == "POST":
        fName = request.form.get("fName")
        lName = request.form.get("lName")
        bDate = request.form.get("bDate")

        db.execute("INSERT INTO sparkx (fname,lname,dob) VALUES (:fName,:lName,:bDate)", {"fName": fName, "lName" : lName, "bDate": bDate}) 
        db.commit()
        addSuc = True

    return render_template("add-sparkx.html", addSuc = addSuc, fName = fName, lName = lName)


@app.route("/birthday-list", methods = ["GET", "POST"])
def bList():
    delSuc = False
    if request.method == "POST":
        delSuc = True
        fname = request.form.get("fName")
        lname = request.form.get("lName")

        spark = db.execute("SELECT id FROM sparkx WHERE LOWER(fname) = LOWER(:fname) AND LOWER(lname) = LOWER(:lname)", {"fname": fname, "lname": lname}).fetchone()
        if spark is None:
            return render_template("birthday-list.html", message = f"There is no sparkx where with the name: {fname} {lname}", delSuc = delSuc)
        else:
            delSpark = db.execute("DELETE FROM sparkx WHERE LOWER(fname) = LOWER(:fname) AND LOWER(lname) = LOWER(:lname)", {"fname": fname, "lname": lname})
            db.commit()
            return render_template("birthday-list.html", message = f"{fname} {lname} has been successfully removed.", delSuc = delSuc)
    sparkx = db.execute("SELECT id, fname, lname, TO_CHAR(dob , 'Month') AS MONTH, TO_CHAR(dob, 'DD') AS DAY FROM sparkx ORDER BY EXTRACT(MONTH FROM dob), DAY ASC").fetchall()
    
    return render_template("birthday-list.html", sparkx = sparkx, delSuc = delSuc)