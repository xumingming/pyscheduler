# -*-coding: utf-8 -*-

import sys
import re
import datetime
from math import ceil

class Task:
    def __init__(self, name, man_day, man, project_start_date, status=0):
        """
        Arguments:
        - `self`:
        - `name`:
        - `man_day`
        """
        self.name = name
        self.man_day = man_day
        self.man = man
        self.status = int(status)
        self.project_start_date = project_start_date

        self.start_point = None

    def start_date(self, vacations):
        return add_days(self.man, self.project_start_date, vacations, self.start_point)

    def end_date(self, vacations):
        return add_days(self.man, self.project_start_date, vacations, self.start_point + self.man_day, False)

TASK_LINE_PATTERN = "\*(.+)\-\-\s*([0-9]+\.?[0-9]?)\s*\[(.+)\](\(([0-9]+)%\))?"
VACATION_PATTERN = "\*(.+)\-\-\s*([0-9]{4}\-[0-9]{2}\-[0-9]{2})(\s*\-\s*([0-9]{4}\-[0-9]{2}\-[0-9]{2}))?"
def skip_weekend(date1):
    weekday = date1.isoweekday()
    if weekday > 5:
        padding_days = (7 - weekday) + 1
        date1 = date1 + datetime.timedelta(days=padding_days)
        return True, date1
    else:
        return False, date1


def skip_vacation(man, date1, vacations):
    if vacations.get(man) and vacations.get(man).count(str(date1)) > 0:
        date1 = date1 + datetime.timedelta(days=1)
        return True, date1
    else:
        return False, date1

def add_days(man, curr_day, vacations, days, is_start_date = True):
    idx = int(ceil(days))
    if idx > days:
        idx -= 1
    else:
        if not is_start_date:
            idx -= 1

    ret = curr_day
    while idx > 0:
        ret = ret + datetime.timedelta(days=1)

        # skip the weekend and vacations
        while True:
            skipped, ret = skip_weekend(ret)
            skipped, ret = skip_vacation(man, ret, vacations)
            
            if not skipped:
                break

        idx -= 1

    return ret

def schedule(tasks):
    curr_days = {}
    for task in tasks:
        if not curr_days.get(task.man):
            curr_days[task.man] = 0
        task.start_point = curr_days[task.man]
        curr_days[task.man] += task.man_day

def actual_width(ch):
    if ord(ch) < 256:
        return 1

    return 2

def actual_width_str(input):
    ret = 0
    for ch in input:
        ret += actual_width(ch)

    return ret

def format_with_width(input, width):
    target = input
    actual_width = actual_width_str(input)

    delta = width - actual_width
    if delta > 0:
        for i in range(delta):
            target += ' '

    return target

def repeat(cnt):
    ret = ''
    for i in range(cnt):
        ret += '-'

    return ret

MAN_LEN = 6
MAN_DAY_LEN = 8
START_DATE_LEN = 10
END_DATE_LEN = 10
STATUS_LEN = 4
def pretty_print_second_line(task_name_len):
    pretty_print(repeat(task_name_len), repeat(MAN_LEN), repeat(MAN_DAY_LEN), repeat(START_DATE_LEN), repeat(END_DATE_LEN), repeat(STATUS_LEN), task_name_len)

def pretty_print(task_name, man, man_day, start_date, end_date, status, task_name_len):
    actual_task_name = format_with_width(task_name, task_name_len)
    actual_man = format_with_width(man, MAN_LEN)
    actual_man_day = format_with_width(str(man_day), MAN_DAY_LEN)
    actual_start_date = format_with_width(str(start_date), START_DATE_LEN)
    actual_end_date = format_with_width(str(end_date), END_DATE_LEN)
    actual_status = format_with_width(str(status), STATUS_LEN)

    print("{} | {} | {} | {} | {} | {}".format(actual_task_name, actual_man, actual_man_day, actual_start_date, actual_end_date, actual_status))

def pretty_print_task(task, vacations, task_name_len):
    pretty_print(task.name, task.man, task.man_day, task.start_date(vacations), task.end_date(vacations), str(task.status) + "%", task_name_len)

def find_max_length_of_tasks(tasks):
    ret = 0
    for task in tasks:
        if actual_width_str(task.name) > ret:
            ret = actual_width_str(task.name)

    return ret

def parse_date(input):
    return datetime.datetime.strptime(input, '%Y-%m-%d').date()

def parse(filepath, project_start_date, target_man=None):
    f = open(filepath, 'r')
    s = f.read()
    lines = s.split('\n')
    tasks = []
    vacations = {}

    for line in lines:
        m = re.search(TASK_LINE_PATTERN, line)
        if m:
            task_name = m.group(1).strip()
            man_day = m.group(2).strip()
            man_day = float(man_day)
            man = m.group(3).strip()
            status = 0
            if m.group(5):
                status = m.group(5).strip()
            task = Task(task_name, man_day, man, project_start_date, status)
            tasks.append(task)
        else:
            m = re.search(VACATION_PATTERN, line)
            if m:
                man = m.group(1).strip()
                vacation_date = parse_date(m.group(2).strip())
                vacation_date_end = vacation_date
                if m.group(4):
                    vacation_date_end = parse_date(m.group(4).strip())

                if not vacations.get(man):
                    vacations[man] = []

                xdate = vacation_date
                while xdate <= vacation_date_end:
                    vacations[man].append(str(xdate))
                    xdate += datetime.timedelta(days=1)

    stat = {}
    for task in tasks:
        if not stat.get(task.man):
            stat[task.man] = 0

        stat[task.man] += task.man_day

    schedule(tasks)

    # pretty print the content
    max_len = find_max_length_of_tasks(tasks)
    pretty_print('任务', '责任人', '所需人日', '开始时间', '结束时间', '进度', max_len)
    pretty_print_second_line(max_len)

    total_man_days = 0
    for task in tasks:
        if not target_man or task.man == target_man:
            total_man_days += task.man_day
            pretty_print_task(task, vacations, max_len)
    
    pretty_print(' ', ' ', total_man_days, ' ', ' ', ' ', max_len)

if __name__ == '__main__':
    project_start_date = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
    filepath = sys.argv[2]
    man = None
    if len(sys.argv) == 4:
        man = sys.argv[3]


    parse(filepath, project_start_date, man)
