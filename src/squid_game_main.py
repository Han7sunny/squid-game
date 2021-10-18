# 오징어 게임 - main
import time
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

import odd_or_even_game
import dalgona_game
import mugunghwa_game

# 인트로 영상 출처 : https://www.youtube.com/watch?v=DcgwyJajOnw
intro = 'Intro'
cap = cv2.VideoCapture('./img/squid_game_intro.mp4')
if cap.isOpened():
    cv2.namedWindow(intro,cv2.WINDOW_NORMAL)
    cv2.moveWindow(intro,300,100)
    cv2.resizeWindow(intro,740,433)
    start_sec = time.time()
    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = int(1000/fps)
    while True:
        end_sec = time.time()
        if round(end_sec - start_sec) == 14:
            break
            
        ret, img = cap.read()
        if ret :
            cv2.imshow(intro,img)
            cv2.waitKey(delay)
        else:
            break
else:
    print("can't open intro video")
cap.release()
cv2.destroyAllWindows()

# 초기 화면
title = 'squid game'
img = cv2.imread('./img/squid.png') 

# menu
cv2.rectangle(img,(70 ,362),(220 ,392),(0,0,255),-1)
cv2.rectangle(img,(285 ,362),(420 ,392),(0,0,255),-1)
cv2.rectangle(img,(485, 362),(670 ,392),(0,0,255),-1)

img = Image.fromarray(img)
font = ImageFont.truetype('fonts/H2GTRE.TTF',15)
draw = ImageDraw.Draw(img)
draw.text((96,370),'구슬 홀짝 게임',font=font,fill=(255,255,255))
draw.text((315,370),'달고나 뽑기',font=font,fill=(255,255,255))
draw.text((500,370),'무궁화 꽃이 피었습니다.',font=font,fill=(255,255,255))
img = np.array(img)    
cv2.namedWindow(title,cv2.WINDOW_NORMAL)
cv2.moveWindow(title,280,100)
cv2.imshow(title, img)
img_copy = img.copy()

# game main
def select_menu(event, x, y, flags, param): 
    global img,img_copy
    if event == cv2.EVENT_LBUTTONDOWN:
        if 70 <= x <= 220 and 362 <= y <= 392:
            odd_or_even_game.game_start()
            cv2.imshow(title, img)
        elif 285 <= x <= 420 and 362 <= y <= 392:
            img = Image.fromarray(img)
            font = ImageFont.truetype('fonts/H2GTRE.TTF',15)
            draw = ImageDraw.Draw(img)
            draw.text((160,330),'달고나 뽑기를 진행할 도형을 빨간색 도형 중 선택하세요.',font=font,fill=(0,0,255))
            img = np.array(img)    
            cv2.imshow(title, img)
        elif 485 <= x <= 670 and 362 <= y <= 392:
            img = Image.fromarray(img)
            font = ImageFont.truetype('fonts/H2GTRE.TTF',15)
            draw = ImageDraw.Draw(img)
            draw.text((130,330),'무궁화 꽃이 피었습니다 게임이 로딩 중입니다. 잠시만 기다려주세요',font=font,fill=(0,0,255))
            img = np.array(img)
            cv2.imshow(title, img)
            mugunghwa_game.game_start()
        elif 150 <= x <= 220 and 125 <= y <= 190: # dalgona - circle
            dalgona_game.game_start('circle')
            cv2.imshow(title, img)
        elif 245 <= x <= 310 and 150 <= y <= 210: # dalgona - triangle
            dalgona_game.game_start('triangle')
            cv2.imshow(title, img)         
        elif 550 <= x <= 616 and 205 <= y <= 265: # dalgona - square
            dalgona_game.game_start('square')
            cv2.imshow(title, img)
        else:
            pass
    img = img_copy.copy()
cv2.setMouseCallback(title, select_menu) 

while True:
    if cv2.waitKey(0) & 0xFF == 27:    
        break
    else:
        pass
cv2.destroyAllWindows() 