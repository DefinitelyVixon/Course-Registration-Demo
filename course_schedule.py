import json
import os
import sys
import PySimpleGUI as sg


def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)


sg.theme('Dark')
sg.popup_quick_message('Hang on for a moment, this will take a bit to create....', auto_close=True, non_blocking=True)

weekdays = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
hours = ['08:30\n09:10', '09:20\n10:00', '10:10\n10:50', '11:00\n11:40', '11:50\n12:30', '12:40\n13:20', '13:30\n14:10',
         '14:20\n15:00', '15:10\n15:50', '16:00\n16:40', '16:50\n17:30', '17:40\n18:20', '18:30\n19:10', '19:20\n20:00',
         '20:10\n20:50', '21:00\n21:40']
weekdays_in_one_line = f'{" " * 15}MON{" " * 11}TUE{" " * 13}WED{" " * 11}THU{" " * 13}FRI{" " * 14}SAT{" " * 13}SUN'
filename = 'data/course_list.json'

with open(resource_path(filename), mode='r', encoding='utf8') as in_file:
    courses = json.load(in_file)

data = [[x['code'], x['name'], x['credits'], x['department']] for x in courses.values()]

search_table = [[sg.Table(values=data,
                          headings=['Code', 'Name', 'ECTS', 'Dept'],
                          display_row_numbers=False,
                          auto_size_columns=False,
                          visible_column_map=[True, True, True, False],
                          col_widths=[8, 38, 4, 0],
                          num_rows=min(35, len(data)),
                          font=6,
                          select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                          enable_events=True,
                          justification='center',
                          key='-search_table-',
                          expand_y=True)]]

selected_course_dic = {}
selected_table = [[sg.Table(values=[],
                            headings=['Code', 'Name', 'Section', 'ECTS', 'TTI'],
                            visible_column_map=[True, True, True, True, False],
                            display_row_numbers=False,
                            auto_size_columns=False,
                            hide_vertical_scroll=True,
                            col_widths=[8, 26, 6, 4, 0],
                            num_rows=max(13, len(selected_course_dic.values())),
                            select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                            enable_events=True,
                            justification='center',
                            key='-selected_table-')],
                  [sg.Button('Remove', button_color=('White', 'Red'), enable_events=True, key='-course_remove-',
                             bind_return_key=True, expand_x=True),
                   sg.Button('Remove All', button_color=('White', 'Orange'), enable_events=True, key='_course-reset_',
                             bind_return_key=True, expand_x=True, auto_size_button=True),
                   sg.Text('Total ECTS: ', pad=((25, 0), (0, 0))),
                   sg.Multiline('0', size=(5, 1), justification='center', key='-total_ects-', no_scrollbar=True,
                                disabled=True)]]
filter_column = [
    [sg.Frame('Filters', [
        [sg.Input(key='-input-', size=(23, 1))],
        [sg.Listbox(values=[], key='-listbox-', size=(23, 12), enable_events=True, no_scrollbar=True)],
        [sg.Button('Add', button_color=('White', 'Green'), enable_events=True, key='-filter_add-', bind_return_key=True,
                   size=(5, 1)),
         sg.Button('Remove', disabled=True, button_color=('Black', 'Grey'), enable_events=True, key='-filter_remove-',
                   size=(5, 1), expand_x=True),
         sg.Button('Reset All', button_color=('White', 'Red'), enable_events=True, key='-filter_reset-')]
    ], element_justification='center'),
     sg.Frame('Selected Courses', selected_table, expand_x=True)],
    [sg.Frame('', search_table, expand_y=True)]
]

filtered_courses = set()
schedule_column = [[sg.T(weekdays_in_one_line)]] + \
                  [[sg.T(hours[y])] + [
                      sg.Multiline(size=(10, 3), key=(x, y), disabled=True, justification='center', no_scrollbar=True)
                      for x in range(len(weekdays))] for y in range(len(hours))]

layout = [[sg.Column(filter_column), sg.Column(schedule_column, key='_schedule-column_')]]
window = sg.Window('Weekly Schedule', layout, default_element_size=(12, 1), element_padding=(1, 1),
                   return_keyboard_events=True)

