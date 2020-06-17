import flask
from flask import request, jsonify
import util
from model import engine, recommendation
from database import dbfetch
import json
from api_v1 import api_return
from api_v1.api_return import Error

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config["JSON_SORT_KEYS"] = False

#create database lock and token for upload bot
DATABASE_UPDATE = False
BOT_TOKEN = 'eZGcnkJKIzZvpcZ0hSzzarEX1th6exKgJ0vpbKMD3y8wFIfXVr3DayYkbQT2ym8s'

#homepage
@app.route('/', methods=['GET'])
def home():
    return '''<h1>Anime Selecting Application using Artificial Intelligence</h1>'''

#return all titles from database in json format
@app.route('/all', methods=['GET'])
def api_all():
    #checking errors from request
    update = checkUpdate()
    if type(update) == Error:
        return update.get()
    tk = request.headers.get('id')
    verify = verifyToken(tk)
    if type(verify) == Error:
        return verify.get()
    
    #if there is no error, verify is user account in format (id,username,password)
    username = verify[1]
    #get all title from database
    result = dbfetch.getAll()
    
    #generate filter for status code of a title
    fil = recommendation.generateFilter(username)
    return jsonify(util.jsonTitle(result, fil = fil))

#search function, return conditional title
@app.route('/search', methods=['GET'])
def api_search():
    #checking errors from requests
    update = checkUpdate()
    if type(update) == Error:
        return update.get()
    tk = request.headers.get('id')
    verify = verifyToken(tk)
    if type(verify) == Error:
        return verify.get()
    
    #if there is no error, verify is user account in format (id,username,password)
    username = verify[1]
    
    #get filter options from request
    param = request.args
    name = param.get('name') #title name can be at format "an_apple" or "an apple"
    tags = param.get('tags')
    unwantedTags = param.get('not')
    
    #preprocess the title, return the format of name and tags
    #for name, it is a string; for tags and unwanted tags, it is a list of string
    name,tags,unwantedTags = util.searchPreprocess(name, tags, unwantedTags)
    
    #get title from database based on input and return with filter (status code)
    titles = dbfetch.getTitle([name] + tags + unwantedTags)
    fil = recommendation.generateFilter(username)
    return jsonify([]) if titles == 0 else jsonify(util.jsonTitle(titles, fil = fil))

#handling user registration
#a user can register to the system
@app.route('/regis', methods=['POST'])
def api_register():
    #checking for server maintenance
    update = checkUpdate()
    if type(update) == Error:
        return update.get()
    
    #getting username as password from request
    param = request.form
    username = param.get('name')
    password = param.get('pw')
    
    #if either username or password is None, return 400 (Bad request)
    if not (username and password):
        return api_err_400().get()
   
    #find input username in the database, if user exists, return 409 (Conflict)
    user = dbfetch.findUserbyName(username)
    if user != []:
        return api_err_409(username).get()
    
    #generate a token not located in the database
    tk = util.generateToken()
    while type(verifyToken(tk)) != Error: 
        tk = util.generateToken()
    
    #add the user into the database and return the token
    dbfetch.addUser(tk, username, password)
    return jsonify(api_return.register_success(tk).get())

#handling user login
@app.route('/login', methods=['POST'])
def api_login():
    #checking for server maintenance
    update = checkUpdate()
    if type(update) == Error:
        return update.get()
    
    #getting username as password from request
    param = request.form
    username = param.get('name')
    password = param.get('pw')
    
    #if either username or password is None, return 400 (Bad request)
    if not (username or password):
        return api_err_400().get()
    
    #find input username in the database, if user not exists, return 401 (Unauthorized)
    user = list(dbfetch.findUserbyName(username))
    if not user or user[0][2] != password:
        return api_err_401().get()
    else:
        #generate a nonexistence token. Then, update the token in the database and return it
        tk = util.generateToken()
        while type(verifyToken(tk)) != Error:
            tk = util.generateToken()
        dbfetch.addUser(tk,username, password)
        return jsonify(api_return.login_success(tk).get())

