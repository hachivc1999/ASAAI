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

#return all titles from database
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
    
    username = verify[1]
    result = dbfetch.getAll()
    fil = recommendation.generateFilter(username)
    return jsonify(util.jsonTitle(result, fil = fil))
#------------------SEARCH-----------------------
@app.route('/search', methods=['GET'])
def api_search():
    #important check
    update = checkUpdate()
    if type(update) == Error:
        return update.get()
    tk = request.headers.get('id')
    verify = verifyToken(tk)
    if type(verify) == Error:
        return verify.get()
    
    username = verify[1]
    param = request.args
    name = param.get('name')
    tags = param.get('tags')
    unwantedTags = param.get('not')
    name,tags,unwantedTags = util.searchPreprocess(name, tags, unwantedTags)
    titles = dbfetch.getTitle([name] + tags + unwantedTags)
    fil = recommendation.generateFilter(username)
    return jsonify([]) if titles == 0 else jsonify(util.jsonTitle(titles, fil = fil))

#-----------------USER_HANDLING-----------------
@app.route('/regis', methods=['POST'])
def api_register():
    #check update
    update = checkUpdate()
    if type(update) == Error:
        return update.get()
    param = request.form
    username = param.get('name')
    password = param.get('pw')
    
    if not (username and password):
        return api_err_400().get()
    tk = util.generateToken()
    user = dbfetch.findUserbyName(username)
    if user != []:
        #user exists
        return api_err_409(user[0][1]).get()
    while type(verifyToken(tk)) != Error: 
        tk = util.generateToken()
    dbfetch.addUser(tk, username, password)
    return jsonify(api_return.register_success(tk).get())

@app.route('/login', methods=['POST'])
def api_login():
    update = checkUpdate()
    if type(update) == Error:
        return update.get()
    param = request.form
    username = param.get('name')
    password = param.get('pw')
    if not (username or password):
        return api_err_400().get()
    user = list(dbfetch.findUserbyName(username)[0])
    if user is False or user[2] != password:
        return api_err_401().get()
    else:
        tk = util.generateToken()
        while type(verifyToken(tk)) != Error:
            tk = util.generateToken()
        dbfetch.addUser(tk,username, password)
        return jsonify(api_return.login_success(tk).get())

#---------------UTILITY----------------------
@app.route('/fav', methods=['GET','POST'])
def api_fav_update():
    update = checkUpdate()
    if type(update) == Error:
        return update.get()
    if request.method == 'GET':
        return fav_get(request.headers)
    elif request.method == 'POST':
        return fav_post(request.form)

def fav_get(header):
    tk = header.get('id')
    verify = verifyToken(tk)
    if type(verify) == Error:
        return verify.get()

    username = verify[1]
    newCompatible = recommendation.updateCompatible(username)
    return jsonify(util.jsonTitle(dbfetch.getFavoriteList(username),compatible = newCompatible))
    
def fav_post(form):
    tk = form.get('id')
    verify = verifyToken(tk)
    if type(verify) == Error:
        return verify.get()
    
    username = verify[1]
    title = form.get('title')
    option = form.get('op')
    #add fav
    if option == 'af':
        dbfetch.updateFavoriteList(username,title,0)
        return jsonify(api_return.favorite_success().get())
    #remove fav
    elif option == 'rf':
        dbfetch.updateFavoriteList(username, title,1)
        return jsonify(api_return.favorite_remove_success().get())
    #add nonfav
    elif option == 'an':
        dbfetch.updateNotFavoriteList(username,int(title),0)
        return jsonify(api_return.unfavorite_success().get())
    #remove nonfav
    elif option == 'rn':
        dbfetch.updateNotFavoriteList(username,int(title),1)
        return jsonify(api_return.unfavorite_remove_success().get())
    else:
        return jsonify(api_err_400().get())
  
@app.route('/watch', methods = ['GET', 'POST'])
def api_watchlist():
    update = checkUpdate()
    if type(update) == Error:
        return update.get()
    if request.method == 'GET':
        return watchlist_get(request.headers)
    elif request.method == 'POST':
        return watchlist_post(request.form)

def watchlist_get(header):
    tk = header.get('id')
    verify = verifyToken(tk)
    if type(verify) == Error:
        return verify.get()

    username = verify[1]
    ids = util.jsonId(dbfetch.getIdWatchingList(username))
    idcompatible = dbfetch.getCompatibleFavoriteList(username)
    compatible = [1]*len(ids) if idcompatible == 1 else [y[1] for x in ids for y in idcompatible if str(x) == y[0]]
    return jsonify(util.jsonTitle(dbfetch.getWatchingList(username),compatible = compatible))
    
def watchlist_post(form):
    tk = form.get('id')
    verify = verifyToken(tk)
    if type(verify) == Error:
        return verify.get()
    
    username = verify[1]
    title = form.get('title')
    option = form.get('op')
    if option == 'a':
        dbfetch.updateWatchingList(username,int(title),0)
        return jsonify(api_return.watchlist_success().get())
    elif option == 'r':
        dbfetch.updateWatchingList(username, int(title),1)
        return jsonify(api_return.watchlist_remove_success().get())
    else:
        return jsonify(api_err_400().get())

@app.route('/tags', methods = ['GET'])
def api_tags_get():
    update = checkUpdate()
    if type(update) == Error:
        return update.get()
    tk = request.headers.get('id')
    verify = verifyToken(tk)
    if type(verify) == Error:
        return verify.get()
    return jsonify(util.jsonTags(dbfetch.getAllTag()))
    
@app.route('/name', methods = ['GET'])
def api_name_get():
    update = checkUpdate()
    if type(update) == Error:
        return update.get()
    tk = request.headers.get('id')
    verify = verifyToken(tk)
    if type(verify) == Error:
        return verify.get()
    return jsonify(util.jsonName(dbfetch.getAllNameTransname()))

@app.route('/recommend', methods = ['GET'])
def api_recommend():
    update = checkUpdate()
    if type(update) == Error:
        return update.get()
    tk = request.headers.get('id')
    verify = verifyToken(tk)
    if type(verify) == Error:
        return verify.get()    
    
    username = verify[1]
    recommend = recommendation.generateRecommendation(username)
    titleList = [dbfetch.getTitleById(x[0])[0] for x in recommend]
    compatibleList = [x[1] for x in recommend]
    return jsonify(util.jsonTitle(titleList, compatible = compatibleList))          

import time
@app.route('/upload', methods = ['POST'])
def api_upload():
    global DATABASE_UPDATE
    DATABASE_UPDATE = True
    tk = request.form.get('id')
    if tk != BOT_TOKEN:
        return api_err_401().get()
    file = request.files['file']
    file_bytes = file.read()
    file_json = json.loads(file_bytes)
    title = util.dejsonTitle(file_json)

    #wait for other to disconnect before continue to insert to db
    time.sleep(30)
    for t in title:
        if util.checkMatching(t[0]):
            t.insert(5,0)
            t.insert(6,0)
            dbfetch.addTitle(t)
    newTrainModel = engine.Engine()
    newTrainModel.train(dbfetch.DB)
    DATABASE_UPDATE = False
    return 'SUCCESS'     

def verifyToken(tk):
    if tk == '':
        return api_err_400()
    user = dbfetch.findUserbyToken(tk)
    if user == []:
        return api_err_401()
    else:
        return list(user[0])
def checkUpdate():
    if DATABASE_UPDATE is True:
        return api_err_503()

#--------------ERROR--------------------------
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
@app.errorhandler(503)
def api_err_503():
    return api_return.maintenance()

app.run()
