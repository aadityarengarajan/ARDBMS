from flask import redirect, render_template, Flask, request, url_for, send_file
import msal,random
import app_config
from flask_session import Session
import uuid
import datetime
import hashdict
import os
import pickle
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import csv,startup
from artistconfig import *

def usersdblist():
	usersdb = {}
	for i in os.listdir('usersdb'):
		with open(f'./usersdb/{i}') as f:
			try:
				name=f.readlines()[0].replace('NAME,','').replace('\n','')
				usersdb.update({str(name):str(i)})
			except:
				with open(f'./usersdb/{i}','a') as f:
					f.write('FAULTY USER')
	return usersdb

app = Flask(__name__)
app.config.from_object(app_config)
Session(app)


def Message(subject,recipient,text):
        sender_email = "vortex.artistmgmt@gmail.com"
        receiver_email = recipient
        password = 'vortexsynaptics'
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = receiver_email
        part = MIMEText(text, "plain")
        message.attach(part)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )

# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone/#proxy-setups
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


@app.route('/')
def home():
	from flask import g,session
	if not session.get('loggedin'):
		session['loggedin']=False
	if session.get('loggedin')==False:
		return redirect(url_for('signup'))
	else:
		return redirect(url_for('loginuser'))

@app.route("/signup")
def signup():
    from flask import g, session
    session["state"] = str(uuid.uuid4())
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    auth_url = _build_auth_url(scopes=app_config.SCOPE, state=session["state"])
    return render_template("login.html", artist=artistconfig['artist'], auth_url=auth_url, version=msal.__version__)

@app.route(app_config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    from flask import g, session

    if request.args.get('state') != session.get("state"):
        return redirect(url_for("home"))  # No-OP. Goes back to Index page
    if "error" in request.args:  # Authentication/Authorization failure
        return render_template("auth_error.html", result=request.args)
    if request.args.get('code'):
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_authorization_code(
            request.args['code'],
            scopes=app_config.SCOPE,  # Misspelled scope would cause an HTTP 400 error here
            redirect_uri=url_for("authorized", _external=True))
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    session['username']=str(session['user'].get('preferred_username')).replace("@live.com",'').replace('@outlook.com','').replace('@hotmail.com','').replace('@gmail.com','').replace('@','').replace('.com','')
    session['name']=session['username']
    return redirect(url_for('loginuser'))

@app.route("/logout")
def logout():
    from flask import g, session

    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("home", _external=True))

def _load_cache():
    from flask import g, session

    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    from flask import g, session

    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def _build_msal_app(cache=None, authority=None):
    from flask import g, session

    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)

def _build_auth_url(authority=None, scopes=None, state=None):
    from flask import g, session

    return _build_msal_app(authority=authority).get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=url_for("authorized", _external=True))

def _get_token_from_cache(scope=None):
    from flask import g, session

    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result

@app.route('/signup/submit')
def loginuser():
	from flask import g,session
	if session.get('loggedin')!=True:
		for i in usersdblist().keys():
			if {session.get('username')}==i:
				with open(f"./usersdb/{usersdblist()[str(session.get('name'))]}") as f:
					lines = f.readlines()
					session['name']=lines[0].split(',')[1]
					session['email']=lines[1].split(',')[1]
					session['memberid']=lines[2].split(',')[1]
					session['datejoined']=lines[3].split(',')[1]
					session['timejoined']=lines[4].split(',')[1]
					session['city']=lines[5].split(',')[1]
					session['instagram']=lines[6].split(',')[1]
					session['facebook']=lines[7].split(',')[1]
					session['twitter']=lines[8].split(',')[1]
					session['whatsapp']=lines[9].split(',')[1]
					session['spotify']=lines[10].split(',')[1]
					session['donated']=lines[11].split(',')[1]
					session['officialmerchandise']=lines[12].split(',')[1]
					session['totalmessageactivity']=lines[13].split(',')[1]
					session['artistmessageactivity']=lines[14].split(',')[1]
					session['topstreamer']=lines[15].split(',')[1]
					session['pmdate']=lines[16].split(',')[1]
					session['theme']=lines[17].split(',')[1]
				session['loggedin']=True
				return redirect(url_for('dashboard'))
	return render_template('completesignup.html')

