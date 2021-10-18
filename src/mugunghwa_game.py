import cv2 as cv
import numpy as np
import time
from PIL import ImageFont, ImageDraw,Image

def game_start():
    global on, result, get_xy, center_x, center_y, frame_width, frame_height

    on = 1          # 전체 플레이
    start_condition = 1  # 준비 여부
    ready = 0       # 준비화면 출력
    body = 0        # 본게임 시작
    body_sub = 1    # 본게임 시작 시간 가져오기
    body_time = 0                        # 본 플레이 타이머

    time_limit= 30    # 플레이 제한시간
    result = 0        # 게임 결과 저장
    green = (50,150,45)
    red = (25,25,195)

    get_xy = True # 1 -> True

    def ask_popup():  # 종료/재시작 선택
        img = np.full((70,500,3),(255,255,255),np.uint8)
        img = Image.fromarray(img)
        font = ImageFont.truetype('fonts/gulim.ttc',15)
        draw = ImageDraw.Draw(img)
        draw.text((10,10), '종료 하시겠습니까? (y/n)', font=font,fill=(0,0,255))
        draw.text((10,30), '   -- y: 종료', font=font,fill=(0,0,255))
        draw.text((10,50), '   -- n: 이어서 하기', font=font,fill=(0,0,255))
        popup = np.array(img)
        cv.imshow('warning', popup)
        key1 = cv.waitKey(0) & 0xFF
        cv.destroyWindow('warning')
        if key1 == ord('y'):
            return 1
        elif key1 == ord('n'):
            return 0
        else:
            return 1

    def alert(text):  # 객체 추적 불가 시 안내창
        img = np.full((70,500,3),(255,255,255),np.uint8)
        img = Image.fromarray(img)
        font = ImageFont.truetype('fonts/gulim.ttc',15)
        draw = ImageDraw.Draw(img)
        draw.text((95,10),text, font=font,fill=(0,0,255))
        
        popup = np.array(img)
        cv.imshow('warning', popup)
        key1 = cv.waitKey(0) & 0xFF
        cv.destroyWindow('warning')
        if key1 == 27:  # Esc
            return 0
        else: 
            return 1

    def detecting(param, sec): # 멈춤 조건 감지 함수
        global get_xy, center_x, center_y, result, on, frame_width, frame_height, init_xy
        detct_on = param
        if detct_on:                # 움직임 판독
            while get_xy:   # 멈춤 시>> 첫 위치 가져오기
                init_xy = np.array((center_x, center_y))
                get_xy = False
            diff = abs(init_xy - np.array((center_x, center_y)))
            if sum(diff) > 13:
                print('초기위치: {}\n검출위치: {}'.format(init_xy, sum(diff)))
                cv.putText(img_color, 'Motion', ((frame_width-45)//2-30, frame_height//2), font, 1, (0,255,255), 1)
                cv.putText(img_color, 'detected', ((frame_width-45)//2-40, frame_height//2+20), font, 1, (0,255,255), 1)
                detct_on = 0
                result = 0    # 게임결과
                on = 0      # 게임종료
        return on
        
    # 프레임 설정
    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 480)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 320)
    frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

    print('width: {}, height: {}'.format(frame_width, frame_height))
    while on:
        ret,img_color = cap.read()
        img_color = cv.flip(img_color, 1)    # 화면 좌우 대칭
        
        img_hsv = cv.cvtColor(img_color, cv.COLOR_BGR2HSV) 

        hue_blue = 120                        # 추출 조건
        lower_blue = (hue_blue-20, 150, 0)
        upper_blue = (hue_blue+20, 255, 255)
        img_mask = cv.inRange(img_hsv, lower_blue, upper_blue)

        kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))   # 노이즈 제거
        img_mask = cv.morphologyEx(img_mask, cv.MORPH_DILATE, kernel, iterations=3)
        
        # 출발/도착 라인

        cv.rectangle(img_color, (0,46), (45,frame_height), green, 1)
        cv.rectangle(img_color, (4,50), (41,frame_height-4), green, 2)
        
        cv.rectangle(img_color, (frame_width-45,46), (frame_width,frame_height), red, 1)
        cv.rectangle(img_color, (frame_width-48,49), (frame_width-4,frame_height-4), red, 2)


        font = cv.FONT_HERSHEY_PLAIN
        for i, l in enumerate(list('START HERE')):
            cv.putText(img_color, l, (18, 85+18*i), font, 1, green, 2)
        for i, l in enumerate(list('FINISH')):
            cv.putText(img_color, l, (frame_width-30, 85+25*i), font, 1, red, 2)

        # 객체 정보를 함께 반환하는 레이블링 함수
        # 참조: https://deep-learning-study.tistory.com/228
        nlabels, labels, stats, centroids = cv.connectedComponentsWithStats(img_mask)
        
        max = -1
        max_index = -1 

        for i in range(nlabels):
            if i < 1:
                continue
            area = stats[i, cv.CC_STAT_AREA]
            if area > max:
                max = area
                max_index = i

        # 추적 객체 유무
        if max_index != -1:       # yes 
            center_x = int(centroids[max_index, 0])
            center_y = int(centroids[max_index, 1]) 
            left = stats[max_index, cv.CC_STAT_LEFT]
            top = stats[max_index, cv.CC_STAT_TOP]
            width = stats[max_index, cv.CC_STAT_WIDTH]
            height = stats[max_index, cv.CC_STAT_HEIGHT]
                    
            cv.rectangle(img_color, (left, top), (left+width, top+height), (60,120,255), 2)
            cv.circle(img_color, (center_x, center_y), 5, (105,225,255), -1)
            
            if start_condition:
                if center_x > 45:
                    cv.putText(img_color, 'stand on', ((frame_width-45)//2-40, frame_height//2-60), font, 1.5, (0,255,255), 2)
                    cv.putText(img_color, 'the start line', ((frame_width-30)//2-90, frame_height//2-30), font, 1.5, (0,255,255), 2)
                    cv.putText(img_color, '<<<', ((frame_width-45)//2-10, frame_height//2), font, 1.5, (0,255,255), 2)
                else:    
                    header_time = time.time()            # 준비화면 출력 기준
                    start_condition = 0
                    ready = 1

            if ready:      # 준비 화면 출력
                if time.time()-header_time < 2 and center_x <= 45:
                    cv.putText(img_color, 'READY', ((frame_width-45)//2-70, frame_height//2-60), font, 3, green, 4)

                else:
                    ready = 0
                    body = 1
                    continue

            if body:
                if body_sub == 1:
                    body_time = time.time()
                    body_sub = 0
                cv.putText(img_color, 
                        'Countdown: {}/sec'.format(int(time_limit-(time.time()-body_time))),
                        (18,25), font, 1, (255,255,255), 2)
                        
                font = cv.FONT_HERSHEY_DUPLEX
                
                sec = int(time_limit-(time.time()-body_time))
                if int(time.time()-body_time) < 30:    # 제한시간 내
                    if sec%10 == 0 and sec != 0:
                        cv.putText(img_color, 'Go!',  ((frame_width-45)//2-20, frame_height//2-60), font, 1.5, green, 3)
                    if sec%10 > 5:
                        cv.putText(img_color, 'Go!',  ((frame_width-45)//2-20, frame_height//2-60), font, 1.5, green, 3)
                    if sec%10 == 8:                        
                        cv.putText(img_color, '3', ((frame_width-45)//2,frame_height//2-10), font, 1.5, green, 2)
                    if sec%10 == 7:                        
                        cv.putText(img_color, '2', ((frame_width-45)//2,frame_height//2-10), font, 1.5, green, 2)
                    if sec%10 == 6:                        
                        cv.putText(img_color, '1', ((frame_width-45)//2,frame_height//2-10), font, 1.5, green, 2)
                    if sec%10 != 0 and sec%10 < 6:
                        detecting(1, 0)
                        cv.putText(img_color, 'Stop!', ((frame_width-45)//2-35, frame_height//2-60), font, 1.5, red, 3)
                    if sec%10 == 3:                        
                        cv.putText(img_color, '3', ((frame_width-45)//2,frame_height//2-10), font, 1.5, red, 2)
                    if sec%10 == 2:                        
                        cv.putText(img_color, '2', ((frame_width-45)//2,frame_height//2-10), font, 1.5, red, 2)
                    if sec%10 == 1:                        
                        cv.putText(img_color, '1', ((frame_width-45)//2,frame_height//2-10), font, 1.5, red, 2)

                    # 시간 내 지정 위치 도착 >> Success
                    if center_x > frame_width-48 and sec >= 0:
                        result = 1    # 게임결과
                        on = 0      # 게임종료  
                
                else:
                    cv.putText(img_color, 'TIME OVER', ((frame_width-45)//2-45, frame_height//2-60), font, 1, red, 2)
                    result = 0    # 게임 결과
                    on = 0        # 게임 종료
            
        else:                 # 파란색 객체 추적 불가 시 안내창 출력
            answer = alert('''해당 게임은 파란색 객체를 추적하여 실행합니다
            화면에 파란색이 보이게 준비하세요.
            *** 계속 진행: \'Enter\', 종료: \'Esc\' ***''')
            if answer == 0:
                break
            else: pass
        
        # 컬러 스케일 영상과 스레시홀드 영상을 통합해서 출력
        stacked = np.hstack((img_color, cv.cvtColor(img_mask, cv.COLOR_GRAY2BGR)))
        cv.namedWindow('motion sensor',cv.WINDOW_NORMAL)
        cv.moveWindow('motion sensor',280,100)
        cv.imshow('motion sensor', img_color )
        
        key = cv.waitKey(1)
        if key == 27:        # esc
            answer = ask_popup()
            if answer == 1:
                break
            else:
                continue
    # 최종 결과 출력
    img = np.full((200,600,3),(255,255,255),np.uint8)

    if result == 0:
        cv.putText(img, 'GAME OVER', (33,130), font, 3, red, 3)
    else:
        cv.putText(img, 'SUCCESS', (95,130),font, 3, green, 3)
    cv.imshow('Result',img)
    cv.waitKey()
    cv.destroyWindow('Result')


