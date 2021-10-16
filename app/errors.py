# created by 
# 2021

from flask import render_template
from app import app, db


# HTTP Error 403 - Forbidden
@app.errorhandler(403)
def forbidden_error(error):
    return render_template('/errors/403.html'), 403

# HTTP Error 404 - Not Found
@app.errorhandler(404)
def not_found_error(error):
    return render_template('/errors/404.html'), 404

# HTTP Error 500 - Internal Server Error
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('/errors/500.html'), 500