#update or return user favorite list
@app.route('/fav', methods=['GET','POST'])
def api_fav_update():
    #checking update
    update = checkUpdate()
    if type(update) == Error:
        return update.get()
    #method == get <=> return user favorite list
    if request.method == 'GET':
        return fav_get(request.headers)
    #method == post <=> update user favorite list
    elif request.method == 'POST':
        return fav_post(request.form)

def fav_get(header):
    #checking token from database
    tk = header.get('id')
    verify = verifyToken(tk)
    if type(verify) == Error:
        return verify.get()

    #getting username and using it to get favorite titles and their compatibleScore
    username = verify[1]
    newCompatible = recommendation.updateCompatible(username)
    return jsonify(util.jsonTitle(dbfetch.getFavoriteList(username),compatible = newCompatible))
    
def fav_post(form):
    #checking token from database
    tk = form.get('id')
    verify = verifyToken(tk)
    if type(verify) == Error:
        return verify.get()
    
    #getting username, titleId and option for update favorite list
    username = verify[1]
    title = form.get('title')
    option = form.get('op')
    #add to favorite list
    if option == 'af':
        dbfetch.updateFavoriteList(username,title,0)
        return jsonify(api_return.favorite_success().get()) #return 1
    #remove from favorite list
    elif option == 'rf':
        dbfetch.updateFavoriteList(username, title,1)
        return jsonify(api_return.favorite_remove_success().get()) # return -1
    #add to nonFavorite list
    elif option == 'an':
        dbfetch.updateNotFavoriteList(username,int(title),0)
        return jsonify(api_return.unfavorite_success().get()) #return 2
    #remove from nonFavorite list
    elif option == 'rn':
        dbfetch.updateNotFavoriteList(username,int(title),1)
        return jsonify(api_return.unfavorite_remove_success().get()) #return -2
    else:
        #if option is None or not correct, return 400 (Bad request)
        return jsonify(api_err_400().get())
  
#update or return user watching list
@app.route('/watch', methods = ['GET', 'POST'])
def api_watchlist():
    #checking update
    update = checkUpdate()
    if type(update) == Error:
        return update.get()
    #method == GET <=> return
    if request.method == 'GET':
        return watchlist_get(request.headers)
    #method == POST <=> update
    elif request.method == 'POST':
        return watchlist_post(request.form)

def watchlist_get(header):
    #checking token from database
    tk = header.get('id')
    verify = verifyToken(tk)
    if type(verify) == Error:
        return verify.get()
    
    #getting username. From it, get the id and compatibleScore of each title in watching list
    #notice that the compatibleScore is stored with titles in Favorite list
    #after that, return the titles with their compatible scores
    username = verify[1]
    ids = util.jsonId(dbfetch.getIdWatchingList(username))
    idcompatible = dbfetch.getCompatibleFavoriteList(username)
    compatible = [1]*len(ids) if idcompatible == 1 else [y[1] for x in ids for y in idcompatible if str(x) == y[0]]
    return jsonify(util.jsonTitle(dbfetch.getWatchingList(username),compatible = compatible))
    
def watchlist_post(form):
    #checking token from database
    tk = form.get('id')
    verify = verifyToken(tk)
    if type(verify) == Error:
        return verify.get()
    
    #getting username, titleId and option
    username = verify[1]
    title = form.get('title')
    option = form.get('op')
    if option == 'a':
        #add title to watching list
        dbfetch.updateWatchingList(username,int(title),0)
        return jsonify(api_return.watchlist_success().get()) #return 2
    elif option == 'r':
        #remove title from watching list
        dbfetch.updateWatchingList(username, int(title),1)
        return jsonify(api_return.watchlist_remove_success().get()) #return -2
    else:
        #when option is None or not match, return 400 (Bad request)
        return jsonify(api_err_400().get())

