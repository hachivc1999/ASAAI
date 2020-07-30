from database import dbfetch
import numpy as np
import random

#second part of the recommnendation system
#please check the first part (file engine.py) if you are not familiar with the system 
#this part deals with user recommendation by doing fast calculations based on similarity matrix

#global declaration
RECOMMENDATION_SIZE = 5 #size of recommendation user wants to get
DEFAULT_SCORE = 50. #the default score when there is no recommendation
FAST_RECOMMENDATION_THRESHOLD = 400 #the threshold where suboptimal recommendation is preferred

def generateRecommendation(username):
    #generate recommendations for a user
    #this function receives input as username and return a list of (titleId, compatibleScore) ranked by compatibleScore
    #there are two situations for recommendations, when user has not favored one title yet and when user has liked at least one title
    #favorite and nonFavorite are two numpy arrays, storing id of titles in favorite and not favorite list
    favorite = generateFavList(username)
    nonFavorite = generateNonFavList(username)
    if favorite.size == 0:
        return generateDefaultRecommendation(nonFavorite)
    elif favorite.size < FAST_RECOMMENDATION_THRESHOLD:
        return generateFastRecommendation(favorite, nonFavorite)
    else:  
        #The recommendList is title Ids which are not in favorite or nonFavorite
        recommendList = [x[0] for x in dbfetch.getIdAllTitle() if x[0] not in np.concatenate((favorite,nonFavorite))]
        return generateNormalRecommendation(favorite, nonFavorite, recommendList)   
    
def generateDefaultRecommendation(nonfav):
    #the default recommendation
    #for distinguishable reason, every user should return a list of titles by random
    #compatibleScore of these titles are DEFAULT_SCORE
    recommendlist = [x[0] for x in dbfetch.getIdAllTitle() if x[0] not in nonfav]
    if len(recommendlist) > RECOMMENDATION_SIZE:
        recommendlist = random.sample(recommendlist, RECOMMENDATION_SIZE)
    return np.array([(x,DEFAULT_SCORE) for x in recommendlist])
 
def generateFastRecommendation(fav, nonfav):
    #the suboptimal case of recommendation
    #it is much faster since only 100 titles are calculated instead of recommendList size
    #this function is purely for testing on a slow server.
    recommendList = [x[0] for x in dbfetch.getIdAllTitle() if x[0] not in np.concatenate((fav,nonfav))] 
    randomList = random.sample(recommendList, 10*RECOMMENDATION_SIZE)
    return generateNormalRecommendation(fav, nonfav, randomList)
    
    
def generateNormalRecommendation(fav, nonfav, lst):
    #the normal case of recommendation
    #the algorithm works as follow:
    #for every title not in either favorite or nonfavorite list, select X titles with highest compatible from favorite
    #and Y titles with highest compatible from nonfavorite. X,Y are determined by size of favorite and nonfavorite list
    #the compatibleScore of the title is a function of sum of compatibleScore in X titles minus compatibleScore in Y titles
    #if the calculated compatibleScore of a title is lower than 10, it will become 10
    #RECOMMENDATION_SIZE highest compatibleScore will be returned
    recommendSize = len(lst)
    if recommendSize == 0:
        return np.array([])
    arr = np.zeros((recommendSize,2))
    compatibleList = dict(dbfetch.getSomeRecommendation(lst))
    i = 0
    for title in lst:
        scoreStr = compatibleList.get(title)
        scoreFav,scoreNon = split_withlst(scoreStr, fav,nonfav)
        sf, sn = matchSize(scoreFav.size, scoreNon.size)
        topFav = scoreFav if sf >= scoreFav.size else -np.sort(np.partition(-scoreFav,sf)[:sf])
        topNon = scoreNon if sn >= scoreNon.size else -np.sort(np.partition(-scoreNon,sn)[:sn])
        score = geometricSeriesDualAverage(topFav,topNon)
        arr[i] = (title,10) if score <= 10 else (title,np.round(score,2))
        i += 1
    return arr[arr[:,1].argsort()[::-1]][:RECOMMENDATION_SIZE]
    
