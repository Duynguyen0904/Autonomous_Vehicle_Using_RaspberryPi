import cv2
import numpy as np

def un_distort(img):
    #Camera Matrix
    K = np.array([[1.15422732e+03, 0.00000000e+00, 6.71627794e+02],
        [0.00000000e+00, 1.14818221e+03, 3.86046312e+02],
        [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    #Distortion Coefficients
    dist = np.array([[-2.42565104e-01, -4.77893070e-02, -1.31388084e-03, -8.79107779e-05,
        2.20573263e-02]])
    undistorted_image = cv2.undistort(img, K, dist, None, K)

    return undistorted_image

def lane_curve(img,t):
    h,w,c = img.shape
    pts1 = np.float32([t[0], t[1], t[2], t[3]]).reshape(-1,1,2)
    pts2 = np.float32([[0,0], [0,h], [w,h], [w,0]]).reshape(-1,1,2)
    # Mtx, mask = cv2.findHomography(pts1, pts2, cv2.RANSAC, 10)
    Mtx = cv2.getPerspectiveTransform(pts1, pts2)
    warp = cv2.warpPerspective(img, Mtx, (w,h))

    return warp

def findEdge(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
    # white color
    lower1 = np.array([0, 200, 0])
    upper1 = np.array([255, 255, 255])
    mask1 = cv2.inRange(hsv, lower1, upper1)
    # yellow color
    # hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    lower2 = np.array([0, 50, 100])
    upper2 = np.array([120, 255, 255])
    mask2 = cv2.inRange(hsv, lower2, upper2)
    # resultant mask
    result = cv2.bitwise_or(mask1, mask2)

    return result

def process(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9,9), 3) # kernel size must be positive and odd
    thresh = cv2.threshold(blur, 50, 255, cv2.THRESH_BINARY)[1]
    
    return blur,thresh

def line_fitting(img):
    # histogram
    ## img.shape[0]: height; img.shape[1]: width
    histogram = np.sum(img[img.shape[0]//2:, :], axis=0)
    out_img = np.dstack((img, img, img))*255
    midpoint = np.int32(histogram.shape[0]//2)
    left_base = np.argmax(histogram[:midpoint]) ## position of max number of histogram from 0 to midpoint
    right_base = np.argmax(histogram[midpoint:]) + midpoint ## position of max number of histogram from midpoint to end 
    # print(f"histogram: {histogram[:]}")
    # print(f"midpoint: {midpoint}")
    # print(f"left_base: {left_base}")
    # print(f"right_base: {right_base}")
    
    #IDENTIFY THE NON ZERO VALUES
    nonzero = img.nonzero() # find the location of nonzero element in array 
    nonzero_y = np.array(nonzero[0]) ## row indices 
    nonzero_x = np.array(nonzero[1]) ## column indices
    # print(f"nonzero: {nonzero}")
    # print(f"nonzero_y: {nonzero_y}")
    # print(f"nonzero_x: {nonzero_x}")

    #NUMBER OF WINDOWS AND LINE FITTING
    n_windows = 10
    min = 50
    margin = 100
    height = np.int32(img.shape[0]/n_windows)
    left_lane_inds = []
    right_lane_inds = []
    left_current = left_base
    right_current = right_base

    ## draw bounded rectangle in range 30 window
    for i in range(n_windows):
        wind_y_low = img.shape[0] - (i+1)*height
        wind_y_high = img.shape[0] - i*height
        win_left_low = left_current - margin
        win_left_high = left_current + margin
        win_right_low = right_current - margin
        win_right_high = right_current + margin 

        #VISUALIZE THE RECTANGLES
        cv2.rectangle(out_img, (win_left_low, wind_y_low), (win_left_high, wind_y_high), (0,255,0), 2)
        cv2.rectangle(out_img, (win_right_low, wind_y_low), (win_right_high, wind_y_high), (0,255,0), 2)

        #FIND THE NON ZERO SPOTS ON THE IMAGE
        good_left_inds = ((nonzero_y >= wind_y_low) & (nonzero_y < wind_y_high) & 
        (nonzero_x >= win_left_low) &  (nonzero_x < win_left_high)).nonzero()[0]
        good_right_inds = ((nonzero_y >= wind_y_low) & (nonzero_y < wind_y_high) & 
        (nonzero_x >= win_right_low) &  (nonzero_x < win_right_high)).nonzero()[0]
        # print(f"q: {((nonzero_y >= wind_y_low) & (nonzero_y < wind_y_high) & (nonzero_x >= win_left_low) &  (nonzero_x < win_left_high)).nonzero()}")
        # print(f"e: {((nonzero_y >= wind_y_low) & (nonzero_y < wind_y_high) & (nonzero_x >= win_left_low) &  (nonzero_x < win_left_high)).nonzero()[0]}")
        
        left_lane_inds.append(good_left_inds)
        right_lane_inds.append(good_right_inds)

        if len(good_left_inds) > min:
            left_current = np.int32(np.mean(nonzero_x[good_left_inds]))
        if len(good_right_inds) > min:
            right_current = np.int32(np.mean(nonzero_x[good_right_inds]))
    try:
        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)
    except ValueError:
        pass
        
    left_x = nonzero_x[left_lane_inds]
    left_y = nonzero_y[left_lane_inds] 
    right_x = nonzero_x[right_lane_inds]
    right_y = nonzero_y[right_lane_inds]
    
    # print(f"left_x: {left_x}")
    # print(f"left_y: {left_y}")
    # print(f"right_x: {right_x}")
    # print(f"right_y: {right_y}")

    #POLYFIT TO FIND THE POINTS OF THE LINE
    try:
        left_fit = np.polyfit(left_y, left_x, 2)
        right_fit = np.polyfit(right_y, right_x, 2)
    except TypeError:
        pass

    #FIND THE EQUATION OF THE CURVE OF THE LEFT AND RIGHT LINES
    plot_y = np.linspace(0, img.shape[0]-1, num = img.shape[0])
    try:
        left_fit_x = left_fit[0]*plot_y**2 + left_fit[1]*plot_y + left_fit[2]
        right_fit_x = right_fit[0]*plot_y**2 + right_fit[1]*plot_y + right_fit[2]
    except ValueError:
        print('The function failed to fit a line!')
        left_fit_x = 1*plot_y**2 + 1*plot_y
        right_fit_x = 1*plot_y**2 + 1*plot_y
    average = (left_fit_x+right_fit_x)//2
    # print(f"average = {average}")

    #FIND THE POINTS OF THE LINES FOUND
    left_points = np.array([np.transpose(np.vstack([left_fit_x, plot_y]))])
    right_points = np.array([np.flipud(np.transpose(np.vstack([right_fit_x, plot_y])))])
    # right_points = np.array([np.transpose(np.vstack([right_fit_x, plot_y]))])
    points = np.hstack([left_points, right_points])
    mid_points = np.array([np.transpose(np.vstack([average, plot_y]))])
    # print(f"l = {left_fit_x}, r = {right_fit_x}")

    #CREATE AN EMPTY MASK
    # warp = np.zeros_like(img).astype(np.uint8)
    color = np.dstack((img, img, img))*255
    
    #DRAW LINES AND FILL
    cv2.polylines(out_img, np.int32([left_points]), False, (0,255,255), 15)
    cv2.polylines(out_img, np.int32([right_points]), False, (0,255,255), 15)
    cv2.polylines(color, np.int32([mid_points]), False, (255,0,255), 10)
    cv2.fillPoly(color, np.int_([points]), (255, 0, 255))

    # return histogram
    return out_img, color, left_fit, right_fit, plot_y
    
def radius(img, left_fit, right_fit, plot_y):
    y = np.max(plot_y)
    # Actual point
    left = 1 + 3.5*left_fit[0]*y**2 + left_fit[1]*y + left_fit[2]
    right = 1 + 3.5*right_fit[0]*y**2 + right_fit[1]*y + right_fit[2]   
    actual_position = (left + right)//2
    cv2.circle(img, (int(actual_position), img.shape[0]),20, (0,255,0), cv2.FILLED)
    position = img.shape[1]//2

    # Position point
    left_p = 1 + left_fit[0]*y**2 + left_fit[1]*y + left_fit[2]
    right_p = 1 + right_fit[0]*y**2 + right_fit[1]*y + right_fit[2]
    cv2.circle(img, (int((left_p+right_p)//2), img.shape[0]),20, (0, 0, 255), cv2.FILLED)
    # cv2.circle(img, (int(left_p), img.shape[0]),20, (0,0,255), cv2.FILLED)
    # cv2.circle(img, (int(right_p), img.shape[0]),20, (0,0,255), cv2.FILLED)
    distance = position - actual_position
    return distance

def UnWarp(img, t):
    h, w, c = img.shape
    pts1 = np.array([t[0], t[1],t[2], t[3]]).reshape(-1,1,2)
    pts2 = np.float32([[0,0], [0,h], [w,h], [w,0]]).reshape(-1,1,2)
    Mtx = cv2.findHomography(pts2, pts1, cv2.RANSAC, 10)[0]
    unwarp = cv2.warpPerspective(img, Mtx, (w,h))

    return unwarp

def Compare_condition(img, process_img, radius):
    result = cv2.addWeighted(img, 1, process_img, 0.5, 1)
    if(radius >= -60 and radius <= 60):
        cv2.putText(result,"Straight Ahead" , (50,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255 , 0), 2)
        direct = "straight"
    elif(radius > 60 ):
        cv2.putText(result,"Left Turn Ahead  " , (50,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255 , 255), 2)
        direct = "left"
    elif(radius <-60):
        cv2.putText(result,"Right Turn Ahead  " , (50,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255 , 0), 2)
        direct = "right"
    
    return result, direct
