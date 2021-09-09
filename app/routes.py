# routes, url

from app import app


@app.route('/login')
def index():
    return "Hey S.H.I.F.T   ---- Login here"