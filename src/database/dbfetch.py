import sqlite3

DB = 'SUM TING WONG?'

def getAll():
    #get user watching list
    #return list of titles
    conn = create_connection(DB)

    cur = conn.cursor()
    cur.execute('SELECT * FROM AnimeModel')
    result = cur.fetchall()
    animeList = getSeasonTag(result)
    return animeList

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except OSError as e:
        print(e)

    return conn

def getSeasonTag(result):
    # get season and tag
    conn = create_connection(DB)
    cur = conn.cursor()
    animeList = []
    for anime in result:
        anime = list(anime)
        cur.execute("SELECT seasonName, realeaseDate, numberOfEpisode, isCompleted,link FROM AnimeModel INNER JOIN SeasonModel ON AnimeModel.id = SeasonModel.animeId WHERE AnimeModel.name LIKE ?"
        ,('%'+anime[1]+'%',))
        temp = cur.fetchall()
        anime.append(temp)

        
        cur.execute("SELECT tagName FROM AnimeModel INNER JOIN AnimeTag ON AnimeModel.id = AnimeTag.animeId  WHERE AnimeModel.name LIKE ?"
        ,('%'+anime[1]+'%',))
        anime.append(cur.fetchall())
        
        animeList.append(anime)
    
    return animeList

#-------------------INTERACTING WITH APPLICATION------------------------------------
def getTitle(param):
    #parameter list can be id,name or tags, use for search
    #util parameter as follows:
    #cur.execute(query,param) with param as list filling into query
    #example: cur.execute('SELECT abc FROM xyz WHERE id = ? AND name = ?',[1,'abcd'])
    #note: title name should be stored as lowercase letter

    # param list type:  [name, tag1, tag2,...]

    conn = create_connection(DB)

    animeListName = []
    if param[0]:
        cur = conn.cursor()
        cur.execute("SELECT * FROM AnimeModel WHERE name LIKE ?",('%'+param[0]+'%',))
        result = cur.fetchall() #search by name
        
        animeListName = getSeasonTag(result)

        if result and len(param) == 1:
            return animeListName
        elif not result:
            return 0                    # wrong name

    # search by tag-----------------------------------------------------------------------------------------------------------------
    if(len(param) == 1):
        return 0            #user dont input tag 

    cur = conn.cursor()
    animeList = []

    if not animeListName:
        cur.execute("SELECT id, name, transName, producer, pictureLink, description, favoriteCount, rank FROM AnimeModel INNER JOIN AnimeTag ON AnimeModel.id = AnimeTag.animeId WHERE AnimeTag.tagName LIKE ?",('%'+param[1]+'%',))
        
        result = cur.fetchall()

        animeList = getSeasonTag(result)
    else:
        # tag and name search
        animeList = animeListName
        animeTagFilter = []
        if (len(param) > 1):                            #sai
            for tagParam in range(1,len(param)):
                for anime in animeList:
                    for temp in range(0,len(anime[9])):        #loop in tag list anime
                        if (anime[9][temp][0] == param[tagParam]):
                            animeTagFilter.append(anime)

                animeList = animeTagFilter
                animeTagFilter = []
        if not animeList:
            return 0
        return animeList
    
    # tag search
    animeTagFilter = []
    if (len(param) > 2):                            #sai
        for tagParam in range(2,len(param)):
            for anime in animeList:
                for temp in range(0,len(anime[9])):        #loop in tag list anime
                    if (anime[9][temp][0] == param[tagParam]):
                        animeTagFilter.append(anime)

            animeList = animeTagFilter
            animeTagFilter = []
         

    return animeList

