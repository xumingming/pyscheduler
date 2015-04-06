<html>
  <head>
	<link type="text/css" href="jquery.dataTables.css" rel="stylesheet">
	<link type="text/css" href="task.css" rel="stylesheet">	
	<script src="jquery.js"></script>
	<script src="jquery.dataTables.min.js"></script>	
	<script src="task.js"></script>
  </head>
  <body>
	<form>
	<table>
	  <tr>
		<td>
		  <%		  
			 task_not_started_checked = ""
			 if options.task_not_started:
    			 task_not_started_checked = "checked"
			 end
			 
			 task_in_progress_checked = ""
			 if options.task_in_progress:
			     task_in_progress_checked = "checked"
			 end
			 
			 task_finished_checked = ""
			 if options.task_finished:
    			 task_finished_checked = "checked"
			 end

			 task_overdue_checked = ""
			 if options.task_overdue:
    			 task_overdue_checked = "checked"
			 end

			 task_ontime_checked = ""
			 if options.task_ontime:
    			 task_ontime_checked = "checked"
			 end

			 task_excel_checked = ""
			 if options.task_excel:
    			 task_excel_checked = "checked"
			 end
			 %>
		  <div class="box">
			<input type="checkbox" name="task_not_started" {{task_not_started_checked}}/>未开始
			<input type="checkbox" name="task_in_progress" {{task_in_progress_checked}}/>进行中
			<input type="checkbox" name="task_finished" {{task_finished_checked}}/>完成
		   </div>
		</td>
		<td>
		  <div class="box">
			<input type="checkbox" name="task_overdue" {{task_overdue_checked}}/>进度落后的
 			<input type="checkbox" name="task_ontime" {{task_ontime_checked}}/>进度正常的
 			<input type="checkbox" name="task_excel" {{task_excel_checked}}/>进度超前的
		  </div>
		</td>
		<td>
		  <div class="box">
			<select name="man">
     		  <option value="All">All</option>			
			  % for man in project.mans:
			  <%
				 man_checked = ""
				 if options.man == man:
     			 man_checked = 'selected="selected"'
				 end
				 %>
			  <option value="{{man}}" {{man_checked}}>{{man}}</option>
			  % end
			</select>
			<%
			   color_checked = ""
			   if options.color:
			   color_checked = "checked"
			   end
			   %>
			<input type="checkbox" name="color" {{color_checked}}/>任务着色
		  </div>
		</td>
		<td>
		  <input type="submit" value="Go">
	  </tr>
	  <tr>
		<td>
		  项目详情:  总体完成度 {{"{:.2%}".format(project.status)}}
		</td>
	  </tr>
	</table>
	</form>
	<table id="tasks">
	  <thead>
        <tr>
          <td>任务</td>
          <td>责任人</td>
          <td>所需人日</td>
          <td>开始时间</td>
          <td>结束时间</td>
          <td>进度</td>
        </tr>
	  </thead>
      <tbody>	
		% for task in project.tasks:
		% if options.color:
     		% if task.status == 100:
            <tr class="finished">
		    % elif task.status == 0:
            <tr class="overdue">
	        % else:
     		<tr>
	    	% end
		% else:
		    <tr>
	    % end
          <td>{{task.name}}</td>
          <td>{{task.man}}</td>
          <td>{{task.man_day}}</td>
          <td>{{project.task_start_date(task)}}</td>
          <td>{{project.task_end_date(task)}}</td>
          <td>{{task.status}}%</td>
        </tr>
		% end
	  </tbody>
	</table>
  </body>
</html>
