from database import dbfetch
import numpy as np
import random


RECOMMENDATION_SIZE = 5
DEFAULT_SCORE = 50.

def generateRecommendation(username):
#def generateRecommendation(favorite, nonFavorite):
    favorite = generateFavList(username)
    nonFavorite = generateNonFavList(username)
    if favorite.size == 0:
        return generateDefaultRecommendation(nonFavorite)
    else:
        return generateNormalRecommendation(favorite, nonFavorite)
    

def generateDefaultRecommendation(nonfav):
    recommendlist = [x[0] for x in dbfetch.getAllTitle() if x[0] not in nonfav]
    if len(recommendlist) > RECOMMENDATION_SIZE:
        recommendlist = random.sample(recommendlist, RECOMMENDATION_SIZE)
    return [(x,DEFAULT_SCORE) for x in recommendlist]
 
def generateNormalRecommendation(fav, nonfav):
    recommendList = [x[0] for x in dbfetch.getAllTitle() if x[0] not in np.concatenate((fav,nonfav))]
    recommendSize = len(recommendList)
    if recommendSize == 0:
        return np.array([])
    arr = np.zeros((recommendSize,2))
    arr[:,0] = recommendList
    for title in recommendList:
        scoreStr = dbfetch.getRecommendation(title)[0][1]
        scoreFav, scoreNon = split_withlst(scoreStr, fav, nonfav)
        if scoreFav.size == 0:
            continue
        #scoreNon = split_withlst(scoreStr, nonfav)
        sf, sn = matchSize(scoreFav.size, scoreNon.size)
        topFav = np.sort(scoreFav)[-sf:-1]
        topNon = np.array([]) if sn == 0 else np.sort(scoreNon)[-sn:-1]
        top = -1 if (topFav.size + topNon.size == 0) else round((sum(topFav) - sum(topNon))/(topFav.size + topNon.size),2)
        index = np.where(arr[:,0] == title)
        arr[index,1] = round(random.random()*10,2) if top <= 10 or top == float('inf') or top == float('-inf') else np.round(top,2)
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
        topFav = np.sort(scoreFav)[-sf:-1]
        topNon = np.array([]) if sn == 0 else np.sort(scoreNon)[-sn:-1]
        compatible = -1 if (topFav.size + topNon.size == 0) else round((sum(topFav) - sum(topNon))/(topFav.size + topNon.size),2)
        if compatible <= 0:
            compatible = 1
        result.append(compatible)          
        dbfetch.updateCompatibleFavoriteList(username, str(title), compatible)
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

def split_withlst(s,lst, lst2 = []):
    #split the string to list and remove all which position are not in lst (or lst2)
    arr = np.array([float(x) for x in s.split(',')])
    arr1 =  arr[np.array(lst) -1]
    if lst2.size != 0:
        arr2 = arr[np.array(lst2) - 1]
        return arr1[arr1 > 1], arr2[arr2 > 1]
    return arr1[arr1 > 1], np.array([])

def join_compatible(lst):
    return ','.join(str(x) for x in lst)

def matchSize(f,n):
    #return approriate size of favorite and nonfavorite title given split size
    rs = RECOMMENDATION_SIZE #for better looking
    if f < rs:
        #when favorite has too few title
        #ex: rs,f,n = 10,6,2 
        return f,0
    if f > 2*rs and n > rs:
        #when both has too many title
        #ex: 10,52,23
        return 2*rs, rs
    if f - n < rs:
        #when nonfavorite is more than favorite
        #ex: 10,11,7
        return f,f-rs
    if f - n > rs:
        #when favorite is more than nonfavorite
        #ex: 10,25,4
        return n+rs,n
    return 2*rs,rs

b = 7
a = b 
a - 1
print(b)