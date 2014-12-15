#!/usr/bin/env python3
# -*-coding: utf-8 -*-

import sys
import getopt
import re
import datetime
import codecs
from math import ceil

class Task:
    def __init__(self, name, man_day, man, status=0):
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

    def start_date(self, project_start_date, vacations):
        return add_days(self.man, project_start_date, vacations, self.start_point)

    def end_date(self, project_start_date, vacations):
        return add_days(self.man, project_start_date, vacations, self.start_point + self.man_day, False)

TASK_LINE_PATTERN = "\*(.+)\-\-\s*([0-9]+\.?[0-9]?)\s*(\[(.+?)\])?(\[([0-9]+)%\])?\s*$"
HEADER_PATTERN = "^(#+)(.*)"
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
            man2days[task.man] = [0,0] # finished_man_days, total_man_days

        task_status = task.status
        man_days = task.man_day
        
        finished_man_days = task_status * man_days / 100
        man2days[task.man][0] = man2days[task.man][0] + finished_man_days
        man2days[task.man][1] = man2days[task.man][1] + man_days
        
    for man in sorted(man2days):
        finished_man_days = man2days[man][0]        
        total_man_days = man2days[man][1]
        total_status = (finished_man_days / total_man_days) * 100
        
        print("{}: {}/{} {:.0f}%".format(man, finished_man_days, total_man_days, total_status))
        
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

def get_headers_as_str(headers):
    return "-".join([header for [_, header] in headers])

def parse_header_line(curr_headers, m):
    new_header_level = len(m.group(1).strip())
    new_header = m.group(2).strip()    
    for i in range(len(curr_headers)):
        header_level, header = curr_headers[len(curr_headers) - 1 - i]
        if new_header_level <= header_level:
            curr_headers.pop()
            
    curr_headers.append([new_header_level, new_header])

def parse_task_line(tasks, curr_headers, append_section_title, m):
    task_name = m.group(1).strip()
    if len(curr_headers) > 0 and append_section_title:
        task_name = get_headers_as_str(curr_headers) + "-" + task_name
        
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
         
    task = Task(task_name, man_day, man, status)
    tasks.append(task)

def parse_vacation_line(vacations, m):
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
    
def parse(filepath, append_section_title, target_man, print_man_stats, only_nonstarted):
    f = codecs.open(filepath, 'r', 'utf-8')    
    s = f.read()
    lines = s.split('\n')
    tasks = []
    vacations = {}

    project_start_date = None
    curr_headers = []
    for line in lines:
        m = re.search(TASK_LINE_PATTERN, line)
        if m:
            parse_task_line(tasks, curr_headers, append_section_title, m)
        else:
            m = re.search(VACATION_PATTERN, line)
            if m:
                parse_vacation_line(vacations, m)
            else:
                m = re.search(PROJECT_START_DATE_PATTERN, line)
                if m and m.group(1):
                    project_start_date = parse_date(m.group(1).strip())
                else:
                    m = re.search(HEADER_PATTERN, line)
                    if m:
                        parse_header_line(curr_headers, m)
                        
    if not project_start_date:
        print("请在文件中指定项目开始时间！")
        exit(1)

    schedule(tasks)

    # filter the tasks
    if only_nonstarted:
        tasks = [task for task in tasks if task.status == 0]
    
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
    opts, args = getopt.getopt(sys.argv[1:], 'm:tsn')
    if not args or len(args) != 1:
        help()
        exit(1)
    
    filepath = args[0]
    man = None
    append_section_title = False
    print_man_stats = False
    only_nonstarted = False
    for opt_name, opt_value in opts:
        opt_value = opt_value.strip()
        if opt_name == '-m':
            man = opt_value
        elif opt_name == '-t':
            append_section_title = True
        elif opt_name == '-s':
            print_man_stats = True
        elif opt_name == '-n':
            only_nonstarted = True

    parse(filepath, append_section_title, man, print_man_stats, only_nonstarted)
