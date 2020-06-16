import random
import string

def jsonTags(tags):
    #convert these [('tag1',),('tag2',)] to ['tag1','tag2']
    return [tag[0] for tag in tags]
def jsonId(ids):
    return [int(i[0]) for i in ids]
def jsonName(names):
    namekey = ['name', 'transName']
    return [dict(zip(namekey,x)) for x in names]
def jsonTitle(titleList, compatible = [], fil = []):
    #convert list of title (with or without compatible) to json
    #tag and season position
    tagposdb = 9
    seasonposdb = 8
    tagposjson = 5
    seasonposjson = 7
    #keys
    titlekey = ['id','name', 'transName','producer','pictureLink','tags','description','seasons','favoriteCount','rank']
    seasonkey = ['name','releaseDate','numberOfEpisode','isCompleted','link']
    newtitleList = []
    #loop for generating json
    for title in titleList:
        #remove tag and season from title
        tag = title.pop(tagposdb)
        season = title.pop(seasonposdb)
        #remove extra ',' from tag
        taglst = []
        for t in tag:
            taglst.append(t[0])
        #insert back tag and season
        title.insert(tagposjson, taglst)
        seasonlst = [dict(zip(seasonkey,s)) for s in season]
        title.insert(seasonposjson,seasonlst)
        #insert compatible if required
        if compatible != []:
            #recommend/fav
            score = compatible.pop(0)
            title.append(score)
            title = dict(zip(titlekey + ['compatibleScore'],title))
        elif len(fil) != 0:
            #search
            # with filter as [non,fav,watching], filter will be 0 if title not in anything
            # if f in some array, value of it will be different. 1 for fav, 2 for non, 3 for watching and 4 for fav+watching
            idtitle = title[0]
            f = round(sum([x+0.7 for x in range(0,3) if idtitle in fil[x]]))
            title.append(f)
            title = dict(zip(titlekey + ['status'], title))
        else:
            title = dict(zip(titlekey,title))
        newtitleList.append(title)
    return newtitleList

#convert json to database output
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

#check whether a dict title satisfies the condition to be inserted into db
def checkMatching(dic):
    #match length
    if len(dic) != 7:
        return False
    titlekey = ('name', 'transName','producer','pictureLink','tags','description','seasons')
    seasonkey = ('name','releaseDate','numberOfEpisode','isCompleted','link')
    dickey, dicvalue = zip(*dic.items())
    print(dicvalue[5])
    #match keys
    if dickey != titlekey:
        return False
    #match type except season
    if not all(type(dicvalue[x]) is str for x in [0,1,2,3,5]) or type(dicvalue[4]) is not list:
        return False
    season = dicvalue[6]
    for s in season:
        #match season length
        if len(s) != 5:
            return False
        skey, svalue = zip(*s.items())
        #match season key
        if skey != seasonkey:
            return False
        #match type
        if not all(type(svalue[x]) is str for x in [0,1,4]) or type(svalue[2]) is not int or svalue[3] not in [0,1]:
            return False
        if svalue[1][4] != '-' or svalue[1][7]!= '-' or len(svalue[1])!= 10:
            return False
        date = svalue[1].split('-')
        if len(date) != 3 or int(date[1]) > 12 or int(date[2]) > 31:
            return False
    return True
#get a length 16 string token
def generateToken(strlen = 16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k = strlen))

def searchPreprocess(name, tags, unwantedTags):
    #convert name and tags to suitable db query
    #name: string like oni_chi
    #tags: string with , like "Adventure,Action"
    #unwantedTags: same as tags
    #return three lists preprocessed
    name = name.replace('_',' ')
    tags = [] if tags is None else tags.split(',')
    unwantedTags = [] if unwantedTags is None else unwantedTags.split(',')
    return name,tags, unwantedTags

