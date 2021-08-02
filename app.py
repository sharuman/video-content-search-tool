from flask import Flask, render_template, request
from database import MySQLConnection

app = Flask(__name__)

@app.route("/") 
def home(): 
    data = "VideoSearch"
    return render_template('index.html', data = data)

@app.route("/search", methods = ['GET'])
def search():
    needle = request.args.get('needle')
    confidence = request.args.get('confidence')
    
    with MySQLConnection(False) as mysql:
        cursor = mysql.connection.cursor()

        cursor.execute("SELECT * FROM keyframes \
            WHERE concept LIKE '%{}%' AND confidence >= {} \
            ORDER BY confidence DESC".format(needle, confidence))

        result = cursor.fetchall()

    return render_template('result.html', data = result)

app.run(debug = True)