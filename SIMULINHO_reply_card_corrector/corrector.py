import csv
import answers
import os
from functions import *
from pprint import pprint
from operator import itemgetter


def run():
    print('Linking tables...')
    app_folder = 'SIMULINHO_reply_card_corrector/'
    answers_table_path = app_folder + 'info/data.csv'
    subscribers_table_path = app_folder + 'info/subscribers.csv'
    class_table_path = app_folder + 'info/class.csv'
    output_data_path = app_folder + 'info/organized_data.csv'

    if not os.path.exists(output_data_path):
        with open(output_data_path, 'w') as f:
            pass

    students = list()

    class_table = list()
    with open(class_table_path, 'r', encoding="latin-1") as f:
        reader = csv.reader(f)
        for row in reader:
            class_table.append(row)

    answers_table = list()
    with open(answers_table_path, 'r', encoding="latin-1") as f:
        reader = csv.DictReader(f)
        for row in reader:
            answers_table.append(row)

    subs_table = list()
    with open(subscribers_table_path, 'r', encoding="latin-1") as f:
        reader = csv.reader(f)
        for row in reader:
            subs_table.append(row)

    for class_row in class_table:
        tmp = dict()
        for subs_row in subs_table:
            if subs_row[0] == class_row[1]:
                tmp['name'] = class_row[0]
                tmp['cpf'] = class_row[1]
                tmp['course'] = subs_row[1]
                tmp['lang'] = subs_row[2]
                tmp['quota'] = subs_row[3]
                tmp['answers'] = [dict(i) for i in answers_table
                                  if i['cpf'] == tmp['cpf']]
                if tmp['answers'] == []:
                    tmp['answers'] = answers.empty

                else:
                    tmp['answers'] = tmp['answers'][0]
                    tmp['answers'].pop('cpf')

                if tmp['lang'] == 'espanhol':
                    tmp['score'] = get_correction(tmp['answers'],
                                                  answers.esp_r_answers)

                elif tmp['lang'] == 'inlges':
                    tmp['score'] = get_correction(tmp['answers'],
                                                  answers.eng_r_answers)

                students.append(tmp)

    students.sort(key=itemgetter('name'))
    keys = list(students[0]['answers'].keys())
    keys.sort()

    with open(output_data_path, 'a') as f:
        writer = csv.writer(f)
        for student in students:
            responses = list()
            for key in keys:
                responses.append(student['answers'][key])

            writer.writerow([student['name'], student['cpf'],
                             student['lang'], student['quota'], *responses])
