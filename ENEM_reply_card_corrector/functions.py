import cv2 as cv
import numpy as np
import csv
import os


# Debugging ways
DEBUG = False

# Upper bound
upper_boud_lecture = [250, 130, 130]


def distance_between(pt1, pt2):
    """ @param pt1 and pt2 : tupĺe of positions

        @return distance between two points
    """
    return ((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)**(1/2)


def show_img(img):
    """ @param img: image to be displayed until key pressed

        @return: None
    """
    cv.imshow('Image', img)
    cv.waitKey(0)
    cv.destroyAllWindows()


def find_binary_mask(img_rgb, lower_bound: list, upper_bound: list):
    """ @param img_rgb: receive image read from cv, in rgb form
        @param lower_bound: inferior limit of threshold to be aplied
        @param upper_bound: superior limit of threshold to be aplied

        @return a black and white image (0 or 255, 1 channel), that
        have 255 in pixels inside the range defined by lower and
        upper bounds, and 0 in the rest
    """
    # Transform common lists on np.array to use in cv.inRange
    upper = np.array(upper_bound)
    lower = np.array(lower_bound)

    # Filter input and return a binary image, where is 1 where color on rgb
    # is between the bounds
    return cv.inRange(img_rgb, lower, upper)


# Check if the square 10x10 on the points have more zeros of 255
# to say if it is marked
def check_square(mask, pt):
    """ @param mask: image black and white
        @param pt: point to be checked

        @return True if points in a squares around the point
        are mostly white.
    """
    sample = mask[pt[1] - 3: pt[1] + 3, pt[0] - 3: pt[0] + 3]
    h, w = sample.shape

    # if 40% of the square is white, it will be recognized as
    # filled
    if np.count_nonzero(sample) > h*w*4/10:
        return True
    else:
        return False


# CPF fields positions
def get_cpf_pos():
    """ @return a dict with positions of the circles, need
        to be adjusted for every reply-card format

    """
    positions = dict()

    x_dis_digit_1_0 = 175
    y_dis_digit_1_0 = 340

    x_dis_between_digits_in_block = 21
    y_dis_between_digitis_in_block = 22
    x_dis_between_blocks = 28
    x_dis_between_last_block_to_regular_blocks = 48

    for digit in range(11):
        nums = list()
        for item in range(10):
            x = int(x_dis_digit_1_0 +
                    x_dis_between_digits_in_block * digit +
                    x_dis_between_blocks * ((digit > 2) + (digit > 5)) +
                    x_dis_between_last_block_to_regular_blocks * (digit > 8))

            y = int(y_dis_digit_1_0 +
                    y_dis_between_digitis_in_block * item)

            nums.append((x, y))

        positions[digit] = nums

    return positions


def read_cpf(img, cpf_pos):
    """ @param img: scanned image
        @cpf_pos: dict of positions taken from get_cpf_pos function

        @return [cpf, logs] where cpf is a string with 11 numbers, 3 dots and a slash.
        logs  is a list of strings.
    """
    # Make a mask based on warped image
    h, w, _ = img.shape
    if (h != 1401 or w != 1017):
        img = cv.resize(img, (1017, 1401))

    mask = find_binary_mask(img, [0, 0, 0], upper_boud_lecture)

    digits = list()
    logs = list()

    for digit in cpf_pos:
        find_d = False
        for number, pt in enumerate(cpf_pos[digit]):
            if (check_square(mask, pt)):
                if not find_d:
                    digits.append(number)
                    find_d = True

                else:
                    logs.append('Falha na leitura do digito ' +
                                str(digit + 1) + 'duplo preenchimento')
                    return ['FAILED', logs]

        if not find_d:
            logs.append('Falta de digito: ' + str(digit + 1) + '\n')
            return ['FAILED', logs]

    # Format the cpf to return as string
    cpf = ''.join([str(n) for n in digits[0:3]]) + '.' + \
          ''.join([str(n) for n in digits[3:6]]) + '.' + \
          ''.join([str(n) for n in digits[6:9]]) + '-' + \
          ''.join([str(n) for n in digits[9:11]])

    return [cpf, logs]


def save_logs(logs_cpf, logs_ans, scanned, cpf, path):
    """ @param logs_cpf: logs returned by read_cpf
        @param logs_ans: logs returned by read_answers
        @param scanned: image read from scans folder
        @param cpf: string cpf read from read_cpf func
        @param path: path to the file, where the data will be saved

        Save informations about the correction, to future verification

        @return None
    """
    with open(path + cpf + '.txt', 'w') as f:
        for item in logs_cpf:
            f.write(item)

        for item in logs_ans:
            f.write(item)

    cv.imwrite(path + cpf + '.jpg', scanned)


def find_squares(img):
    """ @param img: read image from scans folder, already resized

        @return list with 4 contours, wich are the top_left, top_right,
        bot_right and bot_left squares
    """

    # The params passed to find_binary_mask on this case can be ajusted
    # according to the printing
    mask = find_binary_mask(img, [0, 0, 0], [180, 180, 180])
    _, contours, hierarchy = cv.findContours(mask,
                                             cv.RETR_TREE,
                                             cv.CHAIN_APPROX_SIMPLE)

    height, width, _ = img.shape
    four_pts_cnts = list()
    for cnt in contours:
        # Aproximating contours to a square.
        epsilon = 0.1*cv.arcLength(cnt, True)
        cnt = cv.approxPolyDP(cnt, epsilon, True)
        area = cv.contourArea(cnt)
        # Check if have 4 points in the contour, to be a square-like form
        # and already filtrate the smaller areas
        if len(cnt) == 4 and cv.contourArea(cnt) > 100:
            four_pts_cnts.append(cnt)

    top_left_cnts = list()
    top_right_cnts = list()
    bot_right_cnts = list()
    bot_left_cnts = list()

    for cnt in four_pts_cnts:
        # Get the points
        # rect[0] = top_left
        # rect[1] = top_right
        # rect[2] = bot_right
        # rect[3] = bot_left
        _, __, rect = find_max_wd(cnt)

        # Arbitrary division of the page. Just separate all square-like
        # contours in four groups based on their most internal  points,
        # the ones in top_left region, top_right, etc
        if rect[2][0] < width/6 and rect[2][1] < height/10:
            top_left_cnts.append(cnt)

        elif rect[3][0] > width*5/6 and rect[3][1] < height/10:
            top_right_cnts.append(cnt)

        elif rect[0][0] > width*5/6 and rect[0][1] > height*9/10:
            bot_right_cnts.append(cnt)

        elif rect[1][0] < width/6 and rect[1][1] > height*9/10:
            bot_left_cnts.append(cnt)

    if DEBUG:
        print("list of squares found")
        print("top_left len: ", len(top_left_cnts),
              "\ntop_right len: ", len(top_right_cnts),
              "\nbot_right len: ", len(bot_right_cnts),
              "\nbot_left len: ", len(bot_left_cnts))
        show_img(cv.drawContours(img, four_pts_cnts,
                                 -1, (0, 0, 255), 2))

    # Order list from biggest to smallest, to take only the first
    # Expecting that only the biggest square that is inside the range
    # is the one to be used
    top_left_cnts.sort(key=lambda k: cv.contourArea(k), reverse=True)
    top_right_cnts.sort(key=lambda k: cv.contourArea(k), reverse=True)
    bot_right_cnts.sort(key=lambda k: cv.contourArea(k), reverse=True)
    bot_left_cnts.sort(key=lambda k: cv.contourArea(k), reverse=True)

    return [top_left_cnts[0], top_right_cnts[0],
            bot_right_cnts[0], bot_left_cnts[0]]


# Find max width, height and the rect of the page,
# defined with four points
def find_max_wd(rect):
    """ @param rect: four point contour, expect to be a regular square

        @return [max_width, max_height and rect] where max_width  is the
        max of distances beetween bot_right and bot_left and top_left and
        top_right, analog for max_height. The rect is returned as follow:

        rect[0] = top_left
        rect[1] = top_right
        rect[2] = bot_right
        rect[3] = bot_left
    """
    pts = rect.reshape(4, 2)
    rect = np.zeros((4, 2), dtype='float32')

    # top-left will be the point where the sum is the lowest, and
    # bot-right will be the biggest
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # take the diff between points (x - y), the positive and greatest
    # diff expect to be the top_right and the smallest to be the top_left
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    top_left, top_right, bot_right, bot_left = rect

    widthA = distance_between(bot_right, bot_left)
    widthB = distance_between(top_right, top_left)

    heightA = distance_between(bot_right, top_right)
    heightB = distance_between(bot_left, top_left)

    max_width = max(int(widthA), int(widthB))
    max_height = max(int(heightA), int(heightB))

    return [max_width, max_height, rect]


def adjust_to_squares(squares, img):
    """ @param squares: four squares, from the borders
        @param img: read img from scans folder

        @return image adjusted to squares and resized
    """

    square_points = [*squares[0], *squares[1], *squares[2], *squares[3]]
    pts = np.array(square_points, dtype='int32').reshape(16, 2)

    # top-left will be the point where the sum is the lowest, and
    # bot-right will be the biggest
    s = pts.sum(axis=1)
    top_left = pts[np.argmin(s)]
    bot_right = pts[np.argmax(s)]

    # take the diff between points (x - y), the positive and greatest
    # diff expect to be the top_right and the smallest to be the top_left
    diff = np.diff(pts, axis=1)
    top_right = pts[np.argmin(diff)]
    bot_left = pts[np.argmax(diff)]

    rect = np.ndarray((4, 2), dtype="float32")

    rect[0] = top_left
    rect[1] = top_right
    rect[2] = bot_right
    rect[3] = bot_left

    maxWidth, maxHeight, rect = find_max_wd(rect)

    # Create the four-point rectangle where the page will be warped
    dst = np.array([[0, 0],
                    [maxWidth - 1, 0],
                    [maxWidth - 1, maxHeight - 1],
                    [0, maxHeight - 1]], dtype="float32")

    M = cv.getPerspectiveTransform(rect, dst)
    warp = cv.warpPerspective(img, M, (maxWidth, maxHeight))

    # Defines a size to the image. Arbitrary by now, because the points
    # bellow where calculated with this size
    warp = cv.resize(warp, (1017, 1401))

    return warp
