from collections import namedtuple
import cv2 as cv
import numpy as np
import csv
import os
import shutil
from . import common_functions as cf

# Debugging ways
DEBUG = False

Question = namedtuple('Question', ['ten', 'unit'])

# Read responses from warped  image, based  on positions


def read_response(warp, response_pos):
    """ @param warp: warped image got from adjust_to_squares
        @param response_pos: response positions read from get_response_pos
        @return [lecture, logs]
    """
    # Make a mask based on warped image
    correction_mask = cf.find_binary_mask(warp, [0, 0, 0], [255, 200, 200])
    lecture = dict()
    logs = list()
    for question in response_pos:
        find_unit = False
        find_ten = False
        double_unit = False
        double_ten = False
        value = 0

        for n, pt in enumerate(response_pos[question].unit):
            if check_square(correction_mask, pt):
                if not find_unit:
                    value += n
                    find_unit = True

                else:
                    double_unit = True

        for n, pt in enumerate(response_pos[question].ten):
            if check_square(correction_mask, pt):
                if not find_ten:
                    value += n*10
                    find_ten = True

                else:
                    double_ten = True

        if double_ten:
            value = ''
            logs.append('Duplo preenchimento dezena: ' + question + '\n')

        if double_unit:
            value = ''
            logs.append('Duplo preenchimento unidade: ' + question + '\n')

        if not find_unit:
            value = ''
            logs.append('Sem preenchimento unidade: ' + question + '\n')

        if not find_ten:
            value = ''
            logs.append('Sem preenchimento dezena: ' + question + '\n')

        lecture[question] = value

    return [lecture, logs]


# Define positions
def get_response_pos():
    """ @return a dict with positions of the circles, need
        to be adjusted for every reply-card format

    """
    # UFSC_format size (1017, 1401)
    # box XYZ { X = question, Y = 1=>unit, 0=>dec, Z = line}
    x_dis_border_box100 = 80
    y_dis_border_box100 = 550

    x_dis_between_box100_box110 = 20
    y_dis_between_box100_box101 = 20

    x_dis_between_item_another_box = 64.5
    y_dis_between_item_another_box = 239

    positions = dict()

    # One question per box
    #  ______________________
    # |Box 01 |  ...  | Box 14|
    # |_______|_______|_______|
    # |Box 15 |  ...  | Box 28|
    # |_______|_______|_______|
    # |Box 29 |  .. Box40 |
    # |       |           |
    # |_______|___________|

    for q in range(40):
        question = list()
        q_number = 'q' + str(q + 1).zfill(2)
        for side in range(2):       # side 0 - > dec, side 1 - > unit
            column = list()
            for item in range(10):
                x = int(x_dis_border_box100 +
                        x_dis_between_box100_box110*side +
                        x_dis_between_item_another_box*(q % 14))
                y = int(y_dis_border_box100 +
                        y_dis_between_box100_box101*item +
                        y_dis_between_item_another_box*(q//14))
                column.append(cf.Point(x=x, y=y))

            question.append(column)

        positions[q_number] = Question(ten=question[0], unit=question[1])

    return positions


def get_cpf_pos():
    """ @return a dict with positions of the circles, need
        to be adjusted for every reply-card format
    """
    positions = dict()

    x_dis_digit_1_0 = 175
    y_dis_digit_1_0 = 285

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

            nums.append(Point(x=x, y=y))

        positions[digit] = nums

    return positions


def save_logs(logs_cpf, logs_ans, scanned, cpf, path, day):
    """ @param logs_cpf: logs returned by read_cpf
        @param logs_ans: logs returned by read_answers
        @param scanned: image read from scans folder
        @param cpf: string cpf read from read_cpf func
        @param path: path to the file, where the data will be saved
        @param day: day of the test
        Save informations about the correction, to future verification
        @return None
    """
    with open(path + cpf + '-' + str(day) + '.txt', 'w') as f:
        for item in logs_cpf:
            f.write(item)

        for item in logs_ans:
            f.write(item)

    cv.imwrite(path + cpf + '-' + str(day) + '.jpg', scanned)


def export_to(responses, cpf, filename, headers, day):
    """ @param responses: read answers
        @param cpf: read cpf
        @param filename: name of file to be appended the data
        @param headers: headers wrotten on file at the beggining
        @param day: 1 or 2, corresponding to the day of test
        Append read information to the output file
        @return None
    """
    with open(filename, 'a') as f:
        responses['cpf'] = cpf
        responses['day'] = day
        writer = csv.DictWriter(f, headers)
        writer.writerow(responses)


def check_day(warped):
    """
        @param warped input image, warped to reference squares

        @return day marked on response card
    """
    correction_mask = find_binary_mask(warped, [0, 0, 0], [180, 180, 180])
    pos_1 = Point(x=873, y=336)
    pos_2 = Point(x=873, y=361)

    if check_square(correction_mask, pos_1):
        return 1
    elif check_square(correction_mask, pos_2):
        return 2


def generate_error_report(scanned, warped, squares, logs, count,
                          ans_pos, cpf_pos, path, responses, day, headers):
    """ @param scanned: scanned image from scans folder
        @param warped: warped image, to be saved with positions of answers and
        cpf, for future analysis
        @param squares: squares finded on original image, to be displayed
        on output image
        @param logs: logs to be saved
        @param count: failure count to name the folder
        @param ans_pos: positions of the answers circles, will be displayed
        on output report
        @param cpf_pos: postitions of the cpf circles, will be displayed
        on output report
        @param path: path to folder where te report will be generated
        @param responses: read responsese
        @param day: day of the test
        @param headers: headers of csv
    """

    fail = 'Failure_' + str(count)
    path += fail + '/'
    os.mkdir(path)

    tmp = cv.drawContours(scanned, squares, -1, (0, 0, 255), 2)
    cv.imwrite(path + 'Scanned_Found_Squares' + fail + '.jpg', tmp)

    tmp = warped.copy()

    for q in ans_pos:
        for col in ans_pos[q]:
            for pt in col:
                cv.rectangle(tmp,
                             (pt.x - 1, pt.y - 1),
                             (pt.x + 1, pt.y + 1),
                             (0, 0, 255), 1)

    for digit in cpf_pos:
        for pt in cpf_pos[digit]:
            cv.rectangle(tmp,
                         (pt.x - 1, pt.y - 1),
                         (pt.x + 1, pt.y + 1),
                         (0, 0, 255), 1)

    cv.imwrite(path + 'Positions_On_Warped_' + fail + '.jpg', tmp)

    with open(path + fail + '.txt', 'w') as f:
        for log in logs:
            f.write(log)

    with open(path + fail + '.csv', 'w') as f:
        responses['cpf'] = 'FAILED'
        responses['day'] = day
        writer = csv.DictWriter(f, headers)
        writer.writeheader()
        writer.writerow(responses)
