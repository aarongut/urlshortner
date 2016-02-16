from flask import Flask, request, redirect, url_for
import redis
from urllib import quote_plus

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

    if (f == None or t == None):
        return redirect(url_for('static', filename='new.html'))

    f = quote_plus(f)
    t = quote_plus(t)

    print "I found:", r.get(f)
    if (r.get(f) != None):
        return redirect(url_for('static', filename='error.html'))

    r.set(quote_plus(f), 'http://' + quote_plus(t))

    url = url_for('link', l=f)
    return '<html><body><a href="' + url + '">http://delt.space' + url + '</a>'

@app.route('/<l>')
def link(l=None):
    page = r.get(l)

    if page == None:
        return redirect('/')
    
    return redirect(page)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
