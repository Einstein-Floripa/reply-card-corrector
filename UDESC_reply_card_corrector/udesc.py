import numpy as np
import cv2 as cv
import os
from functions import *


def run():
    app_folder = 'UDESC_reply_card_corrector/'
    failures_path = app_folder + 'results/failures/'
    successes_path = app_folder + 'results/successes/'
    samples_path = app_folder + 'scans/'
    output_csv = app_folder + 'info/data.csv'

    samples = os.listdir(samples_path)
    headers = ['cpf', *list(get_response_pos().keys()), 'day']
    failure_count = 0
    success_count = 0

    if not os.path.exists(output_csv):
        with open(output_csv, 'w') as f:
            writer = csv.DictWriter(f, headers)
            writer.writeheader()

    filenames = [i for i in samples if "scan" in i]

    for filename in filenames:

        print('Scanning ' + filename + '...')

        scanned = cv.imread(samples_path + filename)

        squares = find_squares(scanned)

        warped = adjust_to_squares(squares, scanned)

        warped = correct_image_angle(warped)

        responses_positions = get_response_pos()
        responses, logs_ans = read_response(warped, responses_positions)

        cpf_positions = get_cpf_pos()
        cpf, logs_cpf = read_cpf(warped, cpf_positions)

        day = check_day(warped)

        # draw squares on the points to verify possible errors
        for key in cpf_positions:
            for pt in cpf_positions[key]:
                cv.rectangle(warped,
                             (pt.x - 1, pt.y - 1),
                             (pt.x + 1,  pt.y + 1),
                             (0, 0, 255))

        for q in responses_positions:
            for pt in responses_positions[q]:
                cv.rectangle(warped,
                             (pt.x - 1, pt.y - 1),
                             (pt.x + 1,  pt.y + 1),
                             (0, 0, 255))

        # If any error while reading cpf occurs, the
        # image will be placed on failures
        if cpf == 'FAILED':
            failure_count += 1
            generate_error_report(scanned, warped, squares,
                                  [*logs_cpf, *logs_ans],
                                  failure_count, responses_positions,
                                  cpf_positions, failures_path, responses,
                                  day, headers)

        else:
            success_count += 1
            export_to(responses, cpf, output_csv, headers, day)
            save_logs(logs_cpf, logs_ans, warped, cpf, successes_path, day)
