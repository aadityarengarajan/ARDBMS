from flask import *
from products import *
from flask import g, session
import secrets
from datetime import datetime
import csv
import math
import pandas
import stripe

app = Flask(__name__)
app.secret_key = str(secrets.token_urlsafe(16))
stripe.api_key = stripe_keys['secret_key']

aptcsvnames=['id','ident','type','name','latitude_deg','longitude_deg','elevation_ft','continent','iso_country','iso_region','municipality','scheduled_service','gps_code','iata_code','local_code','home_link','wikipedia_link','keywords']

def aptnamelatlon(icao):
    readrows=[]
    with open('airports.csv', newline='', encoding='utf-8') as apts:
        for i in csv.reader(apts, delimiter = "\t"):
            if str(i[1]).upper()==str(icao).upper():
                alist=[i[3],i[4],i[5]]
                return alist
            else:
                continue
        return [0,0,0]

def getdist(dpt,arr):
    R = 6373.0
    lat1 = math.radians(float(aptnamelatlon(dpt)[1]))
    lon1 = math.radians(float(aptnamelatlon(dpt)[2]))
    lat2 = math.radians(float(aptnamelatlon(arr)[1]))
    lon2 = math.radians(float(aptnamelatlon(arr)[2]))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def nametoicao(name):
    with open('airports.csv', newline='', encoding='utf-8') as apts:
        for i in csv.reader(apts, delimiter = "\t"):
             if str(i[10]).upper()==str(name).upper():
                return str(i[1]).upper()
             else:
                continue
        return 0

def icaotoname(icao):
    with open('airports.csv', newline='', encoding='utf-8') as apts:
        for i in csv.reader(apts, delimiter = "\t"):
            if str(i[1]).upper()==str(name).upper():
                return str(i[10]).upper()
            else:
                continue
        return 0

def citylist():
    listt=pandas.read_csv('airports.csv', sep='\t', encoding='latin-1', header=None, index_col=0, quotechar="'", names=aptcsvnames, skiprows=1)
    return listt







@app.route('/')
def homepage():
    return render_template('entry.html',products=products)

@app.route('/shop')
def shop():
    from flask import g, session
    session['code']=secrets.token_urlsafe(4)
    session['cart']=list('')
    return render_template('products.html',products=products)

@app.route('/billgen')
def billgen():
    from flask import g, session
    prod = request.args.get('jsdata')
    cart=session.get('cart')
    cost=None
    for i in products:
        if i['title']==prod:
            cost=i['cost']
    if cost==None:
        for i in products:
            if i['title']==prod.replace('--rem--',''):
                cost=i['cost']
    if '--rem--' in prod:
        cart.remove(({'prod':prod.replace('--rem--',''),'cost':cost}))
    else:
        cart.append({'prod':prod,'cost':cost})
    session['cart']=cart
    cart=[]
    return render_template('cart.html',cart=session.get('cart'),code=session.get('code'),date=(datetime.now().strftime('%d/%m/%Y')))

@app.route('/checkout')
def checkout():
    from flask import g, session
    return render_template('checkout.html',cities=citylist(),cart=session.get('cart'),key=stripe_keys['publishable_key'],seller_name=seller_name)

@app.route('/delchargen')
def delchargen():
    from flask import g, session
    to = request.args['jsdata']
    to = nametoicao(to)
    frm = source
    dist = getdist(frm,to)
    delcost = 0.01*dist
    delcost = round(delcost,2)
    return str(delcost)

@app.route('/finalizepayment')
def finalizepayment():

    amount = 500

    customer = stripe.Customer.create(
        email='sample@customer.com',
        source=request.form['stripeToken']
    )

    stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Flask Charge'
    )

    return render_template('checkout.html', amount=amount)

app.run()