while True:

    event, values = window.read()


    def remove_from_table(conflicts):
        for conflict in conflicts:
            split_info = conflict.split(' | ')
            conflict_code = split_info[0]
            for day, hour in selected_course_dic[conflict_code]['time_table_index']:
                window[(day, hour)].update('')
            selected_course_dic.pop(conflict_code)
            # window['-total_ects-'].update(int(int(values['-total_ects-']) - int(split_info[2])))
            window['-total_ects-'].update(int(int(values['-total_ects-']) - courses[conflict_code]['credits']))
            window['-selected_table-'].update([x['info'] for x in selected_course_dic.values()])


    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == '-search_table-' and len(values['-search_table-']):
        data_selected = [window['-search_table-'].get()[row] for row in values[event]]
        selected_course = courses[data_selected[0][0]]
        sections = selected_course['sections']


        def values_if_selected(course_key, course_section, return_value):
            button_colors = [('White', 'Green'), ('Black', 'Grey')]
            if course_key in selected_course_dic.keys():
                course_exists = True
                if course_section == selected_course_dic[course_key]['info'][2]:
                    course_section_exists = True
                else:
                    course_section_exists = False
            else:
                course_exists = course_section_exists = False
            if return_value == 'button_color':
                return button_colors[course_section_exists]
            elif return_value == 'disabled':
                return bool(course_section_exists)
            elif return_value == 'bool':
                return bool(course_exists)


        def convert_types(types):
            if len(set(types)) > 1:
                return 'Hybrid'
            else:
                return types[0]


        section_layout = [[sg.Text(f'Section {k} | {convert_types(v["types"])} | {v["time_table"]}', expand_x=True),
                           sg.Button('Select',
                                     key=f'section-{k}',
                                     button_color=values_if_selected(selected_course['code'], k, 'button_color'),
                                     disabled=values_if_selected(selected_course['code'], k, 'disabled')),
                           sg.HorizontalSeparator()] for k, v in sections.items()]
        section_window = sg.Window('Sections',
                                   [[sg.Column(section_layout, scrollable=True, vertical_scroll_only=True)]])


        def add_to_table():
            conflicts = set()
            day_hour_indexes = []
            for day_index, hour_index in sections[selected_section_id]['time_table_index']:
                if values[(day_index, hour_index)] != '':
                    already_added = False
                    for conflict in conflicts:
                        if conflict.split(' | ')[0] == selected_course['code']:
                            already_added = True
                            break
                    if not already_added:
                        conflict = values[(day_index, hour_index)].split('\n')
                        conflicts.add(f'{conflict[0]} | {conflict[1]} | {convert_types(conflict[2])}')
                elif values_if_selected(selected_course['code'], selected_section_id, 'bool'):
                    already_added = False
                    for conflict in conflicts:
                        if conflict.split(' | ')[0] == selected_course['code']:
                            already_added = True
                            break
                    if not already_added:
                        conflicts.add(f"{selected_course['code']} | "
                                      f"Section {selected_section_id} | "
                                      f"{convert_types(selected_course['sections'][selected_section_id]['types'])}")
                day_hour_indexes.append([day_index, hour_index])
            if len(conflicts) > 0:
                conflict_message = "This selection conflicts with:\n"
                for conflict in conflicts:
                    conflict_message += f'{conflict}\n'
                conflict_message += "\nDo you want to replace?"

                choice = sg.popup_yes_no(conflict_message)
                if choice == 'Yes':
                    remove_from_table(conflicts)
                else:
                    return
            i = 0
            print(day_hour_indexes)
            for day, hour in day_hour_indexes:
                window[(day, hour)].update(
                    f'{selected_course["code"]}\n'
                    f'Section {selected_section_id}\n'
                    f'{selected_course["sections"][selected_section_id]["types"][i]}')
                i += 1

            selected_course_dic[selected_course['code']] = {
                'info': [selected_course['code'], selected_course['name'], selected_section_id,
                         selected_course['credits']],
                'time_table_index': selected_course['sections'][selected_section_id]['time_table_index']
            }
            window['-total_ects-'].update(int(int(values['-total_ects-']) + selected_course['credits']))
            window['-selected_table-'].update([x['info'] for x in selected_course_dic.values()])


        while True:
            event_, values_ = section_window.read()
            if event_ in (sg.WIN_CLOSED, 'Exit'):
                break
            elif event_.startswith('section'):
                selected_section_id = event_.split('-')[1]
                add_to_table()
                break
        section_window.close()

    elif event == '-listbox-' and len(filtered_courses) > 0:
        window['-filter_remove-'].update(disabled=False, button_color=('White', 'Green'))
    elif event == '-filter_add-':
        filter_to_add = values['-input-'].upper()
        if filter_to_add == '31':
            filtered_courses.add('SJ')
        else:
            filtered_courses.add(filter_to_add)
        window['-input-'].update('')
        window['-listbox-'].update(filtered_courses)
        window['-filter_remove-'].update(disabled=True, button_color=('Black', 'Grey'))
    elif event == '-filter_remove-':
        filtered_courses.discard(values['-listbox-'][0])
        window['-listbox-'].update(filtered_courses)
        window['-filter_remove-'].update(disabled=True, button_color=('Black', 'Grey'))
    elif event == '-filter_reset-':
        filtered_courses = set()
        window['-listbox-'].update(values=[])
        window['-search_table-'].update(data)
        window['-filter_remove-'].update(disabled=True, button_color=('Black', 'Grey'))
        continue
    elif event == '-course_remove-' and len(selected_course_dic.keys()) > 0:
        select_index = values['-selected_table-'][0]
        data_selected = window['-selected_table-'].get()[select_index]
        remove_from_table([f'{data_selected[0]} | {data_selected[2]} | {data_selected[3]}'])
    elif event == '_course-reset_':
        selected_course_dic = {}
        for d in range(7):
            for h in range(16):
                window[(d, h)].update('')
        window['-selected_table-'].update([])
        window['-total_ects-'].update(0)
    else:
        continue
    new_table = [x for x in data if x[3] in filtered_courses or len(filtered_courses) == 0]
    window['-search_table-'].update(new_table)

window.close()