@app.route('/signup/complete', methods = ['POST'])
def completesignup():
	from flask import g,session
	memid = str(uuid.uuid4()).split('-')[0]
	session['memiddddd'] = memid
	with open(f"./usersdb/{memid}.preferences",'w') as f:
		f.write(f'''NAME,{session.get('username')}
E-MAIL,{str(session.get("user").get("preferred_username"))}
MEMBER ID,{memid}
DATE JOINED,{str((datetime.datetime.now().strftime('%d/%m/%Y')))}
TIME JOINED,{str((datetime.datetime.now().strftime('%H:%M:%S')))}
CITY,{request.form['city']}
INSTAGRAM,{request.form['instagram']}
FACEBOOK,{request.form['facebook']}
TWITTER,{request.form['twitter']}
WHATSAPP,{request.form['whatsapp']}
SPOTIFY,{request.form['spotify']}
DONATED,0
OFFICIAL MERCHANDISE,False
TOTAL MESSAGE ACTIVITY,0
ARTIST MESSAGE ACTIVITY,0
TOP STREAMER,False
PM DATE,{str((datetime.datetime.now().strftime('%d/%m/%Y')))}
THEME,{request.form['theme']}''')
	session['memberid']= memid
	with open(f"./usersdb/{session['memberid']}.preferences") as f:
		lines = f.readlines()
		session['name']=lines[0].replace('NAME,','').replace('\n','')
		session['email']=lines[1].replace('E-MAIL,','').replace('\n','')
		session['memberid']=lines[2].replace('MEMBER ID,','').replace('\n','')
		session['datejoined']=lines[3].replace('DATE JOINED,','').replace('\n','')
		session['timejoined']=lines[4].replace('TIME JOINED,','').replace('\n','')
		session['city']=lines[5].replace('CITY,','').replace('\n','')
		session['instagram']=lines[6].replace('INSTAGRAM,','').replace('\n','')
		session['facebook']=lines[7].replace('FACEBOOK,','').replace('\n','')
		session['twitter']=lines[8].replace('TWITTER,','').replace('\n','')
		session['whatsapp']=lines[9].replace('WHATSAPP,','').replace('\n','')
		session['spotify']=lines[10].replace('SPOTIFY,','').replace('\n','')
		session['donated']=lines[11].replace('DONATED,','').replace('\n','')
		session['officialmerchandise']=lines[12].replace('OFFICIAL MERCHANDISE,','').replace('\n','')
		session['totalmessageactivity']=lines[13].replace('TOTAL MESSAGE ACTIVITY,','').replace('\n','')
		session['artistmessageactivity']=lines[14].replace('ARTIST MESSAGE ACTIVITY,','').replace('\n','')
		session['topstreamer']=lines[15].replace('TOP STREAMER,','').replace('\n','')
		session['pmdate']=lines[16].replace('PM DATE,','').replace('\n','')
		session['theme']=lines[17].replace('THEME,','').replace('\n','')
	os.remove(f"./usersdb/{session['memberid']}.preferences")
	
	code = random.choice(artistconfig['verification-codes'].replace('\n','').split(',')).replace(' ','')
	msg = Message(subject="Vortex Fan Verification",
                  recipient=str(session.get("user").get("preferred_username")),
                  text=f"Enter '{code}' to verify yourself at {artistconfig['artist']['name']}'s fanbase signup :-)")
	session['verification-code'] = hashdict.hash(code)
	return render_template('verify.html',code=hashdict.hash(code))

@app.route('/signup/hashapi/<code>')
def hashapi(code):
	from flask import g,session
	if session['verification-code'] == hashdict.hash(code):
		return 'Verified'
	return 'Wrong'

@app.route('/signup/verified')
def verifiedsignup():
	from flask import g,session
	with open(f"./usersdb/{session.get('memiddddd')}.preferences",'w') as f:
		f.write(f'''NAME,{session.get('name')}
E-MAIL,{session.get('email')}
MEMBER ID,{session.get('memberid')}
DATE JOINED,{session.get('datejoined')}
TIME JOINED,{session.get('timejoined')}
CITY,{session.get('city')}
INSTAGRAM,{session.get('instagram')}
FACEBOOK,{session.get('facebook')}
TWITTER,{session.get('twitter')}
WHATSAPP,{session.get('whatsapp')}
SPOTIFY,{session.get('spotify')}
DONATED,0
OFFICIAL MERCHANDISE,False
TOTAL MESSAGE ACTIVITY,0
ARTIST MESSAGE ACTIVITY,0
TOP STREAMER,False
PM DATE,{session.get('donated')}
THEME,{session.get('theme')}''')
	return redirect(url_for('dashboard'))

