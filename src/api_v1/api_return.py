#Handling the errors and messages of the api
class Error():
    def __init__(self,code,mess):
        self.code = code
        self.message = mess
    def get(self):
        return self.message,self.code

class Message():
    def __init__(self,mess):
        self.message = mess
    def get(self):
        return self.message
    
#--------------ERROR--------------------------
def bad_request():
    return Error(400,'Bad request')
def unauthorized():
    return Error(401, 'Access denied')
def page_not_found(e):
    return Error(404, 'The requested {} cannot be found'.format(e))
def not_allowed():
    return Error(405, 'Method not allowed')
def conflict(u):
    return Error(409,'User {} already exists'.format(u))
def maintenance():
    return Error(503,'Server in maintenance')
#---------------RETURN MESSAGE-----------------
def register_success(tk):
    return Message(tk)

def login_success(tk):
    return Message(tk)

def favorite_success():
    return Message(1)

def favorite_remove_success():
    return Message(-1)

def unfavorite_success():
    return Message(2)

def unfavorite_remove_success():
    return Message(-2)

def watchlist_success():
    return Message(2)

def watchlist_remove_success():
    return Message(-2)
