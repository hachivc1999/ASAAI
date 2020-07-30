import random
import string
#This file convert useful data to desired format

tagposdb = 8
seasonposdb = 7
tagposjson = 5
seasonposjson = 7
titlekey = ['id','name', 'transName','producer','pictureLink','tags','description','seasons','favoriteCount']
seasonkey = ['name','releaseDate','numberOfEpisode','isCompleted','link']


def jsonTags(tags):
    #convert these [('tag1',),('tag2',)] to ['tag1','tag2']
    return [tag[0] for tag in tags]

def jsonId(ids):
    #convert these [('1',),('2',)] to [1,2]
    return [int(i[0]) for i in ids]

def jsonName(names):
    #return a dictionary of names
    #used when application wants to get name list
    namekey = ['name', 'transName']
    return [dict(zip(namekey,x)) for x in names]

def jsonTitle(titleList, compatible = [], fil = []):
    #the most important function
    #convert the database format to dictionary so that it can be return as json files
    newtitleList = []
    
    #loop for generating dictionary
    for title in titleList:
        #remove tag and season from title
        tag = title.pop(tagposdb)
        season = title.pop(seasonposdb)
        
        #insert tag
        title.insert(tagposjson, jsonTags(tag))
        
        #insert season
        seasonlst = [dict(zip(seasonkey,s)) for s in season]
        title.insert(seasonposjson,seasonlst)
        
        #insert compatible
        if compatible != []:
            #the compatible is stored as a list of values matching title order
            score = compatible.pop(0)
            title.append(score)
            title = dict(zip(titlekey + ['compatibleScore'],title))
            
        #insert filter i.e. status code
        elif len(fil) != 0:
            # with filter as [non,fav,watching], filter will be 0 if title not in anything
            # if f in some array, value of it will be different. 0 for normal, 1 for fav, 2 for non, 3 for fav+ watching and 4 for nonfav+watching
            idtitle = title[0]
            f = round(sum([x+0.6 for x in range(0,3) if idtitle in fil[x]]))
            title.append(f)
            title = dict(zip(titlekey + ['status'], title))
        
        #insert nothing
        else:
            title = dict(zip(titlekey,title))
        newtitleList.append(title)
    return newtitleList

def dejsonTitle(lst):
    #convert json to database output when the bot sends data
    titlelist = []
    for title in lst:
        titlevalue = []
        seasons = []
        tags = []
        for key,value in title.items():
            if key == 'seasons':
                for season in value:
                    seasons.append([season.get(item) for item in seasonkey])
            elif key == 'tags':
                tags = value
            else:
                titlevalue.append(value)
        titlevalue.append(seasons)
        titlevalue.append(tags)
        titlelist.append(titlevalue)
    return titlelist

#get a length 16 string token
def generateToken(strlen = 16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k = strlen))

def searchPreprocess(name, tags, unwantedTags):
    #convert name and tags to suitable db query
    #name: string like 'an_apple' or 'an apple'
    #tags: string with , like "Adventure,Action"
    #unwantedTags: same as tags
    #return three lists preprocessed
    name = name.replace('_',' ')
    tags = [] if tags is None else tags.split(',')
    unwantedTags = [] if unwantedTags is None else unwantedTags.split(',')
    return name,tags, unwantedTags

def validAccount(username, password):
    #check if an account is valid or not
    if len(username) < 6 or len(password) < 6:
        return False
    valid = string.ascii_letters + string.digits
    for letter in username:
        if letter not in valid:
            return False
    return True
