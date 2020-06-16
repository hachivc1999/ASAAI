from database import dbfetch
import numpy as np
import random

#second part of the recommnendation system
#please check the first part (file engine.py) if you are not familiar with the system 
#this part deals with user recommendation by doing fast calculations based on similarity matrix

#global declaration
RECOMMENDATION_SIZE = 5 #size of recommendation user wants to get
DEFAULT_SCORE = 50. #the default score when there is no recommendation

def generateRecommendation(username):
    #generate recommendations for a user
    #this function receives input as username and return a list of (titleId, compatibleScore) ranked by compatibleScore
    #there are two situations for recommendations, when user has not favored one title yet and when user has liked at least one title
    #favorite and nonFavorite are two numpy arrays, storing id of titles in favorite and not favorite list
    favorite = generateFavList(username)
    nonFavorite = generateNonFavList(username)
    if favorite.size == 0:
        return generateDefaultRecommendation(nonFavorite)
    else:
        return generateNormalRecommendation(favorite, nonFavorite)
    

def generateDefaultRecommendation(nonfav):
    #the default recommendation
    #for distinguishable reason, every user should return a list of titles by random
    #compatibleScore of these titles are DEFAULT_SCORE
    recommendlist = [x[0] for x in dbfetch.getAllTitle() if x[0] not in nonfav]
    if len(recommendlist) > RECOMMENDATION_SIZE:
        recommendlist = random.sample(recommendlist, RECOMMENDATION_SIZE)
    return [(x,DEFAULT_SCORE) for x in recommendlist]
 
def generateNormalRecommendation(fav, nonfav):
    #the normal case of recommendation
    #the algorithm works as follow:
    #for every title not in either favorite or nonfavorite list, select X titles with highest compatible from favorite
    #and Y titles with highest compatible from nonfavorite. X,Y are determined by size of favorite and nonfavorite list
    #the compatibleScore of the title is the sum of compatibleScore in X titles minus compatibleScore in Y titles
    #if the calculated compatibleScore of a title is lower than 10, it will become 1
    #RECOMMENDATION_SIZE highest compatibleScore will be returned
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
        sf, sn = matchSize(scoreFav.size, scoreNon.size)
        topFav = np.sort(scoreFav)[-sf:-1]
        topNon = np.array([]) if sn == 0 else np.sort(scoreNon)[-sn:-1]
        top = -1 if (topFav.size + topNon.size == 0) else round((sum(topFav) - sum(topNon))/(topFav.size + topNon.size),2)
        index = np.where(arr[:,0] == title)
        arr[index,1] = 1 if top <= 10 or top == float('inf') or top == float('-inf') else np.round(top,2)
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

def split_compatible(s):
    #remember we allocates the compatible as string in part 1?
    #here we convert it back to numpy array
    return np.array([int(x) for x in s.split(',')])

def split_withlst(s,lst, lst2 = []):
    #further optimizing the code by spliting and removing unwanted compatibleScore
    #but how? notice that in part 1 we join ALL values of a row into string, therefore the order after join is the same as id order
    arr = np.array([float(x) for x in s.split(',')])
    arr1 =  arr[np.array(lst) -1]
    if lst2.size != 0:
        arr2 = arr[np.array(lst2) - 1]
        return arr1[arr1 > 1], arr2[arr2 > 1]
    return arr1[arr1 > 1], np.array([])

def join_compatible(lst):
    #join back?
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
