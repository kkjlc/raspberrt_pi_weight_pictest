import os
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
from datetime import date
import time
import sys
from keras.models import load_model
import argparse
import pickle
import glob
import cv2
import subprocess

user_id1 = sys.argv[1]
path_name = "/home/pi/hx711py/Project/"
today = str(date.today())
timestamp = int(time.time())
EMULATE_HX711 = False

referenceUnit = 1

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711


def cleanAndExit():
    print("Cleaning...")


if not EMULATE_HX711:
    GPIO.cleanup()

print("Bye!")
sys.exit()

hx = HX711(5, 6)

hx.set_reading_format("MSB", "MSB")

# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
hx.set_reference_unit(449)
# hx.set_reference_unit(referenceUnit)

hx.reset()

hx.tare()

print("Tare done! Add weight now...")

# to use both channels, you'll need to tare them both
# hx.tare_A()
# hx.tare_B()

ck_list = []
i = 1

while True:
    if i > 10:
        break
    try:
        i += 1
        val = max(0, int(hx.get_weight()))
        print(val)

if val >= 10:
    ck_list.append(val)
    print('gathering data: {}'.format(ck_list))

if len(ck_list) >= 3:
    err = (ck_list[-1] - ck_list[-2]) / ck_list[-1]
    if err >= 0.03:
        pass
    else:
        print(val)  # final output

        #                 with open(path_name + "weight/{}.txt".format(today), "w") as f: #img_txt(save txt)
        #                     f.write(str(val))
        file_name = "{}_{}.jpg".format(today, i)
        p = subprocess.getoutput(
            "sudo fswebcam --no-banner -r 640x360 -S 10 -d /dev/video0 /home/pi/hx711py/Project/image/{}.jpg --no-banner".format(
                timestamp))  # image(save pic) #take the picture and save in the date folder with the name order of image
        #                 i+=1
        print(p)


#                 ck_list = []

hx.power_down()



hx.power_down()
hx.power_up()
time.sleep(0.1)


except (KeyboardInterrupt, SystemExit):
cleanAndExit()



# os.system("python3 train2.py")
b = glob.glob('/home/pi/hx711py/Project/image/{}.jpg'.format(timestamp))[-1]
image = cv2.imread(b)
output = image.copy()
image = cv2.resize(image, (32, 32))



# scale图像数据
image = image.astype("float") / 255.0

# 对图像进行拉平操作
image = image.flatten()
image = image.reshape((1, image.shape[0]))

# 读取模型和标签

print("------读取模型和标签------")
model = load_model('/home/pi/hx711py/Project/simple_nn3.h5')
lb = pickle.loads(open('/home/pi/hx711py/Project/simple_nn_lb3.pickle', "rb").read())

# 预测
preds = model.predict(image)

# 得到预测结果以及其对应的标签
i = preds.argmax(axis=1)[0]
label = lb.classes_[i]
print('辨識結果:', label)






# final result is here !!!!!!
print("{},{},{}".format(user_id1, label, val))


with open(path_name + "result/{}.txt".format(timestamp), "a") as f:
    f.write("{},{},{}".format(user_id1, label, val))