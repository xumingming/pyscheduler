# -*-coding: utf-8 -*-
from bottle import route, run, template, static_file, get, view, request
from scheduler import parse
from datetime import date
import os, sys

FILE_PATH = None
class Options:
    def __init__(self, color = True,
                 task_not_started = True,
                 task_in_progress = True,
                 task_finished = True,
                 task_ontime = True,
                 task_overdue = True,
                 task_excel = True,
                 man = None
    ):
        self.color = color
        self.task_not_started = task_not_started
        self.task_in_progress = task_in_progress
        self.task_finished = task_finished
        self.task_ontime = task_ontime
        self.task_overdue = task_overdue
        self.task_excel = task_excel
        self.man = man

def filter_tasks(project, options):
    today = date.today()    
    tasks = []
    
    if options.task_not_started:
        tasks.extend([task for task in project.tasks if task.status == 0])
            
    if options.task_in_progress:
        tasks.extend([task for task in project.tasks if task.status > 0 and task.status < 100])
            
    if options.task_finished:
        tasks.extend([task for task in project.tasks if task.status == 100])

    if options.task_overdue:
        tasks.extend([task for task in project.tasks if task.end_date <= today and task.status < 100])

    if options.task_ontime:
        tasks.extend([task for task in project.tasks if (task.end_date <= today and task.status == 100
                                                         ) or (task.end_date > today and task.status == 0)])
            
    if options.task_excel:
        tasks.extend([task for task in project.tasks if task.end_date > today and task.status > 0])

    project.tasks = tasks

def list_breakdown_files():
    files = os.listdir("/Users/xumingmingv/local/alipay/xlab.wiki")
    files = [f for f in files if f.find("breakdown") > 0]

    return files
    
@route('/')
@view('table')
def index():
    color = ("color" in request.params)
    task_not_started = ("task_not_started" in request.params)
    task_in_progress = ("task_in_progress" in request.params)
    task_finished = ("task_finished" in request.params)
    task_ontime = ("task_ontime" in request.params)
    task_overdue = ("task_overdue" in request.params)
    task_excel = ("task_excel" in request.params)            
    man = ("man" in request.params)
    if man:
        man = request.params.man
    
    options = Options(
        color = color,
        task_not_started = task_not_started,
        task_in_progress = task_in_progress,
        task_finished = task_finished,
        task_ontime = task_ontime,
        task_overdue = task_overdue,
        task_excel = task_excel,
        man = man
    )

    files = list_breakdown_files()
    project = parse(FILE_PATH)

    # filter the tasks acoording to task status
    filter_tasks(project, options)
    
    # filter the tasks according to man
    if options.man and not options.man == "All":
        project.tasks = [task for task in project.tasks if task.man == options.man]

    print(files)
    return dict(project = project, options = options, files = files)

# Static Routes
@get('/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root='static/js')

@get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='static/css')

@get('/<filename:re:.*\.(jpg|png|gif|ico)>')
@get('/images/<filename:re:.*\.(jpg|png|gif|ico)>')
def images(filename):
    return static_file(filename, root='static/images')

@get('/<filename:re:.*\.(eot|ttf|woff|svg)>')
def fonts(filename):
    return static_file(filename, root='static/')


if __name__ == '__main__':
    FILE_PATH = sys.argv[1]
    run(host='localhost', port=8080)


