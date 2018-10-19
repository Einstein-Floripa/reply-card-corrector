import cv2 as cv
import numpy as np
import csv
import os

# Debugging ways
DEBUG = False


# Read responses from warped  image, based  on positions
def read_response(scan, response_pos):
    """ @param scan: image read from scans folder
        @param response_pos: dict returned from 
        get_response_pos() function
        @return [read answers, logs] where answers is a dict
        and logs a list of strings
    """
    # Make a mask based on scaned image
    letters = ['A', 'B', 'C', 'D', 'E']

    # Check if image is in the right size, if it is not, resize
    h, w, _ = scan.shape
    if (h != 1401 or w != 1017):
        scan = cv.resize(scan, (1017, 1401))

    correction_mask = find_binary_mask(scan, [0, 0, 0], upper_boud_lecture)

    lecture = dict()
    logs = list()

    # Loops over all questions position
    for q in response_pos:
        find_answer = False

        # Loops over all possibles positions of a answer
        for letter, pt in enumerate(response_pos[q]):
            if (check_square(correction_mask, pt)):
                if not find_answer:
                    find_answer = True
                    r = letters[letter]

                else:
                    r = ''
                    logs.append('Duplo preenchimento, ' +
                                'questao ' + str(q) + '\n')

        if find_answer:
            lecture[q] = r
        else:
            lecture[q] = ''
            logs.append('Questao ' + str(q) + ' em branco\n')

    return [lecture, logs]


# Define positions
def get_response_pos():
    """ @return a dict with positions of the circles, need
        to be adjusted for every reply-card format
    """
    # PS_60Q dimensions (1017, 1401)
    x_dis_border_1A = 125
    y_dis_border_1A = 625

    x_dis_between_item_inside_box = 41
    y_dis_between_question_inside_box = 24

    x_dis_between_item_another_box = 325
    y_dis_between_item_another_box = 315

    positions = dict()

    #  _____________________
    # |Box 0 | Box 1 | Box 2|
    # |______|_______|______|
    # |Box 3 | Box 4 | Box 5|
    # |______|_______|______|

    for box in range(6):
        for q in range(10):
            question = list()
            q_number = 'q' + str(box*10 + q + 1).zfill(2)

            for item in range(5):
                x = int(x_dis_border_1A +
                        x_dis_between_item_inside_box * item +
                        x_dis_between_item_another_box * (box % 3))
                y = int(y_dis_border_1A +
                        y_dis_between_question_inside_box * q +
                        y_dis_between_item_another_box * (box > 2))

                question.append((x, y))

            positions[q_number] = question

    return positions


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


def export_to(responses, cpf, filename, headers):
    """ @param responses: read answers
        @param cpf: read cpf
        @param filename: name of file to be appended the data
        @param headers: headers wrotten on file at the beggining


        Append read information to the output file

        @return None
    """
    with open(filename, 'a') as f:
        responses['cpf'] = cpf
        writer = csv.DictWriter(f, headers)
        writer.writerow(responses)