def updateCompatible(username, t = 0):
    #update compatibleScore of favorite titles of a user
    #the algorithm is nearly the same as recommendation:
    #for every title in favorite list, select X titles with highest compatible from favorite but not itself
    #and Y titles with highest compatible from nonfavorite. X,Y are determined by size of favorite and nonfavorite list
    #the compatibleScore of the title is the sum of compatibleScore in X titles minus compatibleScore in Y titles
    #if the favorite list has size of 0, return an empty list
    #if the favorite list has size of 1, return DEFAULT_SCORE
    #the function will update the calculated compatibleScore into the database for future use
    #the function will also return the list of compatibleScore as user called
    favorite = generateFavList(username)
    if favorite.size == 0:
        return np.array([])
    if favorite.size == 1:
        return np.array([favorite[0],DEFAULT_SCORE])
    lst = t if t.size != 0 else favorite
    arr = np.zeros((lst.size,2))
    nonFavorite = generateNonFavList(username)
    compatibleList = dict(dbfetch.getSomeRecommendation(lst))
    for i in range(0,lst.size):
        title = lst[i]
        scoreStr = compatibleList.get(title)
        scoreFav, scoreNon = split_withlst(scoreStr, favorite, nonFavorite)
        sf, sn = matchSize(scoreFav.size, scoreNon.size)
        topFav = scoreFav if sf >= scoreFav.size else -np.sort(np.partition(-scoreFav,sf)[:sf])
        topNon = scoreNon if sn >= scoreNon.size else -np.sort(np.partition(-scoreNon,sn)[:sn])
        score = geometricSeriesDualAverage(topFav,topNon)
        score = 10 if score < 10 else np.round(score,2)
        arr[i] = (title,score)
    s = arr.tostring()
    dbfetch.updateCompatibleUser(username, s)
    return arr

def generateFavList(username):
    #return a numpy array containing id of favorite title
    return np.array([int(x[0]) for x in dbfetch.getIdFavoriteList(username)])

def generateNonFavList(username):
    #return a numpy array containing id of nonfavorite title
    return np.array([int(x[0]) for x in dbfetch.getIdNotFavoriteList(username)])

def generateWatchingList(username):
    #return a numpy array containing id of watching title
    return np.array([int(x[0]) for x in dbfetch.getIdWatchingList(username)])

def generateStatusCode(username, title):
    #return status code as an integer representing the title status (like,dislike etc...)
    #crazy conversion:
    #normal condition - 0
    #in favorite - 1
    #in nonfavorite - 2
    #in favorite and watching - 3
    #in nonfavorite and watching - 4
    fil = generateFilter(username)
    return round(sum([x+0.6 for x in range(0,3) if title in fil[x]]))

def generateFilter(username):
    #generate a filter for status code calculation
    return [generateFavList(username), generateNonFavList(username), generateWatchingList(username)]

def generateWatchingScore(username, ids):
    #generate watching score for every title
    s = dbfetch.getCompatible(username)
    if not s:
        return np.array([]), np.array([])
    s = s[0][0]
    arr = np.frombuffer(s, dtype = float)
    mask = np.isin(arr[::2],ids)
    return arr[::2][mask],arr[1::2][mask]

def generateRandomTitle():
    #generate random title
    titles = [int(x[0]) for x in dbfetch.getIdAllTitle()]
    if len(titles) > RECOMMENDATION_SIZE:
        titles = random.sample(titles, RECOMMENDATION_SIZE)
    return titles

def split_compatible(s):
    #remember we allocates the compatible as string in part 1?
    #here we convert it back to numpy array
    return np.array([int(x) for x in s.split(',')])

def split_withlst(s,lst, lst2 = np.array([])):
    #further optimizing the code by spliting and removing unwanted compatibleScore
    arr = np.frombuffer(s, dtype = float)
    if lst2.size != 0:
        return arr[1::2][np.in1d(arr[::2],lst,assume_unique = True)], arr[1::2][np.in1d(arr[::2],lst2,assume_unique = True)]
    return arr[1::2][np.in1d(arr[::2],lst,assume_unique = True)], np.array([])

def split_withoutlst(s,lst):
    #split the string to list and remove all which position are in lst
    arr = np.frombuffer(s, dtype = float)
    _,con,_ = np.intersect1d(arr[::2],lst, return_indices = True, assume_unique = True)
    return np.delete(arr,[con*2,con*2+1])

def join_compatible(lst):
    #join back?
    return ','.join(str(x) for x in lst)

#an average calculation which works with strange range output
#example: array like 99 9 9 will return 39 with normal average. However, it isn't good
#apply this conversion will return (99/3 + 9/9 + 9/27)*2 + 9/27 = 69 
#at the worst case it will have same compatible: (81/3 + 81/9 + 81/27) * 2 + 81/27 = 81
def geometricSeriesAverage(arr):
    if arr.size == 0:
        return 0
    for i in range(0, arr.size):
        arr[i] *= (1/3)**(i+1)
    return sum(arr)*2 + arr[-1]

#calculating average on 2 set
def geometricSeriesDualAverage(arr, arr2):
    if arr2.size == 0:
        return geometricSeriesAverage(arr)
    #since nonFavorite list will always has smaller size than favlist, this is doable
    arr[:arr2.size] -= arr2
    return geometricSeriesAverage(arr)

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

def makeRange(x,y = None):
    #a function same as range() for python but return numpy array
    return np.arange(x,y) if y else np.arange(0,x)
