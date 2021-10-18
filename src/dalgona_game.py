import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

def game_start(shape):
    global img, img_copy, game_count, isDragging, x0, y0
    img = cv2.imread('./img/{}.png'.format(shape))
    img_copy = img.copy()
    w_name = 'Dalgona'

    imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    _, imgTh = cv2.threshold(imgray,127,255,cv2.THRESH_BINARY)

    # 원, 모양 모두
    c_all, _ = cv2.findContours(imgTh,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)

    # 원 외부
    c_out, _ = cv2.findContours(imgTh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

    # 뺄셈 => 모양

    # 각각의 원소들 numpy.ndarray -> list
    all_list = list(map(lambda x:x.tolist(),c_all))
    out_list = list(map(lambda x:x.tolist(),c_out))

    # 모양 좌표
    shape_list = [a for a in all_list if a not in out_list] 

    shape_list_sort = [s for sl in shape_list for s in sl ]
    shape_list_sort.sort()

    check_x = dict()
    check_y = dict()

    # 현재 좌표값과 경계값 비교를 위한 좌표 리스트

    preX, preY = -1,-1
    for s in shape_list_sort:
        locX = s[0][0]
        locY = s[0][1]
        if locX in check_x:
            idx_x = len(check_x[locX]) - 1
            if round(locY - preY) == 1:
                check_x[locX][idx_x].append(locY)
            else:
                if len(check_x[locX][idx_x]) > 1 and max(check_x[locX][idx_x]) - min(check_x[locX][idx_x]) >= 14:
                    check_x[locX].append([locY])
                else:
                    check_x[locX][idx_x].append(locY)
            preY = locY
        else:
            check_x[locX] = [[locY]]
            preY = locY

            
        if locY in check_y:
            idx_y = len(check_y[locY]) - 1
            if round(locX - preX) == 1:
                check_y[locY][idx_y].append(locX)
            else:
                if len(check_y[locY][idx_y]) > 1 and max(check_y[locY][idx_y]) - min(check_y[locY][idx_y]) >= 14:
                    check_y[locY].append([locX])
                else:
                    check_y[locY][idx_y].append(locX)
            preX = locX
        else:
            check_y[locY] = [[locX]]
            preX = locX

    c_shape = list(map(lambda x:np.array(x),shape_list_sort))
    cv2.drawContours(img,c_shape,-1,(0,0,255),1) 
    

    cv2.namedWindow(w_name,cv2.WINDOW_NORMAL)
    cv2.moveWindow(w_name,350,100)
    cv2.imshow(w_name,img) # 게임 시작

    game_count = 1
    isDragging = False
    x0, y0 = -1, -1 

    def Finish(result):
        global game_count ,img, img_copy
        
        cv2.destroyWindow(w_name)
        cv2.imshow('Dalgona result',img) # 내가 그린 결과

        fin = np.full((213, 440, 3), 0, dtype=np.uint8)
        if result == 'success':
            cv2.putText(fin, 'SUCCESS', (75,100), cv2.FONT_HERSHEY_COMPLEX, 2, (255,0,0), 6)
        else: # 'fail'
            cv2.putText(fin, 'FAIL', (155,100), cv2.FONT_HERSHEY_COMPLEX, 2, (0,0,255), 6)        
        cv2.putText(fin, 'Try Again?(y/n)', (95,170), cv2.FONT_HERSHEY_COMPLEX,1, (255,255,255), 1)
        
        cv2.namedWindow('FINISH',cv2.WINDOW_NORMAL)
        cv2.moveWindow('FINISH',390,60)
        cv2.imshow('FINISH', fin) # 성공 / 실패 
        
        key = cv2.waitKey(0) & 0xFF
        if key == ord('y'): 
            game_count += 1
            cv2.destroyWindow('Dalgona result')
            cv2.destroyWindow('FINISH')
            img = img_copy.copy()
            cv2.drawContours(img,c_shape,-1,(0,0,255),1) 
            cv2.imshow(w_name,img) 
            cv2.setMouseCallback(w_name,onMouse)
        elif key == ord('n') or key == 27: # esc
            cv2.destroyWindow('Dalgona result')
            cv2.destroyWindow('FINISH')
        else:
            pass

    def area_check(x,y,check_x,check_y):
        
        # 영역 밖 169 362 # 꼭짓점 부분 -> 처리해주어야함
        # y좌표들(위아래) [[328, 354, 355], [369]]
        # x좌표들(양옆) [[149, 384]]
        
        check_x_area,check_y_area = False, False
        pre_min_x,pre_min_y = 0, 0 
        if check_x.get(x) == None or check_y.get(y) == None: # 영역 밖 
            return False
        else:  
            for cyl in check_y.get(y): # x 범위 확인
                if len(cyl) == 1: # 꼭짓점 부분
                    if pre_min_x + 1 < x < max(cyl) - 1:
                        check_x_area = True
                        break
                else:
                    if min(cyl) + 1 < x < max(cyl) - 1:
                        check_x_area = True
                        pre_min_x = min(cyl)
                        break
                    
            for cxl in check_x.get(x): # y 범위 확인
                if len(cxl) == 1: # 꼭짓점 부분
                    if pre_min_y + 1 < y < max(cxl) - 1:
                        check_y_area = True
                        break
                else:
                    if min(cxl) + 1 < y < max(cxl) - 1:
                        check_y_area = True
                        pre_min_y = min(cxl)
                        break       
                    
            if check_x_area and check_y_area:
                return True
                
            else:
                # 게임 종료
                return False
            

    def onMouse(event, x, y, flags, param):
        global isDragging, img, img_copy,x0, y0,  game_count
        
        if event == cv2.EVENT_LBUTTONDOWN: # 왼쪽 버튼 누름
            if game_count != 1:
                img = img_copy.copy()

            if area_check(x,y,check_x,check_y) == False:
                Finish('fail')
                isDragging = False
            else:
                isDragging = True
                x0 = x
                y0 = y
            
        elif event == cv2.EVENT_MOUSEMOVE: # 마우스 움직임
            if isDragging:
                if area_check(x,y,check_x,check_y) == False:
                    Finish('fail')
                    isDragging = False
                else:
                # 사용자 라인 표시 - 달고나와 동일한 색
                    cv2.line(img, (x0,y0), (x,y), (102,217,255), 1, cv2.LINE_AA) # 배경이랑 같은 색으로 그림을 그려 컨투어 생성되도록 함
                    cv2.drawContours(img,c_shape,-1,(0,0,255),1) 

                    cv2.imshow(w_name, img)
                    x0,y0 = x,y
                
        elif event == cv2.EVENT_LBUTTONUP: # 왼쪽 버튼 뗌
            if isDragging:
                draw_img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) 
                _,drawTh = cv2.threshold(draw_img,127,255,cv2.THRESH_BINARY)
                draw_cntrs,_ = cv2.findContours(drawTh,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)

                print('내가 그린 달고나 컨투어',len(draw_cntrs))  # 확인용
                
                # 시작점과 끝점을 잇지 않으면 (막힌 삼각형이 아니라면) 컨투어 개수는 4개가 나옴
                
                if len(draw_cntrs) > 4:
                    Finish('success')
                else: # 기존 달고나 그림의 컨투어 개수 : 3
                    Finish('fail')
                    
                isDragging = False

    cv2.setMouseCallback(w_name, onMouse) 
    cv2.waitKey(0)