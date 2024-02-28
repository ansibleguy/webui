function updateApiTableDataJob(row, row2, entry) {
    // job
    row.innerHTML = document.getElementById('aw-api-data-tmpl-row').innerHTML;
    row.cells[0].innerText = entry.name;
    row.cells[1].innerText = entry.inventory_file;
    row.cells[2].innerText = entry.playbook_file;

    if (entry.comment == "") {
        row.cells[3].innerText = '-';
    } else {
        row.cells[3].innerText = entry.comment;
    }
    if (entry.schedule == "") {
        row.cells[4].innerText = '-';
    } else {
        let scheduleHtml = entry.schedule;
        if (!entry.enabled) {
            scheduleHtml += '<br><i>(disabled)</i>';
        }
        row.cells[4].innerHTML = scheduleHtml;
    }

    if (entry.executions.length == 0) {
        var lastExecution = null;
        row.cells[5].innerText = '-';
        row.cells[6].innerText = '-';
    } else {
        var lastExecution = entry.executions[0];
        row.cells[5].innerHTML = shortExecutionStatus(lastExecution);

        if (entry.next_run == null) {
            row.cells[6].innerText = '-';
        } else {
            row.cells[6].innerText = entry.next_run;
        }
    }

    let actionsTemplate = document.getElementById("aw-api-data-tmpl-actions").innerHTML;
    actionsTemplate = actionsTemplate.replaceAll('${ID}', entry.id);
    if (lastExecution != null) {
        actionsTemplate = actionsTemplate.replaceAll('${EXEC_ID_1}', lastExecution.id);
    }
    row.cells[7].innerHTML = actionsTemplate;

    // execution stati
    row2.innerHTML = document.getElementById('aw-api-data-tmpl-row2').innerHTML;
    row2.setAttribute("id", "aw-spoiler-" + entry.id);
    row2.setAttribute("hidden", "hidden");
    row2.innerHTML = row2.innerHTML.replaceAll('${ID}', entry.id);
    let execs = '<div>';
    for (exec of entry.executions) {
        execs += ('<hr><b>Start time</b>: ' + exec.time_start);
        execs += ('<br><b>Finish time</b>: ' + exec.time_fin);
        execs += ('<br><b>Executed by</b>: ' + exec.user_name);
        execs += ('<br><b>Status</b>: <span class="aw-job-status aw-job-status-' + exec.status_name.toLowerCase() + '">' + exec.status_name + '</span>');
        if (is_set(exec.log_stdout) || is_set(exec.log_stderr) || is_set(exec.log_stdout_repo) || is_set(exec.log_stderr_repo)) {
            let exec_logs = [];
            if (is_set(exec.log_stdout)) {
                exec_logs.push('<a href="' + exec.log_stdout_url + '" title="' + exec.log_stdout + '" download>Job Output</a>');
            }
            if (is_set(exec.log_stderr)) {
                exec_logs.push('<a href="' + exec.log_stderr_url + '" title="' + exec.log_stderr + '" download>Job Error</a>');
            }
            if (is_set(exec.log_stdout_repo)) {
                exec_logs.push('<a href="' + exec.log_stdout_repo_url + '" title="' + exec.log_stdout_repo + '" download>Repository Output</a>');
            }
            if (is_set(exec.log_stderr_repo)) {
                exec_logs.push('<a href="' + exec.log_stderr_repo_url + '" title="' + exec.log_stderr_repo + '" download>Repository Error</a>');
            }
            execs += ('<br><b>Logs</b>: ' + exec_logs.join(', '));
        }
        if (is_set(exec.error_s)) {
            execs += ('<br><br><b>Error</b>: <code>' + exec.error_s + '</code>');
        }
    }
    execs += '</div>';
    row2.innerHTML = row2.innerHTML.replaceAll('${EXECS}', execs);
}

$( document ).ready(function() {
    apiEndpoint = "/api/job?executions=true&execution_count=10";
    fetchApiTableData(apiEndpoint, updateApiTableDataJob, true);
    setInterval('fetchApiTableData(apiEndpoint, updateApiTableDataJob, true)', (DATA_REFRESH_SEC * 1000));
});
