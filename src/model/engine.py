from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from nltk.stem.porter import PorterStemmer
import util, nltk, string, sqlite3
from database import dbfetch
import pandas as pd
import numpy as np

#The first part of the recommendation system
#Where the system calculates the similarities between each title using Tf-idf tokenized with nltk and cosine similarities
#Since the project is real time recommendation, it is wise not to redo
#The only time this file is called is when the bot upload a new title, the matrix needs to be recalculated again
#The executioni time is not too bad, around 30 seconds for 200 titles
class Engine():
    matrix = []
    def __init__(self):
        #initialize the weight of each similarity and max features for tokenizer
        self.WEIGHT_NAME = 0.1
        self.WEIGHT_PRODUCER = 0.2
        self.WEIGHT_DESCRIPTION = 0.1
        self.WEIGHT_TAGS = 0.6
        self.WEIGHT_TOTAL = self.WEIGHT_NAME + self.WEIGHT_PRODUCER + self.WEIGHT_DESCRIPTION + self.WEIGHT_TAGS
        self.max_features = 1000
        
    def preprocess(self, lst):
        #preprocess the data by turning to lowercase and removing punctuation
        return [x.lower().replace("[0-9]",'num ').translate(str.maketrans('', '', string.punctuation)) for x in lst]
    
    def tf_idf_transform(self, lst):
        #return cosine similarity from tf idf
        tf = TfidfVectorizer(tokenizer = self.tokenizer, max_features = self.max_features)
        arr = tf.fit_transform(lst)
        return linear_kernel(arr,arr)
    
    def readSqlite(self, path, query):
        #read the query from database and return
        cur = sqlite3.connect(path)
        df = pd.read_sql_query(query, cur)
        cur.commit()
        cur.close()
        return df
        
    def train(self, path):
        #where the training is done
        #firstly, it needs to get the data from database
        #luckily, pandas support reading from sqlite to Dataframe so the steps aren't that hard
        #read from sqlite to dataframe
        if path is None:
            return "Path not defined"
        query = "SELECT id, name, transName, producer, description FROM AnimeModel"
        df = self.readSqlite(path, query)
        
        #add column tags and join name with transName
        df['tags'] = [' '.join(util.jsonTags(dbfetch.getTag(i))) for i in df['id']]
        df['name'] = df['name'] + ' ' + df['transName']
        
        #making the tf-idf cosine similarity model
        name = self.preprocess(df['name'])
        nametf = np.array(self.tf_idf_transform(name))
        producer = self.preprocess(df['producer'])
        prodtf = np.array(self.tf_idf_transform(producer))
        description = self.preprocess(df['description'])                      
        desctf = np.array(self.tf_idf_transform(description))
        tagtf = np.array(self.tf_idf_transform(df['tags']))
        
        #calculate the final similarity matrix based on each matrix weight
        #after that, convert each row of the matrix to a string and insert to database for part 2, generating recommendations
        total_similarity = np.round((desctf*self.WEIGHT_DESCRIPTION + nametf*(self.WEIGHT_NAME) + prodtf*self.WEIGHT_PRODUCER + tagtf*self.WEIGHT_TAGS)*100/self.WEIGHT_TOTAL,5)
        #remove low similarity between titles
        for i in range(0,len(total_similarity)):
            arr = np.vstack((np.arange(1,total_similarity[i].size + 1),total_similarity[i])).T
            arr = arr[np.logical_and((arr[:,1] >= 10), (arr[:,1] < 100)),:]
            dbfetch.updateRecommendation(i + 1, arr.tostring())
        
    def tokenizer(self, text):
        #this function allows to tokenize and stem the text
        words = nltk.word_tokenize(text)    
        ps = PorterStemmer()
        return [ps.stem(w) for w in words]
