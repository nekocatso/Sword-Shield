from flask import Flask, render_template

app = Flask(__name__)

@app.route("/0")
def index_0():
    return render_template("0.html")

@app.route("/1")
def index_1():
    return render_template("1.html")

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)