from kanado import Kanado
from kanado import render_template

app = Kanado(__name__)


@app.route('/kami')
def home():
    return render_template("home.html")