#get list of tags for the application.
#beware that only login user can get the tags by providing correct token
@app.route('/tags', methods = ['GET'])
def api_tags_get():
    #checking update and token
    update = checkUpdate()
    if type(update) == Error:
        return update.get()
    tk = request.headers.get('id')
    verify = verifyToken(tk)
    if type(verify) == Error:
        return verify.get()
    
    #return tag list
    return jsonify(util.jsonTags(dbfetch.getAllTag()))
    
#get name and translated name of each title
#same as above, only login user can get the tags
@app.route('/name', methods = ['GET'])
def api_name_get():
    #checking update and token
    update = checkUpdate()
    if type(update) == Error:
        return update.get()
    tk = request.headers.get('id')
    verify = verifyToken(tk)
    if type(verify) == Error:
        return verify.get()
    
    #return name and translated name list
    return jsonify(util.jsonName(dbfetch.getAllNameTransname()))

#handling the recommendation request from the application
@app.route('/recommend', methods = ['GET'])
def api_recommend():
    #checking update and token
    update = checkUpdate()
    if type(update) == Error:
        return update.get()
    tk = request.headers.get('id')
    verify = verifyToken(tk)
    if type(verify) == Error:
        return verify.get()    
    
    #get username
    #get the recommended titles from database through a function
    #please check file recommend.py in /src/model for more detail
    #recommended titles come in the form [(id,compatibleScore),...]
    #query the id to get full title details and return it with compatibleScore
    username = verify[1]
    recommend = recommendation.generateRecommendation(username)
    titleList = [dbfetch.getTitleById(x[0])[0] for x in recommend]
    compatibleList = [x[1] for x in recommend]
    return jsonify(util.jsonTitle(titleList, compatible = compatibleList))          

#verify the token from a request
def verifyToken(tk):
    #if token is None or empty string, return 400 (Bad request)
    #if token not exists, return 401 (Unauthorized)
    #else, return user account
    if tk == '' or tk is None:
        return api_err_400()
    user = dbfetch.findUserbyToken(tk)
    if user == []:
        return api_err_401()
    else:
        return list(user[0])
    
#checking update function
#return 503 (Server in maintenance) if global variable DATABASE_UPDATE is True
def checkUpdate():
    if DATABASE_UPDATE is True:
        return api_err_503()

#ERROR HANDLER 
@app.errorhandler(404)
def api_err_404(e):
    return api_return.page_not_found(e).get()
@app.errorhandler(401)
def api_err_401():
    return api_return.unauthorized()
@app.errorhandler(400)
def api_err_400():
    return api_return.bad_request()
@app.errorhandler(405)
def api_err_405():
    return api_return.not_allowed().get()
@app.errorhandler(409)
def api_err_409(e):
    return api_return.conflict(e)
@app.errorhandler(500)
def api_err_500():
    return api_return.server_error().get()
@app.errorhandler(503)
def api_err_503():
    return api_return.maintenance()


#BOT AREA, USER NOT ALLOWED
import time
@app.route('/upload', methods = ['POST'])
def api_upload():
    #toggle the DATABSE_UPDATE i.e. any request while this is running will return 503
    global DATABASE_UPDATE
    DATABASE_UPDATE = True
    
    #checking for correct bot token
    #well, it is a string of 64 so unless someone hack the server to get bot token, it will not be easily manipulated
    tk = request.form.get('id')
    if tk != BOT_TOKEN:
        return api_err_401().get()
    
    #get the file from request, convert it to database format
    file = request.files['file']
    file_bytes = file.read()
    file_json = json.loads(file_bytes)
    title = util.dejsonTitle(file_json)

    #since some events may take a lot of time, before inserting to db, the server need to wait a period of time
    time.sleep(30)
    
    #inserting into database
    for t in title:
        #check for any corrupted data
        if util.checkMatching(t[0]):
            t.insert(5,0)
            t.insert(6,0)
            dbfetch.addTitle(t)
            
    #retraining model. After that, turn the DATABASE_UPDATE back to False
    newTrainModel = engine.Engine()
    newTrainModel.train(dbfetch.DB)
    DATABASE_UPDATE = False
    return 'SUCCESS'     

app.run()
