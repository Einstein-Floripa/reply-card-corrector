import numpy as np
import cv2 as cv
import os
from functions import *


def run():
    failures_path = 'reply_card_corrector/results/failures/'
    successes_path = 'reply_card_corrector/results/successes/'
    samples_path = "reply_card_corrector/scans/"
    samples = os.listdir(samples_path)
    output_csv = 'reply_card_corrector/results/data.csv'
    headers = ['cpf', *list(get_response_pos().keys())]
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

        responses_positions = get_response_pos()
        responses, logs_ans = read_response(warped, responses_positions)

        cpf_positions = get_cpf_pos()
        cpf, logs_cpf = read_cpf(warped, cpf_positions)

        # Resize for the specified size and draw squares on the points
        # to verify possible errors
        for key in cpf_positions.keys():
            for pt in cpf_positions[key]:
                cv.rectangle(warped,
                             (pt[0] - 1, pt[1] - 1),
                             (pt[0] + 1, pt[1] + 1),
                             (0, 0, 255), 1)

        for key in responses_positions.keys():
            for pt in responses_positions[key]:
                cv.rectangle(warped,
                             (pt[0] - 1, pt[1] - 1),
                             (pt[0] + 1, pt[1] + 1),
                             (0, 0, 255), 1)

        # If any error while reading cpf occurs, the
        # image will be placed on failures
        if cpf == 'FAILED':
            failure_count += 1
            generate_error_report(scanned, warped, squares,
                                  [*logs_cpf, *logs_ans],
                                  failure_count, responses_positions,
                                  cpf_positions, failures_path)

        else:
            success_count += 1
            export_to(responses, cpf, output_csv, headers)
            save_logs(logs_cpf, logs_ans, warped, success_count,
                      cpf, successes_path)
