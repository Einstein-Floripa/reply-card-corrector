""" Reply Card Corrector

    https://github.com/Einstein-Floripa/reply-card-corrector

    WARNING: If output folder already exists, script will delete it and
    recreate folder structure

Usage:
    main.py <mode> <subscribers_csv> [-s scans_folder] [-o output_folder]

Options:
    -h --help           Show this screen
    --version           Current version
    --scans -s=<S>      Put target scans folder [default: scans]
    --output -o=<O>     Output folder [default: output]
"""

from functions import *
import UFSC
import UDESC
import ENEM
import SIMULINHO
from docopt import docopt
import os
import shutil

modes = ['ENEM', 'UDESC', 'UFSC', 'SIMULINHO']

if __name__ == '__main__':
    args = docopt(__doc__, version='Reply Card Corrector 2.0')

    mode = args['<mode>']
    print(os.path.isfile(args['<subscribers_csv>']))

    if mode.upper() not in modes:
        print('Invalida mode!')
        exit(1)

    scans_folder = args['--scans']
    if not os.path.isdir(scans_folder):
        print('There is no scans folder!')
        exit(1)

    if scans_folder[:-1] != '/':
        scans_folder += '/'

    # Remove entire output folder if it already exists
    output_folder = args['--output']
    if os.path.isdir(output_folder):
        shutil.rmtree(output_folder)

    # Creating folder structure to execute script
    os.mkdir(output_folder)
    if output_folder[:-1] != '/':
        output_folder += '/'

    os.mkdir(output_folder + 'results')
    os.mkdir(output_folder + 'results/successes')
    os.mkdir(output_folder + 'results/failures')
    os.mkdir(output_folder + 'info')

    # Move subscribers csv file to
    subscribers_csv = args['<subscribers_csv>']
    if not os.path.isfile(subscribers_csv):
        print('There is no subscribers file!')
        exit(1)

    shutil.copy(subscribers_csv, output_folder + 'info/subscribers.csv')

    if mode == 'UFSC':
        UFSC.run(output_folder, scans_folder)

    elif mode == 'UDESC':
        UDESC.run(output_folder, scans_folder)

    elif mode == 'ENEM':
        ENEM.run(output_folder, scans_folder)

    elif mode == 'SIMULINHO':
        SIMULINHO.run(output_folder, scans_folder)
