import os
import json
from datetime import date
import time
import sys


user_id1 = sys.argv[1]
path_name = "/儲存/"
try:
    os.mkdir(path_name + 'user_id')  ######### name each folder per day
except:
    print('folder exists')
with open(path_name + 'user_id' +"/{}.txt".format(user_id1), 'w') as f:
    f.write(user_id1)

os.system("python weight.py")
os.system("python 圖片測試.py")


x = os.listdir('user_id/*')[-1]
y = os.listdir('image/*')[-1]
z = os.listdir('weight/*')[-1]

with open(x, 'r',encoding='UTF-8') as f:
    load_dict1 = f.read()
    print(load_dict1)
with open('y', 'r',encoding='UTF-8') as g:
    load_dict2 = g.read()
    print(load_dict2)
with open('z', 'r',encoding='UTF-8') as h:
    load_dict3 = h.read()
    print(load_dict3)
today = str(date.today())
a = time.localtime()
nowtime = str(time.mktime(a))

path_all = ''
try:
    os.mkdir(path_all + 'allprofile')  ######### name each folder per day
except:
    print('folder exists')
with open(path_all + 'allprofile' +"/{}.json".format(nowtime),"w") as dump_f:
    json.dump(load_dict1,load_dict2,load_dict3,today)
