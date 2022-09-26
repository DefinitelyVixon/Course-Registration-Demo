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

hours_to_index = {'08:30': 0, '09:15': 0, '09:25': 1, '10:10': 1, '10:20': 2, '11:05': 2, '11:15': 3, '12:00': 3,
                  '12:10': 4, '12:55': 4, '13:05': 5, '13:50': 5, '14:00': 6, '14:45': 6, '14:55': 7, '15:40': 7,
                  '15:50': 8, '16:35': 8, '16:45': 9, '17:30': 9, '17:40': 10, '18:25': 10, '18:35': 11, '19:20': 11,
                  '19:30': 12, '20:15': 12, '20:25': 13, '21:10': 13, '21:20': 14, '22:05': 14, '22:15': 15,
                  '23:00': 15, '23:10': 16, '23:55': 16}

index_to_start_hours = ['08:30', '09:25', '10:20', '11:15', '12:10', '13:05', '14:00', '14:55', '15:50', '16:45',
                        '17:40', '18:35', '19:30', '20:25', '21:20', '22:15', '23:10']
index_to_end_hours = ['09:15', '10:10', '11:05', '12:00', '12:55', '13:50', '14:45', '15:40', '16:35', '17:30',
                      '18:25', '19:20', '20:15', '21:10', '22:05', '23:00', '23:55']


def excel_to_json(input_path, output_path):
    dtypes = {'section': 'Int8',
              'ects': 'Int8'}

    excel = pd.read_excel(input_path, dtype=dtypes).fillna(method='ffill')
    records = excel.to_records()
    course_dict = {}

    # 0 - Code
    # 1 - Name
    # 2 - Section
    # 3 - ECTS
    # 4 - Day
    # 5,6 - Start, End Hour
    # 7 - Classroom

    for record in records:
        print(record)
        course_code = record['code']
        course_section = record['section']
        if course_code not in course_dict:
            course_name = record['name']
            course_credit = int(record['ects'])
            course_code_split = course_code.split()
            course_department = course_code_split[0]
            course_url = f"https://ce.ieu.edu.tr/en/syllabus/type/read/id/{course_code_split[0]}+{course_code_split[1]}"
            course_dict[course_code] = {
                'code': course_code,
                'name': course_name,
                'department': course_department,
                'credits': course_credit,
                'url': course_url,
                'sections': {}
            }
        interval_start = record['start']  # .split('\xa0', maxsplit=1)
        interval_end = record['end']  # .split('\xa0', maxsplit=1)
        course_classroom = record['class']

        if course_section not in course_dict[course_code]['sections']:
            course_dict[course_code]['sections'][course_section] = {
                "time_table": [],
                "time_table_index": [],
                "types": []
            }

        course_day = record['day'].split('\xa0')[0]
        day_index = days_to_index[course_day]
        start_index = hours_to_index[interval_start]
        end_index = hours_to_index[interval_end]

        for i in range(start_index, end_index + 1):
            course_dict[course_code]['sections'][course_section]['time_table_index'].append([day_index, i])
            course_dict[course_code]['sections'][course_section]['types'].append(course_classroom)

    with open(output_path, mode='w', encoding='utf8') as out_file:
        json.dump(course_dict, out_file, indent=4)


if __name__ == '__main__':
    excel_to_json(input_path='data/course_list_4_1.xlsx', output_path='data/course_list_4_1.json')
