#API TESTING FOR BOT
#THERE IS NOTHING TO DO HERE YOU FILTHY USER
import flask
from flask import request
import json
from database import dbfetch
app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config["JSON_SORT_KEYS"] = False

def dejsonTitle(lst):
    titlelist = []
    for title in lst:
        titlevalue = []
        seasons = []
        tags = []
        for key,value in title.items():
            if key == 'seasons':
                for season in value:
                    seasons.append([item[1] for item in season.items()])
            elif key == 'tags':
                tags = value
            else:
                titlevalue.append(value)
        titlevalue.append(seasons)
        titlevalue.append(tags)
        titlelist.append(titlevalue)
    return titlelist

@app.route('/upload', methods = ['POST'])
def api_upload():
    print("CATCHED")
    file = request.files['file']
    file_bytes = file.read()
    file_json = json.loads(file_bytes)
    title = dejsonTitle(file_json)
    for t in title:
        t.insert(5,0)
        t.insert(6,0)
        dbfetch.addTitle(t)
    print("DONE")
    return ''
app.run()
