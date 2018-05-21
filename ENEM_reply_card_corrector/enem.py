import numpy as np
import cv2 as cv
import os
from functions import *


def run():
    failures_path = 'ENEM_reply_card_corrector/results/failures/'
    successes_path = 'ENEM_reply_card_corrector/results/successes/'
    samples_path = "ENEM_reply_card_corrector/scans/"
    output_csv = 'ENEM_reply_card_corrector/info/data.csv'

    samples = os.listdir(samples_path)
    headers = ['cpf', *list(get_response_pos().keys())]
    failure_count = 0
    success_count = 0

    if not os.path.exists(output_csv):
        with open(output_csv, 'w') as f:
            writer = csv.DictWriter(f, headers)
            writer.writeheader()

    filenames = [i for i in samples if "scan" in i]
