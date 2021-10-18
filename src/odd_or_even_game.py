# 구슬 홀짝
# 총 구슬 개수가 20이 될 때까지 반복

import cv2
import numpy as np
from PIL import ImageFont, ImageDraw,Image

def game_start():

    global title1, other_total, my_total, my_marble, temp_my_total, click, play_layer

    # 이미지 출처 :《백년 쓰는 관절 리모델링》
    img_m = cv2.imread('./img/my_hand.jpg')
    img_l = cv2.imread('./img/other_lock.jpg')
    img_o = cv2.imread('./img/other_open.jpg')

    merged = np.hstack((img_l, img_m))

    title1 = 'odd or even'

    # title layer
    title_layer = merged.copy()
    cv2.putText(title_layer, 'Start!', (170,150), cv2.FONT_HERSHEY_COMPLEX, 3, (0,0,255), 6)
    cv2.putText(title_layer, 'Press any button to continue.', (140,180), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,0,0), 1)

    cv2.namedWindow(title1, cv2.WINDOW_NORMAL)
    cv2.moveWindow(title1, 310,240) 
    cv2.imshow(title1, title_layer)
    cv2.waitKey()

    # 베팅 결과
    result = ''

    # odd / even 선택 후 click 불가능
    click = True

    # 구슬 보유 개수
    other_total = 10
    my_total = 10
    my_marble = 0
    temp_my_total = my_total

    # 시작 화면 (2)
    sub_title_layer = merged.copy()
    cv2.putText(sub_title_layer, 'Computer: {}'.format(other_total), (80,30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,0,0), 2)
    cv2.putText(sub_title_layer, 'User: {}'.format(my_total), (420,30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,0,0), 2)

    cv2.imshow(title1, sub_title_layer)

    play_layer = merged.copy() # 베팅하는 화면
    text_layer = merged.copy() # 베팅 구슬 카운트 표시 화면

    # 베팅 화면 출력
    def bet_screen(bet):
        cv2.putText(betting_screen, '{}?'.format(bet), (270,100), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
        cv2.putText(betting_screen, ' -- Press any button to continue. --', (160,205), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,0), 1)
        return betting_screen

    # 경고 팝업
    def warning_pop(w_size,org,font_size,text):
        img = np.full(w_size,0,np.uint8) 
        img = Image.fromarray(img)
        font = ImageFont.truetype('fonts/H2GTRE.TTF',font_size)
        draw = ImageDraw.Draw(img)
        draw.text(org,text, font = font,fill=(0,0,255)) 
        warning = np.array(img)
        return warning

    # 결과 화면
    def result_screen(text):
        global after_open, other_total, my_total 
        
        if text == 'Correct':
            math = 1
        else:
            math = -1 
        

        after_open = np.hstack((img_op, play_layer[:,321:].copy())) 
        cv2.putText(after_open, text, (155,180), cv2.FONT_HERSHEY_COMPLEX, 3, (0,0,255), 6)

        cv2.putText(after_open, '({:+2d})'.format(change_marble * (-math)), (265, 30), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255), 2)
        cv2.putText(after_open, '({:+2d})'.format(change_marble * math), (540,30), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255), 2)

        cv2.putText(after_open, 'Computer: {}'.format(other_total), (80,30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,0,0), 2)
        cv2.putText(after_open, 'User: {}'.format(my_total), (420,30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,0,0), 2)
        cv2.putText(after_open, ' -- Press any button to continue. --', (160,205), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,0), 1)
        return after_open

    # 마우스 이벤트
    def onMouse(event, x, y, flags, param):
        global other_total, my_total, my_marble, title1, play_layer, text_layer, temp_my_total, click
    
        color = tuple(np.random.randint(0,256) for _ in range(3))
        if event == cv2.EVENT_LBUTTONDOWN:
            
            if click: # odd 또는 even 선택한 뒤 베팅한 구슬 개수를 변경할 수 없도록
                
                if my_total > 0 and temp_my_total > 0:               # 보유 구슬이 0 ~ my_total개 일 때

                    if 345 <= x <= 475 and 70 <= y <= 125:           # 구슬 위치 영역
                        cv2.circle(play_layer, (x,y), 7, color, -1)  # Random color

                        my_marble += 1                               # 현재 나의 구슬 개수
                        temp_my_total -= 1                           # 베팅하고 남은 구슬 개수

                        text_layer = play_layer.copy()

                        cv2.putText(text_layer, 'Computer: {}'.format(other_total), (80,30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,0,0), 2)
                        cv2.putText(text_layer, 'User: {}'.format(temp_my_total), (420,30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,0,0), 2)

                        cv2.imshow(title1, text_layer)

                    else:
                        cv2.namedWindow('warning', cv2.WINDOW_NORMAL)
                        cv2.moveWindow('warning', 285,300) 
                        cv2.imshow('warning',warning_pop((50,300,3),(50,18),10,'오른쪽 손바닥 위에 본인의 구슬을 놓아주세요.'))
                        cv2.waitKey()
                        cv2.destroyWindow('warning')

                else:
                    # 경고           
                    cv2.namedWindow('warning', cv2.WINDOW_NORMAL)
                    cv2.moveWindow('warning', 285,300) 
                    cv2.imshow('warning',warning_pop((50,400,3),(10,10),10,'더 놓을 수 있는 구슬이 없습니다.\n상대방 구슬 개수가 홀수(odd)라면 o, 짝수(even)라면 e를 입력해주세요.'))
                    cv2.waitKey()
                    cv2.destroyWindow('warning') 
            
    cv2.setMouseCallback(title1, onMouse)


    while my_total > 0 and other_total > 0:

        other_marble = np.random.randint(1, other_total + 1) # 상대방 구슬 개수

        # print("술래:", other_marble)                       # 확인용 출력
        
        while True:
            key = cv2.waitKey(0) & 0xFF                    # 구슬 입력하고 상대편 보려고 할 때
            betting_screen = text_layer.copy()

            if key == ord('o'):     # odd 홀
                cv2.imshow(title1, bet_screen('Odd'))
                click = False 
                cv2.waitKey()

                if other_marble % 2 != 0:
                    other_total -= my_marble
                    my_total += my_marble
                    result = 'Correct'              # 승리
                else:
                    my_total -= other_marble 
                    other_total += other_marble
                    result = 'Wrong'             # 패배
                break
            
            elif key == ord('e'):    # even 짝
                cv2.imshow(title1, bet_screen('Even'))
                click = False
                cv2.waitKey()
            
                if other_marble % 2 == 0:
                    other_total -= my_marble
                    my_total += my_marble
                    result = 'Correct'              # 승리
                else:
                    my_total -= other_marble
                    other_total += other_marble
                    result = 'Wrong'                # 패배
                break
                            
            else:
                # 경고창
                cv2.namedWindow('warning', cv2.WINDOW_NORMAL)
                cv2.moveWindow('warning', 285,300) 
                cv2.imshow('warning',warning_pop((50,380,3),(20,18),10,'상대방 구슬 개수가 홀수(odd)라면 o, 짝수(even)라면 e를 입력해주세요.'))
                cv2.waitKey()
                cv2.destroyWindow('warning')
                
        # # 확인용 출력
        # print("베팅:", my_marble)
        # print('total other: ',other_total,',total my: ',my_total)

        click = True
        
        img_op = img_o.copy()
        
        if other_total < 0 :
            other_total = 0
        elif other_total > 20:
            other_total = 20
        cv2.putText(img_op, 'Computer: {}'.format(other_total), (80,30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,0,0), 2)

        for i in range(other_marble): 
            color = tuple(np.random.randint(0,256) for _ in range(3))
            cv2.circle(img_op,(195 + (i % 5) * 17, 70 + 20 * (i // 5)), 7, color, -1)
        
        if my_total < 0 :
            my_total = 0
        elif my_total > 20:
            my_total = 20

        if result == 'Correct' : 
            change_marble = my_marble
        else:
            change_marble = other_marble
        
        cv2.imshow('odd or even result', result_screen(result))
        cv2.moveWindow('odd or even result', 310,240)     
        cv2.waitKey(0)
        cv2.destroyWindow('odd or even result')
        
        # 베팅 초기화
        my_marble = 0
        temp_my_total = my_total # 생략 가능
        play_layer_init = merged.copy()
        play_layer = merged.copy()
        cv2.putText(play_layer_init, 'Computer: {}'.format(other_total), (80,30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,0,0), 2)
        cv2.putText(play_layer_init, 'User: {}'.format(my_total), (420,30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,0,0), 2)
        cv2.imshow(title1, play_layer_init)

    else: 
        if my_total > other_total:
            fin = np.full_like(merged, (0,0,0))
            cv2.putText(fin, 'YOU WIN', (95,150), cv2.FONT_HERSHEY_COMPLEX, 3, (0,0,255), 6)
            cv2.imshow(title1, fin)
            cv2.moveWindow(title1, 310, 240) 
            cv2.waitKey(0)
            cv2.destroyWindow(title1)
        else:
            fin = np.full_like(merged, (0,0,0))
            cv2.putText(fin, 'YOU LOSE', (90,150), cv2.FONT_HERSHEY_COMPLEX, 3, (0,0,255), 6)
            cv2.imshow(title1, fin)
            cv2.moveWindow(title1, 310, 240) 
            cv2.waitKey(0)
            cv2.destroyWindow(title1)
