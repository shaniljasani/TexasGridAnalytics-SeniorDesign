from flask import Flask, render_template, session, request, redirect, url_for

from resources.database import get_chart

app = Flask(__name__, static_url_path='', static_folder='')
app.secret_key = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
app.url_map.strict_slashes = False

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == 'POST':
        user = request.form.get("username")
        pw = request.form.get("password")

        if user == "FH10" and pw == "demo":
            session['id'] = user
            return redirect(url_for("home"))
        else:
            return render_template('login.html', message="Invalid username or password")
    else:
        return render_template('login.html')

@app.route("/")
def home():
    if session.get('id', None):
        return render_template('home.html')
    else:
        return render_template('login.html')

@appFlask.route('/index/', defaults={'subject' : 'Flask'})
@appFlask.route('/index/<subject>')

@app.route('/chart/<chart_type>/<start_date>/<end_date>')
def swd(chart_type, start_date, end_date):
    chart = get_chart(chart_type, start_date, end_date)
    if session.get('id', None):
        return render_template('swd.html', swd_data=chart['data'], swd_labels=chart['labels'])
    else:
        return render_template('login.html')


@app.errorhandler(404)
def FUN_404(error):
    return render_template("404.html"), 404

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5001)