def getTitle2(name, tag = [], unwanttag = []):
    #parameter list can be id,name or tags, use for search
    #util parameter as follows:
    #cur.execute(query,param) with param as list filling into query
    #example: cur.execute('SELECT abc FROM xyz WHERE id = ? AND name = ?',[1,'abcd'])
    #note: title name should be stored as lowercase letter

    # param list type:  name, list of tag, list of unwanttag
    # neu khong co name thi pass None o param name

    conn = create_connection(DB)

    animeListName = []
    if name:#param[0]:
        cur = conn.cursor()
        cur.execute("SELECT * FROM AnimeModel WHERE name LIKE ? OR transName LIKE ?",('%'+name+'%','%'+name+'%'))         ##
        result = cur.fetchall() #search by name
        
        animeListName = getSeasonTag(result)

        if result and not tag and not unwanttag:
            return animeListName
        elif not result:
            return 0                    # wrong name

    # search by tag-----------------------------------------------------------------------------------------------------------------
    if not tag:#(len(param) == 1): ##
        return 0            #user dont input tag 

    cur = conn.cursor()
    animeList = []

    if not animeListName:
        cur.execute("SELECT distinct id, name, transName, producer, pictureLink, deion, favoriteCount, rank FROM AnimeModel INNER JOIN AnimeTag ON AnimeModel.id = AnimeTag.animeId WHERE AnimeTag.tagName LIKE ?",('%'+tag[0]+'%',))
        #get anime of first tag
        result = cur.fetchall()

        animeList = getSeasonTag(result)
    else:
        # tag and name search
        animeList = animeListName
        animeTagFilter = []
        if  (len(tag) > 0): #(len(param) > 1):                            #sai
            for tagParam in range(0,len(tag)): #range(1,len(param)):
                for anime in animeList:
                    for temp in range(0,len(anime[9])):        #loop in tag list anime
                        if (anime[9][temp][0] == tag[tagParam]):
                            animeTagFilter.append(anime)

                animeList = animeTagFilter
                animeTagFilter = []
        if not animeList:
            return 0
        return animeList
    
    # tag search
    animeTagFilter = []
    if (len(tag) > 1): #(len(param) > 2):                            #sai
        for tagParam in range(1,len(tag)): #range(2,len(param)):
            for anime in animeList:
                for temp in range(0,len(anime[9])):        #loop in tag list anime
                    if (anime[9][temp][0] == tag[tagParam]):
                        animeTagFilter.append(anime)

            animeList = animeTagFilter
            animeTagFilter = []
    #print(animeList)
    tempAnimeList = []
    for anime in animeList:
        tempAnimeList.append(anime)
    if unwanttag:
        for anime in animeList:
            #print("amime: " + str(anime[0]) +" len: " + str(len(anime[9])))
            for temp in range(0,len(anime[9])):
                #print(anime[9][temp][0])
                if(anime[9][temp][0] in unwanttag):
                    # print("remove: ")
                    # print(anime[0])
                    # print("------")
                    tempAnimeList.remove(anime)


def getTitleById(idLst):
    conn = create_connection(DB)

    sql = "SELECT * FROM AnimeModel WHERE id IN ("
    for x in range(0,idLst.size-1):
        sql = sql + str(idLst[x])+ ","
    sql = sql + str(idLst[idLst.size - 1]) + ")"
    cur = conn.cursor()
    # cur.execute("SELECT * FROM AnimeModel WHERE id = ?",(id,))
    
    cur.execute(sql)
    result = cur.fetchall() #search by name
    
    animeDetail = getSeasonTag(result)

    return animeDetail

def getAllTitle():
    #get all title, use for recommending algorithm
    conn = create_connection(DB)
    cur = conn.cursor()
    cur.execute('SELECT * FROM AnimeModel')
    row = cur.fetchall()
    return row

def getIdAllTitle():
    conn = create_connection(DB)
    cur = conn.cursor()
    cur.execute('SELECT id FROM AnimeModel')
    row = cur.fetchall()
    return row

def findUserbyName(username):
    #get user account based on username, use for login
    conn = create_connection(DB)

    cur = conn.cursor()
    cur.execute('SELECT * FROM User WHERE userName = ?', (username,))

    row = cur.fetchall()
    return row

