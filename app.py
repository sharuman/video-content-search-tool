from flask import Flask, render_template

app = Flask(__name__) 

@app.route("/") 
def home(): 
    data = "Codeloop"
    return render_template('index.html', data = data)

app.run(debug = True)