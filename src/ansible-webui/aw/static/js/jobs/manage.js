function updateApiTableDataJob(row, row2, entry) {
    // job
    row.insertCell(0).innerText = entry.name;
    c2 = row.insertCell(1);
    c2.setAttribute("class", "aw-responsive-lg");
    c2.innerText = entry.inventory_file;
    c3 = row.insertCell(2);
    c3.setAttribute("class", "aw-responsive-lg");
    c3.innerText = entry.playbook_file;

    c4 = row.insertCell(3);
    c4.setAttribute("class", "aw-responsive-lg");
    if (entry.comment == "") {
        c4.innerText = '-';
    } else {
        c4.innerText = entry.comment;
    }
    if (entry.schedule == "") {
        row.insertCell(4).innerText = '-';
    } else {
        scheduleHtml = entry.schedule;
        if (!entry.enabled) {
            scheduleHtml += '<br><i>(disabled)</i>';
        }
        row.insertCell(4).innerHTML = scheduleHtml;
    }

    if (entry.executions.length == 0) {
        lastExecution = null;
        row.insertCell(5).innerText = '-';

        c7 = row.insertCell(6);
        c7.setAttribute("class", "aw-responsive-med");
        c7.innerHTML = '-';
    } else {
        lastExecution = entry.executions[0];
        c6 = row.insertCell(5);
        c6.innerHTML = shortExecutionStatus(lastExecution);

        c7 = row.insertCell(6);
        c7.setAttribute("class", "aw-responsive-med");
        if (entry.next_run == null) {
            c7.innerText = '-';
        } else {
            c7.innerText = entry.next_run;
        }
    }

    actionsTemplate = document.getElementById("aw-api-data-tmpl-actions").innerHTML;
    actionsTemplate = actionsTemplate.replaceAll('${ID}', entry.id);
    if (lastExecution != null) {
        actionsTemplate = actionsTemplate.replaceAll('${EXEC_ID_1}', lastExecution.id);
    }
    row.insertCell(7).innerHTML = actionsTemplate;

    // execution stati
    executionsTemplate = document.getElementById("aw-api-data-tmpl-executions").innerHTML;
    executionsTemplate = executionsTemplate.replaceAll('${ID}', entry.id);
    row2.setAttribute("hidden", "hidden");
    row2.setAttribute("id", "aw-spoiler-" + entry.id);
    row2Col = row2.insertCell(0);
    row2Col.setAttribute("colspan", "100%");
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
    executionsTemplate = executionsTemplate.replaceAll('${EXECS}', execs);
    row2Col.innerHTML = executionsTemplate;
}

function updateApiTableDataJobPlaceholder(dataTable, placeholderId) {
    tableHead = dataTable.rows[0];
    tmpRow = dataTable.insertRow(1);
    tmpRow.setAttribute("aw-api-entry", placeholderId);
    tmpRow.insertCell(0).innerText = '-';
    c2 = tmpRow.insertCell(1);
    c2.innerText = '-';
    c2.setAttribute("class", "aw-responsive-lg");
    c3 = tmpRow.insertCell(2);
    c3.innerText = '-';
    c3.setAttribute("class", "aw-responsive-lg");
    c4 = tmpRow.insertCell(3);
    c4.innerText = '-';
    c4.setAttribute("class", "aw-responsive-lg");
    tmpRow.insertCell(4).innerText = '-';
    c6 = tmpRow.insertCell(5);
    c6.innerText = '-';
    c6.setAttribute("class", "aw-responsive-med");
    tmpRow.insertCell(6).innerText = '-';
}


$( document ).ready(function() {
    apiEndpoint = "/api/job?executions=true";
    fetchApiTableData(apiEndpoint, updateApiTableDataJob, true, updateApiTableDataJobPlaceholder);
    setInterval('fetchApiTableData(apiEndpoint, updateApiTableDataJob, true, updateApiTableDataJobPlaceholder)', (DATA_REFRESH_SEC * 1000));
});
