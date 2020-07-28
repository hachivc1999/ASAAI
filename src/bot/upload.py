import requests

TOKEN = 'eZGcnkJKIzZvpcZ0hSzzarEX1th6exKgJ0vpbKMD3y8wFIfXVr3DayYkbQT2ym8s'


def upload(path):
    url = 'https://hachihachi.pythonanywhere.com/v1/upload'  # DO NOT CHANGE
    # url = 'http://127.0.0.1:5000/upload'
    file = 'file'  # DO NOT CHANGE
    ids = 'id'  # DO NOT CHANGE

    name = ''  # add name if required
    dirr = path + name if name != '' else path
    files = {file: open(dirr, 'rb')}
    payload = {ids: TOKEN}
    print(requests.post(url, files=files, data=payload))


directory = 'D:/Programming/Pycharm Project/assai/assai_bot/doithuong.json'  # INSERT PATH HERE
upload(directory)
