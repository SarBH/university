from flask import Flask, render_template
import sqlite3

DB_FILE = 'G:\My Drive\F18\SSW-810\Week 11\Homework11.db' #path of db file (from data grip, rightclick > properties)

app = Flask(__name__)

@app.route("/instructors")
def instructors():
    query = """select I.CWID, I.Name, I.Dept, G.Course, count(*) as StudentPerClass
    FROM HW11_instructors I
    join HW11_grades G
    on I.CWID = G.Instructor_CWID
    group by G.Course"""

    db = sqlite3.connect(DB_FILE) #load the database into db
    results = db.execute(query)
    
    #convert the query results into a list of dictionaries to pass to the template
    data = [{'cwid': cwid, 'name': name, 'dept': dept, 'course': course, 'StudentPerClass': StudentPerClass} for cwid, name, dept, course, StudentPerClass in results]

    db.close() #close the connection to the database

    return render_template('instructor_table.html', title='Instructors Summary', table_title='Number of students by class and instructor', instructors=data)

app.run(debug=True)