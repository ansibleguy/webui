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
        scheduleHtml = entry.schedule;
        if (!entry.enabled) {
            scheduleHtml += '<br><i>(disabled)</i>';
        }
        row.cells[4].innerHTML = scheduleHtml;
    }

    if (entry.executions.length == 0) {
        lastExecution = null;
        row.cells[5].innerText = '-';
        row.cells[6].innerText = '-';
    } else {
        lastExecution = entry.executions[0];
        row.cells[5].innerHTML = shortExecutionStatus(lastExecution);

        if (entry.next_run == null) {
            row.cells[6].innerText = '-';
        } else {
            row.cells[6].innerText = entry.next_run;
        }
    }

    actionsTemplate = document.getElementById("aw-api-data-tmpl-actions").innerHTML;
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
    execs = '<div>';
    for (i = 0, len = entry.executions.length; i < len; i++) {
        exec = entry.executions[i];
        execs += ('<hr><b>Start time</b>: ' + exec.time_start)
        execs += ('<br><b>Finish time</b>: ' + exec.time_fin)
        execs += ('<br><b>Executed by</b>: ' + exec.user_name)
        execs += ('<br><b>Status</b>: <span class="aw-job-status aw-job-status-' + exec.status_name.toLowerCase() + '">' + exec.status_name + '</span>')
        execs += ('<br><b>Logs</b>: <a href="' + exec.log_stdout_url + '" title="' + exec.log_stdout + '" download>Output</a>, ')
        execs += ('<a href="' + exec.log_stderr_url + '" title="' + exec.log_stderr + '" download>Error</a>')
        if (exec.error_s != null) {
            execs += ('<br><br><b>Error</b>: <code>' + exec.error_s + '</code>')
            if (exec.error_m != null) {
                execs += ('<br><b>Error full</b>:<div class="code">' + exec.error_m + '</div>')
            }
        }
    }
    execs += '</div>';
    row2.innerHTML = row2.innerHTML.replaceAll('${EXECS}', execs);
}

function updateApiTableDataJobPlaceholder(dataTable, placeholderId) {
    tmpRow = dataTable.insertRow(1);
    tmpRow.innerHTML = document.getElementById('aw-api-data-tmpl-row').innerHTML;
    tmpRow.removeAttribute("hidden");
    tmpRow.setAttribute("aw-api-entry", placeholderId);

    tableHead = dataTable.rows[0];
    for (i = 0, len = tableHead.cells.length; i < len; i++) {
        tmpRow.cells[i].innerText = '-';
    }
}


$( document ).ready(function() {
    apiEndpoint = "/api/job?executions=true";
    fetchApiTableData(apiEndpoint, updateApiTableDataJob, true, updateApiTableDataJobPlaceholder);
    setInterval('fetchApiTableData(apiEndpoint, updateApiTableDataJob, true, updateApiTableDataJobPlaceholder)', (DATA_REFRESH_SEC * 1000));
});
