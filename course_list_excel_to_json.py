import json

import numpy as np
import pandas as pd

days_to_index = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6}
index_to_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

hours_to_index = {'08:30': 0, '09:10': 0, '09:20': 1, '10:00': 1, '10:10': 2, '10:50': 2, '11:00': 3, '11:40': 3,
                  '11:50': 4, '12:30': 4, '12:40': 5, '13:20': 5, '13:30': 6, '14:10': 6, '14:20': 7, '15:00': 7,
                  '15:10': 8, '15:50': 8, '16:00': 9, '16:40': 9, '16:50': 10, '17:30': 10, '17:40': 11,
                  '18:20': 11, '18:30': 12, '19:10': 12, '19:20': 13, '20:00': 13, '20:10': 14, '20:50': 14,
                  '21:00': 15, '21:40': 15, '21:50': 16, '22:30': 16}

index_to_start_hours = ['08:30', '09:20', '10:10', '11:00', '11:50', '12:40', '13:30', '14:20', '15:10', '16:00',
                        '16:50', '17:40', '18:30', '19:20', '20:10', '21:00', '21:50']
index_to_end_hours = ['09:10', '10:00', '10:50', '11:40', '12:30', '13:20', '14:10', '15:00', '15:50', '16:40',
                      '17:30', '18:20', '19:10', '20:00', '20:50', '21:40', '22:30']


def fix_time_table_k():
    with open('data/course_list.json', mode='r+', encoding='utf8') as io_file:
        course_list = json.load(io_file)
        for course in course_list.values():
            code = course['code']
            for k, v in course['sections'].items():
                section = k
                for time_table in v['time_table']:
                    course_date = time_table.split(maxsplit=1)
                    interval_start, interval_end = tuple(course_date[1].split(' - '))

                    if 'MB' in interval_end:
                        interval_end = interval_end[:-7]

                    day_index = days_to_index[course_date[0]]
                    start_index = hours_to_index[interval_start]
                    end_index = hours_to_index[interval_end] + 1

                    for p in range(start_index, end_index):
                        new_time_table = [day_index, p]
                        if new_time_table not in v['time_table_index']:
                            course_list[code]['sections'][section]['time_table_index'].append(new_time_table)
        json.dump(course_list, io_file, indent=4)


def excel_to_json():
    excel = pd.read_excel('course_list.xlsx').fillna(method='ffill')
    records = excel.to_records()
    course_list = {}

    # 0 - Code
    # 1 - Name
    # 2 - Section
    # 3 - ECTS
    # 4 - Day
    # 5,6 - Start, End Hour

    for record in records:
        if record[1] is np.nan or record[6] == '(Online)' or record[5] == 'null':
            continue
        course_code = record[1]
        course_section = str(int(record[3]))
        if course_code not in course_list:
            course_name = record[2]
            course_credit = int(record[4])
            course_code_split = course_code.split()
            course_department = course_code_split[0]
            course_url = f"https://ce.ieu.edu.tr/en/syllabus/type/read/id/{course_code_split[0]}+{course_code_split[1]}"

            course_list[course_code] = {
                'code': course_code,
                'name': course_name,
                'department': course_department,
                'credits': course_credit,
                'url': course_url,
                'sections': {}
            }
        start_split = record[6].split('\xa0', maxsplit=1)
        end_split = record[7].split('\xa0', maxsplit=1)

        interval_start, interval_end = start_split[0], end_split[0]

        if course_section not in course_list[course_code]['sections']:
            course_list[course_code]['sections'][course_section] = {
                # "type": course_type,
                "time_table": [],
                "time_table_index": [],
                "types": []
            }

        course_list[course_code]['sections'][course_section]['types'].append(start_split[1])

        course_day = record[5]
        day_index = days_to_index[course_day]
        start_index = hours_to_index[interval_start]
        end_index = hours_to_index[interval_end]

        for i in range(start_index, end_index + 1):
            course_list[course_code]['sections'][course_section]['time_table_index'].append([day_index, i])

    with open('data/course_list.json', mode='w', encoding='utf8') as out_file:
        json.dump(course_list, out_file, indent=4)


def fix_lecturer_names():
    with open('data/course_list.json', mode='r+', encoding='utf8') as io_file:
        course_list = json.load(io_file)
        for course in course_list.values():
            for k, v in course['sections'].items():
                split_name = v['lecturer'].split()
                v['lecturer'] = f'{split_name[0]}{split_name[1]}'
        json.dump(course_list, io_file, indent=4)


def fix_time_table():
    with open('test.json', mode='r+', encoding='utf8') as io_file:
        course_list = json.load(io_file)
        for course in course_list.values():
            for section in course['sections'].values():
                temp_day = -1
                temp_end = -1
                full_string = True
                new_table = False
                for i in range(len(section['time_table_index'])):
                    d, h = section['time_table_index'][i]
                    if i == len(section['time_table_index']) - 1:
                        section['time_table'].append(f'{full_string}{index_to_end_hours[h]}')
                    elif new_table:
                        full_string += f'{index_to_days[d]} {index_to_start_hours[h]} - '
                        temp_day = d
                        temp_end = h
                        new_table = False
                    elif temp_day == d:
                        if temp_end + 1 == h:
                            temp_end = h
                        else:
                            section['time_table'].append(f'{full_string}{index_to_end_hours[temp_end]}')
                            full_string = ''
                            new_table = True
                    elif temp_day != d:
                        section['time_table'].append(f'{full_string}{index_to_end_hours[temp_end]}')
                        full_string = ''
                        new_table = True
        json.dump(course_list, io_file, indent=4)


if __name__ == '__main__':
    excel_to_json()
