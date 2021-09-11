""" Referências:

https://python-mss.readthedocs.io/examples.html#multiprocessing - Seção PIL -> OpenCV/Numpy

"""
#############################################################
#                                                           #
#    (     (    (            (    (    (        )      )    #  
#   )\ )  )\ ) )\ )         )\ ) )\ ) )\ )  ( /(   ( /(     # 
#   (()/( (()/((()/( (   (  (()/((()/((()/(  )\())  )\())   #  
#    /(_)) /(_))/(_)))\  )\  /(_))/(_))/(_))((_)\  ((_)\    #  
#   (_))_|(_)) (_)) ((_)((_)(_)) (_)) (_))    ((_)  _((_)   #  
#   | |_  | _ \/ __|\ \ / / |_ _|/ __||_ _|  / _ \ | \| |   #  
#   | __| |  _/\__ \ \ V /   | | \__ \ | |  | (_) || .` |   #
#   |_|   |_|  |___/  \_/   |___||___/|___|  \___/ |_|\_|   #  
#                                                           #
#############################################################                                                   

import math
import keyboard
import mss.tools
import numpy as np
import serial
import torch

arduino = serial.Serial('COM17', 115200, timeout=0)

# modelo = torch.hub.load('Pasta do yolov5 na raiz', 'custom', path='Pasta com o arquivo .pt treinado', source='local', force_reload=True)

modelo = torch.hub.load('C:/yolov5-master', 'custom',
                        path='C:/Warzone.pt', source='local',
                        force_reload=True)

with mss.mss() as sct:

    # Use the first monitor, change to desired monitor number

    dimensions = sct.monitors[1]
    SQUARE_SIZE = 600

    # Part of the screen to capture

    monitor = {
        'top': int(dimensions['height'] / 2 - SQUARE_SIZE / 2),
        'left': int(dimensions['width'] / 2 - SQUARE_SIZE / 2),
        'width': SQUARE_SIZE,
        'height': SQUARE_SIZE,
        }

    while True:

        # Screenshot

        BRGframe = np.array(sct.grab(monitor))

        # Convert to format model can read

        RGBframe = BRGframe[:, :, [2, 1, 0]]

        # PASSING CONVERTED SCREENSHOT INTO MODEL

        results = modelo(RGBframe, size=600)

        modelo.conf = 0.6

        # READING OUTPUT FROM MODEL AND DETERMINING DISTANCES TO ENEMIES FROM CENTER OF THE WINDOW

        # Get number of enemies / num of the rows of .xyxy[0] array

        enemyNum = results.xyxy[0].shape[0]

        if enemyNum == 0:

            pass
        else:

            # Reset distances array to prevent duplicating items

            distances = []

            closest = 1000

            # Cycle through results (enemies) and get the closest

            for i in range(enemyNum):

                x1 = float(results.xyxy[0][i, 0])

                x2 = float(results.xyxy[0][i, 2])

                y1 = float(results.xyxy[0][i, 1])

                y2 = float(results.xyxy[0][i, 3])

                centerX = (x2 - x1) / 2 + x1

                centerY = (y2 - y1) / 2 + y1

                distance = math.sqrt((centerX - 300) ** 2 + (centerY
                        - 300) ** 2)

                distances.append(distance)

                # Get the shortest distance from the array (distances)

                if distances[i] < closest:

                    closest = distances[i]

                    closestEnemy = i

                # cv2.line(results.imgs[0], (int(centerX), int(centerY)), (300, 300), (255, 0, 0), 1, cv2.LINE_AA)

            # Getting the coordinates of the closest enemy

            x1 = float(results.xyxy[0][closestEnemy, 0])

            x2 = float(results.xyxy[0][closestEnemy, 2])

            y1 = float(results.xyxy[0][closestEnemy, 1])

            y2 = float(results.xyxy[0][closestEnemy, 3])

            Xenemycoord = (x2 - x1) / 2 + x1

            Yenemycoord = (y2 - y1) / 2 + y1

            # MOVING THE MOUSE

            difx = int(Xenemycoord - SQUARE_SIZE / 2)

            dify = int(Yenemycoord - SQUARE_SIZE / 2)

            if keyboard.is_pressed('/'):

                data = str(difx) + ':' + str(dify)

                arduino.write(data.encode())

                print(data)



            """Press "q" to quit
            if cv2.waitKey(25) & 0xFF == ord("q"):
                cv2.destroyAllWindows()
                break
            """
