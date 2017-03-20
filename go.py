from flask import Flask, request, redirect, url_for
import redis
from urllib import quote_plus, unquote
import logging
from logging.handlers import RotatingFileHandler
from key import secret
import requests

app = Flask(__name__)

app.debug = True

r = redis.StrictRedis(host='localhost', port=6379, db=0)

@app.route('/')
def home():
    return redirect(url_for('static', filename='new.html'))

@app.route('/new', methods=['GET'])
def new_link():
    f = request.args.get('from', None)
    t = request.args.get('to', None)

    if (f == None or t == None or f == "" or t == ""):
        return redirect(url_for('static', filename='new.html'))

    f = quote_plus(f)

    if (r.get(f) != None):
        return redirect(url_for('static', filename='error.html'))

    data = {
        'secret': secret,
        'response': request.args.get('g-recaptcha-response'),
        'remoteip': request.environ.get('REMOTE_ADDR'),
    }


    verify = requests.get('https://www.google.com/recaptcha/api/siteverify',
                          params=data)

    if not (verify.status_code == 200 and verify.json()['success']):
        app.logger.info('SPAM: ' + request.environ.get('REMOTE_ADDR'))
        return redirect(url_for('static', filename='spam.html'))


    ssl = t[:5].lower() == 'https'

    t = t.split('https://')[-1].split('http://')[-1]

    protocol = 'https://' if ssl else 'http://'
    r.set(quote_plus(f), protocol + quote_plus(t))

    url = url_for('link', l=f)
    app.logger.info('NEW: ' + url + ' -> ' + t)
    return '<html><body><a href="' + url + '">http://delt.space' + url + '</a>'

@app.route('/<l>')
def link(l=None):
    page = r.get(quote_plus(l))

    if page == None:
        if l[-1] == 's' and r.get(l[:-1]):
            app.logger.info('RICK: ' + l + ' -> https://www.youtube.com/watch?v=dQw4w9WgXcQ')
            return redirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        return redirect('/')

    app.logger.info('GET: ' + l + ' -> ' + unquote(page))
    return redirect(unquote(page))

if __name__ == '__main__':
    handler = RotatingFileHandler('go.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=8080)
