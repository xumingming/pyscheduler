# pyscheduler spec

## Define the `project start date`

```bash
* ProjectStartDate: 2015-07-21
```

This project will start at `2015-07-21`.

## Define a task

### A task which is not assigned

```bash
* task1 -- 2
```

This task named `task1` is evaluated to be 2 man-days.

### A task which is assigned

```bash
* task1 -- 2[James]
```

This task is assigned to a guy named `James`.

### A task which has progress

```bash
* task1 -- 2[James][90%]
```

This task's progress is about `90%`.

## Define a `time off`

```bash
* James -- 2015-07-21 - 2015-07-25
```

James will be not in this project between `2015-07-21` and `2015-07-25`.