@app.route('/fan/community')
def communitychat():
	from flask import g,session
	return render_template('communitychat.html')

@app.route('/fan/community/update/<message>',methods=['POST'])
def updatecommunity(message):
	from flask import g,session
	with open('./chatsdb/community.bin','rb') as binfile:
		data = pickle.load(binfile)
	data.append({'sender':session.get('username'),'message':message,'date':{str((datetime.datetime.now().strftime('%d/%m/%Y')))},'time':{str((datetime.datetime.now().strftime('%H:%M:%S')))}})
	with open('./chatsdb/community.bin','wb') as binfile:
		pickle.dump(binfile,data)
	return '200'

@app.route('/fan/community/retreive',methods=['POST'])
def retreivecommunity(message):
	from flask import g,session
	with open('./chatsdb/community.bin','rb') as binfile:
		data = pickle.load(binfile)
	data = {'messages':data}
	return str(json.dumps(data))

@app.route('/fan/profile/<userid>')
def profilepage(userid):
	from flask import g,session
	with open(f'./usersdb/{userid}.preferences') as f:
		lines=f.readlines()
		session['showname']=lines[0].split(',')[1].replace('\n','')
		session['showemail']=lines[1].split(',')[1].replace('\n','')
		session['showmemberid']=lines[2].split(',')[1].replace('\n','')
		session['showdatejoined']=lines[3].split(',')[1].replace('\n','')
		session['showtimejoined']=lines[4].split(',')[1].replace('\n','')
		session['showcity']=lines[5].split(',')[1].replace('\n','')
		session['showinstagram']=lines[6].split(',')[1].replace('\n','')
		session['showfacebook']=lines[7].split(',')[1].replace('\n','')
		session['showtwitter']=lines[8].split(',')[1].replace('\n','')
		session['showwhatsapp']=lines[9].split(',')[1].replace('\n','')
		session['showspotify']=lines[10].split(',')[1].replace('\n','')
		session['showdonated']=lines[11].split(',')[1].replace('\n','')
		session['showofficialmerchandise']=lines[12].split(',')[1].replace('\n','')
		session['showtotalmessageactivity']=lines[13].split(',')[1].replace('\n','')
		session['showartistmessageactivity']=lines[14].split(',')[1].replace('\n','')
		session['showtopstreamer']=lines[15].split(',')[1].replace('\n','')
		session['showpmdate']=lines[16].split(',')[1].replace('\n','')
		session['showtheme']=lines[17].split(',')[1].replace('\n','')
	return render_template('profilepage.html',session=session,artist=artistconfig['artist'])

@app.route('/fan/bandcamp')
def bandcamp():
	from flask import g,session
	return render_template('bandcamp.html',artist=artistconfig['artist'])

@app.route('/fan/artist/info')
def artist():
	from flask import g,session
	regf = len(os.listdir('usersdb'))
	cwd = os.getcwd()
	os.chdir('artist')
	exc = len(os.listdir('exclusives'))
	os.chdir(cwd)
	return render_template('artist.html',artist=artistconfig['artist'],info=[regf,exc])

@app.route('/fan/artist')
def artistchat():
	from flask import g,session
	return render_template('communitychat.html')

@app.route('/fan/artist/update/<message>',methods=['POST'])
def updateartist(message):
	from flask import g,session
	with open('./chatsdb/artist.bin','rb') as binfile:
		data = pickle.load(binfile)
	data.append({'sender':session.get('username'),'message':message,'date':{str((datetime.datetime.now().strftime('%d/%m/%Y')))},'time':{str((datetime.datetime.now().strftime('%H:%M:%S')))}})
	with open('./chatsdb/artist.bin','wb') as binfile:
		pickle.dump(binfile,data)
	return '200'

