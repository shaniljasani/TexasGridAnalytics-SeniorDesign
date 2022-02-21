from flask import Flask, render_template

app = Flask(__name__, static_url_path='', static_folder='')

@app.route("/")
def home():
    return render_template('index.html', my_var="yoooooo")


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5001)