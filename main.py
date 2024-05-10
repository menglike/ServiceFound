from flask import Flask,render_template

app = Flask(__name__)
app.debug = True

from controller.cloud import cloud
from lib.log import Log

app.register_blueprint(cloud)


@app.errorhandler(404)
def page_404(e):
    return  render_template('404.html'),404

@app.errorhandler(500)
def page_500(e):
    return  render_template('500.html'),500

@app.errorhandler(403)
def page_403(e):
    return  render_template('403.html'),403


app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'pythonisbest'

app.run("127.0.0.1",8888)

