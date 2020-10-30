from flask_spotify_auth import getAuth, refreshAuth, getToken

CLIENT_ID = "273291319af445d78ef31d0714f4f4de"
CLIENT_SECRET = "586cf523c3a540028c3cea1b12ac8788"
PORT = "5000"
CALLBACK_URL = "http://localhost"
SCOPE = "user-top-read"
TOKEN_DATA = []


def getUser():
    return getAuth(CLIENT_ID, "{}:{}/callback/".format(CALLBACK_URL, PORT), SCOPE)

def getUserToken(code):
    global TOKEN_DATA
    TOKEN_DATA = getToken(code, CLIENT_ID, CLIENT_SECRET, f"{CALLBACK_URL}:{PORT}/callback/")
    return TOKEN_DATA[0]
 
def refreshToken(time):
    time.sleep(time)
    TOKEN_DATA = refreshAuth()

def getAccessToken():
    return TOKEN_DATA