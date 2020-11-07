from keras.models import load_model
import time
import argparse
import pickle
import sys
import os
import subprocess
import cv2
from datetime import date
import json

today = str(date.today())
path_name = "/home/pi/img_txt/"
print(path_name + today)
try:
    os.mkdir(path_name + today)  ######### name each folder per day
except:
    print('folder exists')

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
hx.set_reference_unit(101.2)
hx.reset()
hx.tare()

print("Tare done! Add weight now...")

ck_list = []
i = 1

while True:
    try:
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
            with open(path_name + today + "/{}_{}.txt".format(today, i), "w") as f:  # img_txt(save txt)
                f.write(str(val))

            p = subprocess.getoutput("sudo fswebcam /home/pi/image/{}_{}.jpg".format(today,i))

            i += 1
            print(p)

            ck_list = []
            #開始圖片訓練
            image1 = cv2.imread("/home/pi/image/{}_{}.jpg".format(today,i))
            output = image1.copy()
            image1 = cv2.resize(image1, (32, 32))
            image1 = image1.astype("float") / 255.0
            image1 = image1.flatten()
            image1 = image1.reshape((1, image1.shape[0]))
            print("------读取模型和标签------")
            model = load_model('C:/Users/Big data/recipe_work/simple_nn3.h5')
            lb = pickle.loads(open('C:/Users/Big data/recipe_work/simple_nn_lb3.pickle', "rb").read())
            preds = model.predict(image1)
            i = preds.argmax(axis=1)[0]
            label = lb.classes_[i]
            print('辨識結果:', label)
            today = str(date.today())
            a = time.localtime()
            nowtime = str(time.mktime(a))
            path_name = "/home/pi/image/"
            try:
                os.mkdir(path_name + today + '2')
            except:
                print('folder exists')
            with open(path_name + today + '3' + "/{}.json".format(nowtime), "w") as dump_f:
                json.dump(dump_f)

            while True:
                hx.power_down()
                hx.power_up()
                ck_val = int(hx.get_weight())
                if ck_val > 10:
                    print('ck_val: {}, val: {}'.format(ck_val, val))
                    print('please put the next item.')
                    time.sleep(3)
                    continue
                else:
                    break
            hx.power_down()
            hx.power_up()
            time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()