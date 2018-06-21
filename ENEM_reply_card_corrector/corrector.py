import csv
import os
from answers import *
from operator import itemgetter


def run():
    print('Linking tables...')
    app_folder = 'ENEM_reply_card_corrector/'
    answers_table_path = app_folder + 'info/data.csv'
    subscribers_table_path = app_folder + 'info/subscribers.csv'
    output_data_path = app_folder + 'info/organized_data.csv'

    if not os.path.exists(output_data_path):
        with open(output_data_path, 'w') as f:
            pass

    students = list()

    answers_table = list()
    with open(answers_table_path, 'r', encoding="latin-1") as f:
        reader = csv.DictReader(f)
        for row in reader:
            answers_table.append(row)

    # [0] - name
    # [1] - cpf
    # [2] - course
    # [3] - lang
    # [4] - quota
    subs_table = list()
    with open(subscribers_table_path, 'r', encoding="latin-1") as f:
        reader = csv.reader(f)
        for row in reader:
            subs_table.append(row)

    for sub_row in subs_table:
        tmp = dict()
        tmp['name'] = sub_row[0]
        tmp['cpf'] = sub_row[1]
        tmp['course'] = sub_row[2]
        tmp['lang'] = sub_row[3]
        tmp['quota'] = sub_row[4]

        tmp['answers_d1'] = [
            dict(i) for i in answers_table if i['cpf'] == tmp['cpf'] and
            i['day'] == '1']

        if tmp['answers_d1'] == []:
            tmp['answers_d1'] = empty

        else:
            tmp['answers_d1'] = tmp['answers_d1'][0]
            tmp['answers_d1'].pop('cpf')
            tmp['answers_d1'].pop('day')

        tmp['answers_d2'] = [
            dict(i) for i in answers_table if i['cpf'] == tmp['cpf'] and
            i['day'] == '2']

        if tmp['answers_d2'] == []:
            tmp['answers_d2'] = empty

        else:
            tmp['answers_d2'] = tmp['answers_d2'][0]
            tmp['answers_d2'].pop('cpf')
            tmp['answers_d2'].pop('day')

        students.append(tmp)

    students.sort(key=itemgetter('name'))
    keys1 = list(students[0]['answers_d1'].keys())
    keys2 = list(students[0]['answers_d2'].keys())
    keys1.sort()
    keys2.sort()

    with open(output_data_path, 'a', encoding="latin-1") as f:
        writer = csv.writer(f)
        for student in students:
            responses = list()
            for key in keys1:
                responses.append(student['answers_d1'][key])
            for key in keys2:
                responses.append(student['answers_d2'][key])

            writer.writerow([student['name'], student['cpf'],
                             student['lang'], student['quota'], *responses])
