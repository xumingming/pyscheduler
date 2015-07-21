#!/usr/bin/env python3
# -*-coding: utf-8 -*-

import sys
import getopt
import parser
import codecs

def find_max_length_of_tasks(tasks):
    ret = 0
    for task in tasks:
        if actual_width_str(task.name) > ret:
            ret = actual_width_str(task.name)

    return ret

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

MAN_LEN = 10
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

def pretty_print_task(project, task):
    pretty_print(task.name, task.man, task.man_day, project.task_start_date(task), 
                 project.task_end_date(task), str(task.status) + "%", find_max_length_of_tasks(project.tasks))

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
        
        print("{}: {:.0f}/{} {:.0f}%".format(man, finished_man_days, total_man_days, total_status))
        
def pretty_print_scheduled_tasks(project, options):
    # pretty print the scheduler
    max_length_of_tasks = find_max_length_of_tasks(project.tasks)
    if options.english:
        pretty_print('Task', 'Developer', 'Man-days', 'Start Date', 'End Date', 'Progress', max_length_of_tasks)
    else:
        pretty_print('任务', '责任人', '所需人日', '开始时间', '结束时间', '进度', max_length_of_tasks)

    pretty_print_second_line(max_length_of_tasks)

    for task in project.tasks:
        if not options.man or task.man == options.man:
            pretty_print_task(project, task)
            
    print("")

    if options.english:
        print(">> Total mandays: {}, Finished mandays: {:.2f}, Progress: {:.2%}".format(project.total_man_days,
                                                                                        project.cost_man_days,
                                                                                        project.status))
    else:
        print(">> 总人日: {}, 已经完成的人日: {:.2f}, 完成度: {:.2%}".format(project.total_man_days,
                                                                             project.cost_man_days,
                                                                             project.status))
    
    
def parse_and_print(filepath, options):
    f = codecs.open(filepath, 'r', 'utf-8')
    content = f.read()
    f.close()
    
    project = parser.parse(content)
    # filter the tasks
    if options.only_nonstarted:
        project.tasks = [task for task in project.tasks if task.status < 100]
    
    pretty_print_scheduled_tasks(project, options)
    if options.print_man_stats:
        pretty_print_man_stats(project.tasks)

        
def help():
    print("""用法: scheduler.py <options> /path/to/work-breakdown-file.markdown

Options:
  -m <man> 只显示指定人的任务
  -t 把每个section的标题apppend到这个section下面所有任务名称前面去
  -s 显示每个人的任务数统计信息
""")

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], 'm:tsne')
    if not args or len(args) != 1:
        help()
        exit(1)
    
    filepath = args[0]
    man = None

    options = parser.Options()
    for opt_name, opt_value in opts:
        opt_value = opt_value.strip()
        if opt_name == '-m':
            options.man = opt_value
        elif opt_name == '-s':
            options.print_man_stats = True
        elif opt_name == '-n':
            options.only_nonstarted = True
        elif opt_name == '-e':
            options.english = True

    parse_and_print(filepath, options)