@app.route('/fan/artist/retreive',methods=['POST'])
def retreiveartist(message):
	from flask import g,session
	with open('./chatsdb/artist.bin','rb') as binfile:
		data = pickle.load(binfile)
	data = {'messages':data}
	return str(json.dumps(data))

@app.route('/fan/preview')
def exclusivepreview():
	from flask import g,session
	def csvtodict(csvfile):
	    a_csv_file = open(csvfile, "r")
	    dict_reader = csv.DictReader(a_csv_file)

	    mainlist=[]
	    for i in list(dict_reader):
	        mainlist.append(dict(i))
	    return mainlist
	return render_template('previews.html',exclusives=csvtodict('./artist/previews.db'),artist=artistconfig['artist'])

@app.route('/fan/preview/track/<track>')
def previewaudio(track):
	return send_file(f'./artist/exclusives/{track}.mp3')


@app.route('/fan/ideations')
def ideations():
	from flask import g,session
	ideations=[]
	with open('./artist/ideations.db') as f:
		for i in f.readlines():
			ideations.append(i)
	return render_template('ideations.html',ideations=ideations,artist=artistconfig['artist'])

@app.route('/callback/')
def callback(): 
    from flask import g,session
    oauth = f'Bearer {(startup.getUserToken(request.args["code"]))}'
    session['oauth']=oauth
    session['spotitoken'] = 'Gottem Baby!'
    return redirect(url_for('relation'))

@app.route('/fan/spotify/connect',methods=['POST','GET'])
def tokengetter():
    from flask import g,session
    response = startup.getUser()
    return redirect(response)

@app.route('/resetsp',methods=['POST','GET'])
def resetspoti():
	from flask import g,session
	session['spotitoken'] = None
	return redirect('http://localhost:5000//fan/dashboard')

@app.route('/artist/relation')
def relation():
	from flask import g,session
	if not session.get('spotitoken'):
		return redirect(url_for('tokengetter'))
	elif session.get('spotitoken')==None:
		return redirect(url_for('tokengetter'))
	import requests
	headers = {
	    'Accept': 'application/json',
	    'Content-Type': 'application/json',
	    'Authorization': session.get('oauth'),
	}
	response = requests.get('https://api.spotify.com/v1/me/top/artists?limit=100', headers=headers)
	try:
		import json
		userdet = (json.loads(response.content))
		gottem = False
		for i in userdet['items']:
			if gottem == False:
				if artistconfig['artist']['links']['SPOTIFY'] == i['external_urls']['spotify']:
					session['topstreamer'] = "True"
					gottem = True
				else:
					session['topstreamer'] = "False"
	except:
		session['topstreamer'] = "NoSpot"
	with open(f"./usersdb/{session['memberid']}.preferences",'w') as f:
		memid,datejoined,timejoint = session['memberid'].replace('\n',''),session['datejoined'].replace('\n',''),session['timejoined'].replace('\n','')
		f.write(f'''NAME,{session['name']}
E-MAIL,{session['email']}
MEMBER ID,{session['memberid']}
DATE JOINED,{session['datejoined']}
TIME JOINED,{session['timejoined']}
CITY,{session['city']}
INSTAGRAM,{session['instagram']}
FACEBOOK,{session['facebook']}
TWITTER,{session['twitter']}
WHATSAPP,{session['whatsapp']}
SPOTIFY,{session['spotify']}
DONATED,{session['donated']}
OFFICIAL MERCHANDISE,{session['officialmerchandise']}
TOTAL MESSAGE ACTIVITY,0{session['totalmessageactivity']}
ARTIST MESSAGE ACTIVITY,0{session['artistmessageactivity']}
TOP STREAMER,{session['topstreamer']}
PM DATE,{str((datetime.datetime.now().strftime('%d/%m/%Y')))}
THEME,dark''')
	with open(f"./usersdb/{session['memberid']}.preferences") as f:
		lines = f.readlines()
		session['name']=lines[0].split(',')[1].replace('\n','')
		session['email']=lines[1].split(',')[1].replace('\n','')
		session['memberid']=lines[2].split(',')[1].replace('\n','')
		session['datejoined']=lines[3].split(',')[1].replace('\n','')
		session['timejoined']=lines[4].split(',')[1].replace('\n','')
		session['city']=lines[5].split(',')[1].replace('\n','')
		session['instagram']=lines[6].split(',')[1].replace('\n','')
		session['facebook']=lines[7].split(',')[1].replace('\n','')
		session['twitter']=lines[8].split(',')[1].replace('\n','')
		session['whatsapp']=lines[9].split(',')[1].replace('\n','')
		session['spotify']=lines[10].split(',')[1].replace('\n','')
		session['donated']=lines[11].split(',')[1].replace('\n','')
		session['officialmerchandise']=lines[12].split(',')[1].replace('\n','')
		session['totalmessageactivity']=lines[13].split(',')[1].replace('\n','')
		session['artistmessageactivity']=lines[14].split(',')[1].replace('\n','')
		session['topstreamer']=lines[15].split(',')[1].replace('\n','')
		session['pmdate']=lines[16].split(',')[1].replace('\n','')
		session['theme']=lines[17].split(',')[1].replace('\n','')
	return render_template('pm.html',word=artistconfig['words'][session.get('topstreamer')],artist=artistconfig['artist'],session=session)

	from flask import g,session
	with open('./artist/ideations.db') as f:
		for i in f.readlines():
			ideations.append(i)
	return render_template('ideations.html',ideations=ideations)


