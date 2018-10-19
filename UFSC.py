import numpy as np
import cv2 as cv
import os
import csv
import functions.common_functions as cf
import functions.UFSC_only_functions as ef


def run(app_folder, samples_path):
    failures_path = app_folder + 'results/failures/'
    successes_path = app_folder + 'results/successes/'
    output_csv = app_folder + 'info/data.csv'

    samples = os.listdir(samples_path)
    headers = ['cpf', *list(ef.get_response_pos().keys()), 'day']
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

        scanned = cf.correct_image_angle(scanned)
        try:
            squares = cf.find_squares(scanned)

        except:
            failure_count += 1
            fail = 'Failure_' + str(count)
            path += fail + '/'
            os.mkdir(path)
            with open(path + fail + "_log.txt") as f:
                f.write("Falha ao encontrar quadrados de orientação. \
                         Correção abortada.")

            continue

        warped = cf.adjust_to_squares(squares, scanned)

        responses_positions = ef.get_response_pos()
        responses, logs_ans = ef.read_response(warped, responses_positions)

        cpf_positions = ef.get_cpf_pos()
        cpf, logs_cpf = cf.read_cpf(warped, cpf_positions)

        day = ef.check_day(warped)

        # draw squares on the points to verify possible errors
        for key in cpf_positions.keys():
            for pt in cpf_positions[key]:
                cv.rectangle(warped,
                             (pt.x - 1, pt.y - 1),
                             (pt.x + 1, pt.y + 1),
                             (0, 0, 255), 1)

        for key in responses_positions.keys():
            for side in responses_positions[key]:
                for pt in side:
                    cv.rectangle(warped,
                                 (pt.x - 1, pt.y - 1),
                                 (pt.x + 1, pt.y + 1),
                                 (0, 0, 255))

        # If any error while reading cpf occurs, the
        # image will be placed on failures
        if cpf == 'FAILED':
            failure_count += 1
            ef.generate_error_report(scanned, warped, squares,
                                     [*logs_cpf, *logs_ans],
                                     failure_count, responses_positions,
                                     cpf_positions, failures_path, responses,
                                     day, headers)

        else:
            success_count += 1
            ef.export_to(responses, cpf, output_csv, headers, day)
            ef.save_logs(logs_cpf, logs_ans, warped, cpf, successes_path, day)