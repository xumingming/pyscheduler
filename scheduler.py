#!/usr/bin/env python3
# -*-coding: utf-8 -*-

import sys
import getopt
import re
import datetime
import codecs
from math import ceil

class Task:
    def __init__(self, name, man_day, man, status=0, task_id=None):
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
        self.start_point = None
        self.id = task_id

    def start_date(self, project_start_date, vacations):
        return add_days(self.man, project_start_date, vacations, self.start_point)

    def end_date(self, project_start_date, vacations):
        return add_days(self.man, project_start_date, vacations, self.start_point + self.man_day, False)

TASK_LINE_PATTERN = "\*(.+)\-\-\s*([0-9]+\.?[0-9]?)\s*(\[(.+?)\])?(\[([0-9]+)%\])?\s*$"
HEADER_PATTERN = "^#+(.*)"
VACATION_PATTERN = "\*(.+)\-\-\s*([0-9]{4}\-[0-9]{2}\-[0-9]{2})(\s*\-\s*([0-9]{4}\-[0-9]{2}\-[0-9]{2}))?\s*$"
PROJECT_START_DATE_PATTERN = '项目开始时间\:\s*([0-9]{4}\-[0-9]{2}\-[0-9]{2})'

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
    id_to_start_point = {}
    for task in tasks:
        if not curr_days.get(task.man):
            curr_days[task.man] = 0
        task.start_point = curr_days[task.man]
        curr_days[task.man] += task.man_day

        if task.id:
            id_to_start_point[task.id] = task.start_point

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
    pretty_print(repeat(task_name_len), repeat(MAN_LEN), repeat(MAN_DAY_LEN), 
                 repeat(START_DATE_LEN), repeat(END_DATE_LEN), repeat(STATUS_LEN), 
                 task_name_len)

def pretty_print(task_name, man, man_day, start_date, end_date, status, task_name_len):
    actual_task_name = format_with_width(task_name, task_name_len)
    actual_man = format_with_width(man, MAN_LEN)
    actual_man_day = format_with_width(str(man_day), MAN_DAY_LEN)
    actual_start_date = format_with_width(str(start_date), START_DATE_LEN)
    actual_end_date = format_with_width(str(end_date), END_DATE_LEN)
    actual_status = format_with_width(str(status), STATUS_LEN)

    print("{} | {} | {} | {} | {} | {}".format(actual_task_name, actual_man, actual_man_day, 
                                               actual_start_date, actual_end_date, actual_status))

def pretty_print_task(task, project_start_date, vacations, task_name_len):
    pretty_print(task.name, task.man, task.man_day, task.start_date(project_start_date, vacations), 
                 task.end_date(project_start_date, vacations), str(task.status) + "%", task_name_len)

def pretty_print_man_stats(tasks):
    man2days = {}
    for task in tasks:
        if not man2days.get(task.man):
            man2days[task.man] = 0
        man2days[task.man] += task.man_day

    for man in man2days.keys():
        print("{}: {}".format(man, man2days[man]))
        
def pretty_print_scheduled_tasks(tasks, project_start_date, target_man, vacations):
    # pretty print the scheduler
    max_len = find_max_length_of_tasks(tasks)
    pretty_print('任务', '责任人', '所需人日', '开始时间', '结束时间', '进度', max_len)
    pretty_print_second_line(max_len)

    total_man_days = 0
    cost_man_days = 0
    for task in tasks:
        if not target_man or task.man == target_man:
            total_man_days += task.man_day
            cost_man_days += task.man_day * task.status / 100
            pretty_print_task(task, project_start_date, vacations, max_len)

    project_status = 0
    if total_man_days > 0:
        project_status = cost_man_days / total_man_days

    print("")
    print(">> 总人日: {}, 已经完成的人日: {:.2f}, 完成度: {:.2%}".format(total_man_days,
                                                               cost_man_days,
                                                               project_status))
    
def find_max_length_of_tasks(tasks):
    ret = 0
    for task in tasks:
        if actual_width_str(task.name) > ret:
            ret = actual_width_str(task.name)

    return ret

def parse_date(input):
    return datetime.datetime.strptime(input, '%Y-%m-%d').date()

def parse(filepath, append_section_title, target_man, print_man_stats):
    f = codecs.open(filepath, 'r', 'utf-8')    
    s = f.read()
    lines = s.split('\n')
    tasks = []
    vacations = {}

    project_start_date = None
    curr_header = None
    for line in lines:
        m = re.search(TASK_LINE_PATTERN, line)
        if m:
            task_name = m.group(1).strip()
            if curr_header and append_section_title:
                task_name = curr_header + ": " + task_name
            task_id = None
            if task_name.find("ID:") >= 0:
                start_idx = task_name.find("ID:") + 3
                print(task_name[start_idx:])
                end_idx = start_idx + task_name[start_idx:].find(" ")
                task_id = task_name[start_idx:end_idx]
                task_name = task_name[end_idx + 1:]
                print("task id is ", start_idx, ", ", end_idx)
                
            man_day = m.group(2).strip()
            man_day = float(man_day)
            man = m.group(4)
            if man:
                man = man.strip()
            else:
                man = "TODO"

            status = 0
            if m.group(6):
                status = m.group(6).strip()
            task = Task(task_name, man_day, man, status, task_id)
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
            else:
                m = re.search(PROJECT_START_DATE_PATTERN, line)
                if m and m.group(1):
                    project_start_date = parse_date(m.group(1).strip())
                else:
                    m = re.search(HEADER_PATTERN, line)

                    if m:
                        curr_header = m.group(1)

    if not project_start_date:
        print("Please provide project_start_date!")
        exit(1)

    schedule(tasks)
    pretty_print_scheduled_tasks(tasks, project_start_date, target_man, vacations)
    if print_man_stats:
        pretty_print_man_stats(tasks)

        
def help():
    print("""用法: scheduler.py <options> /path/to/work-breakdown-file.markdown

Options:
  -m <man> 只显示指定人的任务
  -t 把每个section的标题apppend到这个section下面所有任务名称前面去
  -s 显示每个人的任务数统计信息
""")

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], 'm:ts')
    if not args or len(args) != 1:
        help()
        exit(1)
    
    filepath = args[0]
    man = None
    append_section_title = False
    print_man_stats = False
    for opt_name, opt_value in opts:
        opt_value = opt_value.strip()
        if opt_name == '-m':
            man = opt_value
        elif opt_name == '-t':
            append_section_title = True
        elif opt_name == '-s':
            print_man_stats = True
                

    parse(filepath, append_section_title, man, print_man_stats)
