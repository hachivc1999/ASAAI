'''
Created on 15 May 2020

@author: asus
'''
import pandas as pd
import numpy as np
import sqlite3

class Reader:
    def __init__(self, frame = None, path = None):
        self.frame = frame
        self.path = path
        
    def readcsv(self, cols, names, dtype = np.str):
        frame = pd.read_csv(self.path, usecols = cols, names = names, encoding = 'latin1')
        self.frame = frame
    
    def readsqlite(self, path, query):
        cur = sqlite3.connect(path)
        self.frame = pd.read_sql_query(query, cur)
        cur.commit()
        cur.close()
        
    def addColumn(self, colname, colval):
        self.frame[colname] = colval
        
    def write(self, filename):
        self.frame.to_csv(filename, encoding='utf-8')
        
    def merge(self, index, columns, values):
        pv = pd.pivot_table(self.frame, index = index, columns = columns, values = values)
        frame = pd.DataFrame(pv.to_records())
        self.frame = frame.fillna(0, inplace = True)
        
    def getFrame(self):
        return self.frame
    
    def getColumn(self, col):
        return self.frame[col]
    def getColumnList(self):
        return self.frame.columns.tolist()
    def getRow(self,row):
        return self.frame[row]
    def getRowList(self):
        return self.frame.index.tolist()
    def getCell(self,row,column):
        return self.frame.iloc[row,column]
    def getAllItem(self):
        return self.frame.values