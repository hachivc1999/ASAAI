import requests
import json

#THIS FILE IS FOR BOT ONLY
TOKEN = 'eZGcnkJKIzZvpcZ0hSzzarEX1th6exKgJ0vpbKMD3y8wFIfXVr3DayYkbQT2ym8s'

def fillMonthDay(s):
    #change 1-9 to 01-09, return itself otherwise
    if len(s) == 1:
        return '0' + s
    return '0' + s[1] if s[0] == ' ' else s

#convert a random date to suitable date format
#the format of date in this project is:
# (Season) year or (date/)month/year or Updating
def parseDate(s):
    #convert date to uniform format
    if s == '' or s is None or s == []:
        return 'Updating'
    retstr = ''
    if '/' in s:
        datelst = s.split('/')
        if len(datelst) == 2:
            #Mùa xuân 2/2017
            retstr = datelst[1] + '/' + fillMonthDay(datelst[0][-2:])
        else:
            if len(datelst[0]) >= 2:
                #Mùa xuân 1/2/2017
                retstr = '/'.join([datelst[2],fillMonthDay(datelst[1]),fillMonthDay(datelst[0][-2:])])
            else:
                #1/2/2017
                retstr = '/'.join([datelst[2],fillMonthDay(datelst[1]),fillMonthDay(datelst[0])])
    else:
        s = s.lower()
        if len(s) == 4:
            #2017
            retstr = s
        else:     
            if "đang cập nhật" in s: 
                #Mùa xuân Đang cập nhật 
                #đang cập nhật 
                retstr = 'Updating'
            else:
                #Mùa xuân 2017
                dic = {'mùa xuân ' : "Spring ", "mùa hạ " : "Summer ", "mùa thu " : "Autumn ", "mùa đông " : "Winter "}
                season, year = (s[:-4],s[-4:])
                season = dic.get(season,'')
                retstr = season + year
    return retstr       


def jsonifyList(title, tags, seasons, path):
    #convert list to match db model
    #title: list of titles
    #tags: list of tags for each title [['1','2'],['3','4']...]
    #seasons: list of seasons for each title, same structure
    #path: your path
    #remember to make the data at the correct position
    #example:
    #title: [['Oni Chichi', 'Devil Dad', 'PoRo', 'https://cdn.myanimelist.net/images/anime/1793/103867.jpg', 'A nice dad and his beautiful daughter']]
    #tags: [['Ecchi', 'Hentai']]
    #seasons: [[('Oni Chichi Reborn', '2010-6-4', 2, 'YES', 'https://www.youtube.com/watch?v=abcXYZ'), ('Oni Chichi Refresh', '2011-4-2', 4, 'YES', 'https://www.youtube.com/watch?v=abcXYZ')]]
    if title == []:
        return []
    tagpos = 4 #position of tag list in json model
    seasonpos = 6 #position of season list in json model
    titlekey = ['name', 'transName','producer','pictureLink','tags','description','seasons']
    seasonkey = ['name','releaseDate','numberOfEpisode','isCompleted','link']
    newtitleList = []
    for i in range(0, len(title)):
        curtitle = title[i]
        #insert tag list at tag position
        curtitle.insert(tagpos, tags[i])
        
        #match each season with key then insert at season position
        season = seasons[i]
        seasonlst = []
        for s in season:
            if type(s[2]) is not int:
                s[2] = 0
            s = (s[0], parseDate(s[1])) + s[2:] 
            seasonlst.append(dict(zip(seasonkey,s)))
        curtitle.insert(seasonpos, seasonlst)
        #insert final result
        titlefinal = dict(zip(titlekey,curtitle))
        newtitleList.append(titlefinal)
    
    #printout
    name = '' #insert here, if name already in path, skip this
    dirr = path + name if name != '' else path
    print(dirr)
    with open(dirr, "w") as file:
        json.dump(newtitleList, file, indent=4)
        
#upload the file to server
def upload(path):        
    url = 'some_random_url.com/upload' #DO NOT CHANGE
    file = 'file' #DO NOT CHANGE
    ids = 'id' #DO NOT CHANGE
    
    name = '' #add name if required
    dirr = path + name if name != '' else path
    files = {file: open(dirr, 'rb')}
    payload = {ids: TOKEN}
    print(requests.post(url, files=files, data = payload))