@app.route('/fan/profile/settings')
def profilesettings():
	from flask import g,session
	return render_template('profilesettings.html',session=session,artist=artistconfig['artist'])

@app.route('/fan/profile/settings/update',methods = ['POST'])
def updateprofilesettings():
	from flask import g,session
	with open(f"./usersdb/{session['memberid']}.preferences",'w') as f:
		memid,datejoined,timejoint = session['memberid'].replace('\n',''),session['datejoined'].replace('\n',''),session['timejoined'].replace('\n','')
		f.write(f'''NAME,{request.form['name']}
E-MAIL,{request.form['email']}
MEMBER ID,{memid}
DATE JOINED,{datejoined}
TIME JOINED,{timejoint}
CITY,{request.form['city']}
INSTAGRAM,{request.form['instagram']}
FACEBOOK,{request.form['facebook']}
TWITTER,{request.form['twitter']}
WHATSAPP,{request.form['whatsapp']}
SPOTIFY,{request.form['spotify']}
DONATED,0
OFFICIAL MERCHANDISE,{request.form['merch']}
TOTAL MESSAGE ACTIVITY,0
ARTIST MESSAGE ACTIVITY,0
TOP STREAMER,False
PM DATE,{str((datetime.datetime.now().strftime('%d/%m/%Y')))}
THEME,dark''')
	with open(f"./usersdb/{session['memberid']}.preferences") as f:
		lines = f.readlines()
		session['name']=lines[0].split(',')[1].replace('\n','')
		session['email']=lines[1].split(',')[1].replace('\n','')
		session['memberid']=lines[2].split(',')[1].replace('\n','')
		session['datejoined']=lines[3].split(',')[1].replace('\n','')
		session['timejoined']=lines[4].split(',')[1].replace('\n','')
		session['city']=lines[5].split(',')[1].replace('\n','')
		session['instagram']=lines[6].split(',')[1].replace('\n','')
		session['facebook']=lines[7].split(',')[1].replace('\n','')
		session['twitter']=lines[8].split(',')[1].replace('\n','')
		session['whatsapp']=lines[9].split(',')[1].replace('\n','')
		session['spotify']=lines[10].split(',')[1].replace('\n','')
		session['donated']=lines[11].split(',')[1].replace('\n','')
		session['officialmerchandise']=lines[12].split(',')[1].replace('\n','')
		session['totalmessageactivity']=lines[13].split(',')[1].replace('\n','')
		session['artistmessageactivity']=lines[14].split(',')[1].replace('\n','')
		session['topstreamer']=lines[15].split(',')[1].replace('\n','')
		session['pmdate']=lines[16].split(',')[1].replace('\n','')
		session['theme']=lines[17].split(',')[1].replace('\n','')
		session['username']=session['name']
	print(session)
	return redirect(url_for('dashboard',username=session.get('name')))

@app.route('/fan/dashboard')
def dashboard():
	from flask import g,session
	return render_template('dashboard.html',session=session,artist=artistconfig['artist'])

app.run(debug=True)