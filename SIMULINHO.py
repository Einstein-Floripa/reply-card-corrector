import numpy as np
import cv2 as cv
import os
import functions.common_functions as cf
import functions.SIMULINHO_only_functions as sf


def run(app_folder, samples_path):
    failures_path = app_folder + 'results/failures/'
    successes_path = app_folder + 'results/successes/'
    output_csv = app_folder + 'info/data.csv'

    samples = os.listdir(samples_path)
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

        scanned = cf.correct_image_angle(scanned)

        squares = cf.find_squares(scanned)

        warped = cf.adjust_to_squares(squares, scanned)

        responses_positions = sf.get_response_pos()
        responses, logs_ans = sf.read_response(warped, responses_positions)

        cpf_positions = cf.get_cpf_pos()
        cpf, logs_cpf = cf.read_cpf(warped, cpf_positions)

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
            cf.generate_error_report(scanned, warped, squares,
                                     [*logs_cpf, *logs_ans],
                                     failure_count, responses_positions,
                                     cpf_positions, failures_path)

        else:
            success_count += 1
            sf.export_to(responses, cpf, output_csv, headers)
            sf.save_logs(logs_cpf, logs_ans, warped, cpf, successes_path)
