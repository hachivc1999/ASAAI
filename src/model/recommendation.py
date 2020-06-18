from database import dbfetch
import numpy as np
import random

RECOMMENDATION_SIZE = 10
FAST_RECOMMENDATION_THRESHOLD = 400
DEFAULT_SCORE = 50.

def generateRecommendation(username):
#def generateRecommendation(favorite, nonFavorite):
    favorite = generateFavList(username)
    nonFavorite = generateNonFavList(username)
    if favorite.size <  0:
        return generateDefaultRecommendation(nonFavorite)
    elif favorite.size < FAST_RECOMMENDATION_THRESHOLD:
        return generateFastRecommendation(favorite, nonFavorite)
    else:   
        recommendList = [x[0] for x in dbfetch.getIdAllTitle() if x[0] not in np.concatenate((favorite,nonFavorite))]
        return generateNormalRecommendation(favorite, nonFavorite, recommendList)   

def generateDefaultRecommendation(nonfav):
    recommendlist = [x[0] for x in dbfetch.getIdAllTitle() if x[0] not in nonfav]
    if len(recommendlist) > RECOMMENDATION_SIZE:
        recommendlist = random.sample(recommendlist, RECOMMENDATION_SIZE)
    return [(x,DEFAULT_SCORE) for x in recommendlist]

def generateFastRecommendation(fav, nonfav):
    recommendList = [x[0] for x in dbfetch.getIdAllTitle() if x[0] not in np.concatenate((fav,nonfav))] 
    randomList = random.sample(recommendList, 10*RECOMMENDATION_SIZE)
    return generateNormalRecommendation(fav, nonfav, randomList)
    #CONTINUE HERE LAST NIGHT
    
def generateNormalRecommendation(fav, nonfav, lst):   
    recommendSize = len(lst)
    if recommendSize == 0:
        return np.array([])
    arr = np.zeros((recommendSize,2))
    i = 0
    for title in lst:
        scoreStr = dbfetch.getRecommendation(title)[0][1]
        scoreFav,scoreNon = split_withlst(scoreStr, fav)
        sf, sn = matchSize(scoreFav.size, scoreNon.size)
        sf,sn = (int(sf),int(sn))
        topFav = scoreFav if sf >= scoreFav.size else -np.sort(np.partition(-scoreFav,sf)[:sf])
        topNon = scoreNon if sn >= scoreNon.size else -np.sort(np.partition(-scoreNon,sn)[:sn])
        score = geometricSeriesAverage(topFav) - geometricSeriesAverage(topNon)
        arr[i] = (title,10) if score <= 10 else (title,np.round(score,2))
        i += 1
    return arr[arr[:,1].argsort()[::-1]][:RECOMMENDATION_SIZE]
    
def updateCompatible(username, t = 0):
#def updateCompatible(favorite, nonFavorite):
    favorite = generateFavList(username)
    if favorite.size == 0:
        return []
    if favorite.size == 1:
        return [DEFAULT_SCORE]
    result = []
    lst = t if t != 0 else favorite
    nonFavorite = generateNonFavList(username)
    for title in lst:
        scoreStr = dbfetch.getRecommendation(str(title))[0][1]
        scoreFav, scoreNon = split_withlst(scoreStr, favorite, nonFavorite)
        sf, sn = matchSize(scoreFav.size, scoreNon.size)
        sf, sn = (int(sf),int(sn))
        topFav = scoreFav if sf >= scoreFav.size else -np.sort(np.partition(-scoreFav,sf)[:sf])
        topNon = scoreNon if sn >= scoreNon.size else -np.sort(np.partition(-scoreNon,sn)[:sn])
        score = geometricSeriesAverage(topFav) - geometricSeriesAverage(topNon)
        score = 10 if score < 10 else np.round(score,2)
        result.append(score)          
        #dbfetch.updateCompatibleFavoriteList(username, str(title), compatible)
    return result

#get favorite title id
def generateFavList(username):
    return np.array([int(x[0]) for x in dbfetch.getIdFavoriteList(username)])

#get non favorite title id
def generateNonFavList(username):
    return np.array([int(x[0]) for x in dbfetch.getIdNotFavoriteList(username)])

#get watching title id
def generateWatchingList(username):
    return np.array([int(x[0]) for x in dbfetch.getIdWatchingList(username)])

#get status code
def generateStatusCode(username, title):
    fil = generateFilter(username)
    return round(sum([x+0.6 for x in range(0,3) if title in fil[x]]))
#get filter
def generateFilter(username):
    return [generateFavList(username), generateNonFavList(username), generateWatchingList(username)]
def split_compatible(s):
    return np.array([int(x) for x in s.split(',')])

def split_withlst(s,lst, lst2 = np.array([])):
    #split the string to list and remove all which position are not in lst
    arr = s.split(' ')
    dic = dict(zip(arr[::2],arr[1::2]))
    if lst2.size != 0:
        return np.array([float(dic.get(str(x))) for x in lst if dic.get(str(x)) is not None]), np.array([float(dic.get(str(x))) for x in lst2 if dic.get(str(x)) is not None])
    return np.array([float(dic.get(str(x))) for x in lst if dic.get(str(x)) is not None]), np.array([])
    '''    
    arr = np.array(s.split(' ')).astype('float')
    if lst2.size != 0:
        return arr[1::2][np.in1d(arr[::2],lst,assume_unique = True)], arr[1::2][np.in1d(arr[::2],lst2,assume_unique = True)]
    return arr[1::2][np.in1d(arr[::2],lst,assume_unique = True)], np.array([])
    '''
def split_withoutlst(s,lst):
    #split the string to list and remove all which position are in lst
    arr = np.array(s.split(' ')).astype('float')
    _,con,_ = np.intersect1d(arr[::2],lst, return_indices = True, assume_unique = True)
    return np.delete(arr,[con*2,con*2+1])

def join_compatible(lst):
    return ','.join(str(x) for x in lst)
    
#an average calculation which works with strange range output
#example: array like 100 1 1 will return 34 with normal average. However, it isn't good
#apply this conversion will return 100/2 + 1/4 + 1/4 = 50.5 
def geometricSeriesAverage(arr):
    if arr.size == 0:
        return 0
    for i in range(0, arr.size):
        arr[i] *= 0.5**(i+1)
    return sum(arr) + arr[-1]

def matchSize(f,n):
    #return approriate size of favorite and nonfavorite title given split size
    rs = RECOMMENDATION_SIZE #for better looking
    if f < rs:
        #when favorite has too few title
        #ex: rs,f,n = 10,6,2 
        return f,0
    if f >= rs*1.5 and n >= rs*0.5:
        #when both has too many title
        #ex: 10,52,23
        return rs*1.5, rs*0.5
    if f - n < rs:
        #when nonfavorite is more than favorite
        #ex: 10,11,7
        return f,f-rs
    if f - n >= rs:
        #when favorite is more than nonfavorite
        #ex: 10,25,4
        return n+rs,n
    return rs*1.5,rs*0.5
