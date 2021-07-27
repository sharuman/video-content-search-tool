from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/") 
def home(): 
    data = "VideoSearch"
    return render_template('index.html', data = data)

@app.route("/search", methods = ['POST'])
def search(): 
    print(request.form)
    return request.form['needle'] if request.form['needle'] is not '' else request.form['range']

app.run(debug = True)