def findUserbyToken(token):
    #get user account based on token
    conn = create_connection(DB)

    cur = conn.cursor()
    cur.execute('SELECT * FROM User WHERE userToken = ?', (token,))

    row = cur.fetchall()
    return row

def addUser(token,username,password):
    #add new user into the database
    #if username exists, update token
    #remember to add favorite/not favorite/watching as well
    conn = create_connection(DB)


    cur = conn.cursor()
    cur.execute('SELECT userName FROM User')

    listUser = cur.fetchall()

    #check if username has existed => update token
    for temp in listUser:
        if (username == temp[0]):
            sql = ''' UPDATE User SET userToken = ? WHERE userName = ?'''

            cur = conn.cursor()
            cur.execute(sql, (token, username))
            conn.commit()
            return 0

    newUser = (token,username,password)
    
    sql = ''' INSERT INTO User(userToken,userName,password) VALUES(?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, newUser)

    conn.commit()
    conn.close()
    return 1

def getFavoriteList(username):
    #get user favorite list, use for like/dislike
    #return list of titles

    conn = create_connection(DB)

    cur = conn.cursor()
    cur.execute('SELECT id, name, transName, producer, pictureLink, description, favoriteCount, rank FROM (AnimeModel INNER JOIN Favorite ON AnimeModel.id = Favorite.animeId) INNER JOIN User ON Favorite.userName = User.userName WHERE User.userName = ?'
    , (username,))

    result = cur.fetchall()
    animeList = getSeasonTag(result)
    return animeList
    
def getIdFavoriteList(username):
    #get user favorite list, use for like/dislike
    #return list of titles

    conn = create_connection(DB)

    cur = conn.cursor()
    cur.execute('SELECT animeId FROM Favorite WHERE userName = ?', (username,))

    result = cur.fetchall()
    
    return result

def updateFavoriteList(username, titleID, option, compatible = 0):
    #add/remove a title from favorite list
    #option = 0: add
    #option = 1: remove
    #return either success or failure
    conn = create_connection(DB)
    cur = conn.cursor()

    if option == 0:
        cur.execute('SELECT userName, animeId FROM Favorite  WHERE userName = ? AND animeId = ?',(username,titleID))

        listAnime = cur.fetchall()
      
        
        if listAnime:
            temp = listAnime[0]
            if (username == temp[0] and titleID == temp[1]):
                sql = ''' UPDATE Favorite SET compatible = ? WHERE userName = ? AND animeId = ?'''

                cur = conn.cursor()
                cur.execute(sql, (compatible, username, titleID))
                conn.commit()
                conn.close()
                return 0

        
        sql = "INSERT INTO Favorite(userName, animeId, compatible) VALUES(?,?,?)"
        cur.execute(sql,(username,titleID,compatible)) #default value is 0

        conn.commit()

        #increase favorite count
        sql = "UPDATE AnimeModel SET favoriteCount = favoriteCount + 1 WHERE id = ?"
        cur.execute(sql, (titleID,))
        conn.commit()


        #adjust rank
        cur.execute("SELECT id, favoriteCount, rank FROM AnimeModel ORDER BY favoriteCount")
        listRank = cur.fetchall()
        cur.execute("SELECT id, favoriteCount, rank FROM AnimeModel WHERE id = ?",(titleID,))
        chosenAnime = cur.fetchall()
        
        for i in range(0, len(listRank)-1):
            if chosenAnime[0][2] <= listRank[i][2]:     #rank
                continue
            if chosenAnime[0][1] == listRank[i][1]:       #favoriteCount
                # adjust rank + 1 == upper rank
                sql = "UPDATE AnimeModel SET rank = ? WHERE id = ?"
                cur.execute(sql, (listRank[i][2],titleID))
                conn.commit()
                conn.close()
                break

            elif chosenAnime[0][1] < listRank[i][1]:
                #keep rank of chosen anime adjust rank the remaining
                sql = "UPDATE AnimeModel SET rank = rank + 1 WHERE favoriteCount < ?"
                cur.execute(sql, (chosenAnime[0][1],))
                conn.commit()
                conn.close()
                break

        

    elif option == 1:
        sql = "DELETE FROM Favorite WHERE userName = ? AND animeId = ?"
        cur.execute(sql,(username,titleID))  
        conn.commit()

        #decreace favorite count
        sql = "UPDATE AnimeModel SET favoriteCount = favoriteCount - 1 WHERE id = ?"
        cur.execute(sql, (titleID,))
        conn.commit()

        
        #adjust rank
        cur.execute("SELECT id, favoriteCount, rank FROM AnimeModel ORDER BY rank")
        listRank = cur.fetchall()
        cur.execute("SELECT id, favoriteCount, rank FROM AnimeModel WHERE id = ?",(titleID,))
        chosenAnime = cur.fetchall()
        num = 0
        for x in listRank:
            if x[2] == chosenAnime[0][2]:
                num = num + 1
            
        for i in range(0, len(listRank)-1):
            if chosenAnime[0][2] >= listRank[i][2]:     #rank
                continue
            if chosenAnime[0][1] == listRank[i][1]:       #favoriteCount
                # adjust rank  == lower
                sql = "UPDATE AnimeModel SET rank = ? WHERE id = ?"
                cur.execute(sql, (listRank[i][2],titleID))
                conn.commit()
                conn.close()
                break

            elif chosenAnime[0][1] > listRank[i][1]:
                #keep rank of chosen anime adjust rank the remaining
                sql = "UPDATE AnimeModel SET rank = ? WHERE id = ?"
                cur.execute(sql, (chosenAnime[0][2] + num -1,titleID))
                conn.commit()
                conn.close()
                break    
    
def updateCompatibleFavoriteList(username, titleID, compatible):
    conn = create_connection(DB)
    cur = conn.cursor()
    cur.execute('SELECT userName, animeId FROM Favorite  WHERE userName = ? AND animeId = ?',(username,titleID))

    listAnime = cur.fetchall()
        
    if not listAnime:
        return 0

    sql = ''' UPDATE Favorite SET compatible = ? WHERE userName = ? AND animeId = ?'''
    cur.execute(sql, (compatible, username, titleID))
    
    conn.commit()
    conn.close()

def getCompatibleFavoriteList(username):
    conn = create_connection(DB)
    cur = conn.cursor()
    cur.execute('SELECT userName FROM Favorite  WHERE userName = ?',(username,))

    listAnime = cur.fetchall()
        
    if not listAnime:
        return 1

    sql = ''' SELECT animeId,compatible FROM Favorite WHERE userName = ?'''
    cur.execute(sql, (username,))
    result = cur.fetchall()
    return result
    
def updateNotFavoriteList(username, titleID, option = 0):
    #add a title that user dislike
    #return either success or failure
    #0: add
    #1: remove

    conn = create_connection(DB)
    cur = conn.cursor()
    
    if option == 0:
        cur.execute('SELECT userName, animeId FROM NotFavorite  WHERE userName = ? AND animeId = ?',(username,titleID))

        listAnime = cur.fetchall()
        if listAnime:
            temp = listAnime[0]
            if (username == temp[0] and titleID == temp[1]):
                return 0 #failure username, titleId existed

        sql = "INSERT INTO NotFavorite(userName, animeId) VALUES(?,?)"
        cur.execute(sql,(username,titleID))
    
    elif option == 1:
        sql = "DELETE FROM NotFavorite WHERE userName = ? AND animeId = ?"
        cur.execute(sql,(username,titleID))  
        

    conn.commit()
    conn.close()
    return 1       #success

def getIdNotFavoriteList(username):
    #get user favorite list, use for like/dislike
    #return list of titles

    conn = create_connection(DB)

    cur = conn.cursor()
    cur.execute('SELECT animeId FROM NotFavorite WHERE userName = ?', (username,))

    result = cur.fetchall()
    
    return result

def getWatchingList(username):
    #get user watching list
    #return list of titles
    conn = create_connection(DB)

    cur = conn.cursor()
    cur.execute('SELECT id, name, transName, producer, pictureLink, description, favoriteCount, rank FROM (AnimeModel INNER JOIN Watching ON AnimeModel.id = Watching.animeId) INNER JOIN User ON Watching.userName = User.userName WHERE User.userName = ?'
    , (username,))

    result = cur.fetchall()
    animeList = getSeasonTag(result)
    return animeList

def getIdWatchingList(username):
    #get user watching list
    #return list of titles
    conn = create_connection(DB)

    cur = conn.cursor()
    cur.execute('SELECT animeId FROM Watching WHERE userName = ?', (username,))

    result = cur.fetchall()
    return result

def updateWatchingList(username, titleID, option = 0):
    #add or remove a title from user watching list
    #option = 0: add
    #option = 1: remove
    #return either success or failure

    conn = create_connection(DB)
    cur = conn.cursor()
    

    if option == 0:
        cur.execute('SELECT userName, animeId FROM Watching  WHERE userName = ? AND animeId = ?',(username,titleID))

        listAnime = cur.fetchall()
        
        if listAnime:
            temp = listAnime[0]
            if (username == temp[0] and titleID == temp[1]):
                return 0 #failure username, titleId not exist

        sql = "INSERT INTO Watching(userName, animeId) VALUES(?,?)"
        cur.execute(sql,(username,titleID))

    else:
        sql = "DELETE FROM Watching WHERE userName = ? AND animeId = ?"
        cur.execute(sql,(username,titleID))
    
    conn.commit()
    conn.close()
    return 1 #success
    
def getSomeRecommendation(ids):
    conn = create_connection(DB)

    sql = "SELECT * FROM AnimeRankingModel WHERE mainAnimeId IN ("
    for x in range(0,len(ids)-1):
        sql = sql + str(ids[x])+ ","
    sql = sql + str(ids[len(ids) - 1]) + ")"
    cur = conn.cursor()
    # cur.execute("SELECT * FROM AnimeModel WHERE id = ?",(id,))
    cur.execute(sql)
    result = cur.fetchall() #search by name
    return result

def getRecommendation(titleId):
    #return compatibility ranking of title
    conn = create_connection(DB)

    cur = conn.cursor()
    cur.execute('SELECT * FROM AnimeRankingModel WHERE mainAnimeId = ? ', (titleId,))

    row = cur.fetchall()
    return row

def updateRecommendation(mainId,score):
    
    conn = create_connection(DB)
    cur = conn.cursor()
    cur.execute('SELECT mainAnimeId FROM AnimeRankingModel  WHERE mainAnimeId = ? ',(mainId,))

    listAnime = cur.fetchall()
    if listAnime:
        temp = listAnime[0]
        if (mainId == temp[0]):
            sql = ''' UPDATE AnimeRankingModel SET score = ? WHERE mainAnimeId = ? '''

            cur = conn.cursor()
            cur.execute(sql, (score, mainId))
            conn.commit()
            conn.close()
            return 0

    sql = "INSERT INTO AnimeRankingModel(mainAnimeId, score) VALUES(?,?)"
    cur.execute(sql,(mainId,score))

    conn.commit()
    conn.close()
    
def getAllNameTransname():
    #get all title, use for recommending algorithm
    conn = create_connection(DB)


    cur = conn.cursor()
    cur.execute('SELECT name, transName FROM AnimeModel')
    row = cur.fetchall()
    return row

def getAllTag():
    #get all title, use for recommending algorithm
    conn = create_connection(DB)


    cur = conn.cursor()
    cur.execute('SELECT * FROM Tag')
    row = cur.fetchall()
    return row

def getTag(titleId):
    conn = create_connection(DB)

    cur = conn.cursor()
    cur.execute('SELECT tagName FROM AnimeTag WHERE animeId = ?', (titleId,))
    row = cur.fetchall()
    return row

#------------------INTERACTING WITH UPDATE BOT---------------------------------------
def addTitle(title):
    #detailedTitle = util.dejsonTitle(title)
    #add the title into database, the order is the same as get title
    #(test by executing insert)
    #if titleID exists, update the contents

    # title type: [name, transName, producer, pictureLink, description, favoriteCount, rank, [season list], [tag list]]
    conn = create_connection(DB)

    cur = conn.cursor()

    cur.execute('SELECT name FROM AnimeModel')

    listAnime = cur.fetchall()

    #check if username has existed => update token
    for temp in listAnime:
        if (title[0] == temp[0]):           #check title exist
            sql = ''' UPDATE AnimeModel SET  transName = ?, producer = ?, pictureLink = ?, description = ?, favoriteCount = ?, rank = ? WHERE name = ?'''
            cur.execute(sql, (title[1], title[2], title[3], title[4], title[5], title[6], title[0]))
            conn.commit()

            cur.execute("SELECT id FROM AnimeModel WHERE name = ?",(title[0],))
            animeId = cur.fetchall()
            animeId = animeId[0][0]

            sql = 'DELETE FROM SeasonModel WHERE animeId=?'
            cur = conn.cursor()
            cur.execute(sql, (animeId,))
            conn.commit()

            sql = 'DELETE FROM AnimeTag WHERE animeId=?'
            cur = conn.cursor()
            cur.execute(sql, (animeId,))
            conn.commit()

            for season in title[7]:
                cur = conn.cursor()
                sql = "INSERT INTO SeasonModel(seasonName, realeaseDate, numberOfEpisode, isCompleted,link, animeId) VALUES(?,?,?,?,?,?)"
                cur.execute(sql,(season[0],season[1],season[2],season[3],season[4],animeId))
                conn.commit()
            for tag in title[8]:
                updateTag(tag)

                sql = "INSERT INTO AnimeTag(animeId,tagName) VALUES(?,?)"
                cur.execute(sql,(animeId,tag))
                conn.commit()

            conn.close()
            return 0        #1: add title
                            #0  update title

            

    sql = "INSERT INTO AnimeModel(name, transName, producer, pictureLink, description, favoriteCount, rank) VALUES(?,?,?,?,?,?,?)"
    cur.execute(sql,(title[0],title[1],title[2],title[3],title[4],title[5],title[6]))
    conn.commit()

    cur.execute("SELECT id FROM AnimeModel WHERE name = ?",(title[0],))
    animeId = cur.fetchall()
    animeId = animeId[0][0]
    
    #seasonName, realeaseDate, numberOfEpisode, isCompleted,link, animeId
    for season in title[7]:
        cur = conn.cursor()
        sql = "INSERT INTO SeasonModel(seasonName, realeaseDate, numberOfEpisode, isCompleted,link, animeId) VALUES(?,?,?,?,?,?)"
        cur.execute(sql,(season[0],season[1],season[2],season[3],season[4],animeId))
        conn.commit()

    for tag in title[8]:
        updateTag(tag)

        sql = "INSERT INTO AnimeTag(animeId,tagName) VALUES(?,?)"
        cur.execute(sql,(animeId,tag))
        conn.commit()

    conn.close()
    return 1        #1: add title
                    #0  update title
    
    
def updateTag(tagname):
    #add new tag. 
    #tag name should be stored as lowercase letter
    conn = create_connection(DB)
    cur = conn.cursor()
    
    #check tag
    cur.execute('SELECT * FROM Tag')
    listTag = cur.fetchall()
    lst = []
    if not listTag:
        sql = "INSERT INTO Tag(tagName) VALUES(?)"
        cur.execute(sql,(tagname,))
        conn.commit()
    elif listTag:
        for temp in listTag:
            lst.append(temp[0])
        if tagname not in lst:
            sql = "INSERT INTO Tag(tagName) VALUES(?)"
            cur.execute(sql,(tagname,))

            conn.commit()
    conn.close()
