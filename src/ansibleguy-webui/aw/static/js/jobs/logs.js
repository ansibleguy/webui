const colorMapping = {
    '[0m': '</span>',
    '[0;32m': '<span class="aw-log-ok">',
    '[1;32m': '<span class="aw-log-ok">',
    '[0;36m': '<span class="aw-log-skip">',
    '[1;36m': '<span class="aw-log-skip">',
    '[0;35m': '<span class="aw-log-warn">',
    '[1;35m': '<span class="aw-log-warn">',
    '[0;31m': '<span class="aw-log-err">',
    '[1;31m': '<span class="aw-log-err">',
    '[0;33m': '<span class="aw-log-change">',
    '[1;33m': '<span class="aw-log-change">',
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
}

function replaceAll(str, search, replace) {
    return str.replace(new RegExp(escapeRegExp(search), 'g'), replace);
}

function replaceLineColors(rawLines) {
    var fixedLines = [];

    for (line of rawLines) {
        for (let [search, replace] of Object.entries(colorMapping)) {
            line = replaceAll(line, search, replace);
        }
        fixedLines.push(line);
    }

    return fixedLines
}

function addLogLines($this) {
    let logParentElement = $this.attr("aw-expand");
    let logElement = $this.attr("aw-log");
    let logElementEnd = document.getElementById($this.attr("aw-log-end"));
    let job_id = $this.attr("aw-job");
    let exec_id = $this.attr("aw-exec");
    let hidden = document.getElementById(logParentElement).getAttribute("hidden");
    let logLineStart = $this.attr("aw-log-line");
    if(typeof logLineStart === "undefined") {
        logLineStart = 0;
    }
    if (!hidden) {
        $.get("/api/job/" + job_id + "/" + exec_id + "/log/" + logLineStart, function(data) {
          if (data.lines.length > 0) {
            document.getElementById(logElement).innerHTML += replaceLineColors(data.lines).join('');
            $this.attr("aw-log-line", parseInt(logLineStart) + data.lines.length);
            logElementEnd.scrollIntoView({ behavior: "smooth", block: "end", inline: "end" });
          }
        });
    };
}

function updateApiTableDataJobLogs(row, row2, entry) {
    row.innerHTML = document.getElementById(ELEM_ID_TMPL_ROW).innerHTML;
    if (entryIsFiltered(entry.job)) {
        row.setAttribute("hidden", "hidden");
    }

    row.setAttribute("id_job", entry.job);
    row.setAttribute("id_execution", entry.id);
    row2.setAttribute("id_execution", entry.id);

    row.cells[0].innerHTML = shortExecutionStatus(entry);
    row.cells[1].innerText = entry.job_name;
    if (!is_set(entry.time_duration)) {
        row.cells[2].innerText = "-";
    } else {
        row.cells[2].innerText = entry.time_duration;
    }
    if (!is_set(entry.job_comment)) {
        row.cells[3].innerText = "-";
    } else {
        row.cells[3].innerText = entry.job_comment;
    }

    let actionsTemplate = document.getElementById(ELEM_ID_TMPL_ACTIONS).innerHTML;
    actionsTemplate = actionsTemplate.replaceAll('${ID}', entry.id);
    actionsTemplate = actionsTemplate.replaceAll('${JOB_ID}', entry.job);
    row.cells[4].innerHTML = actionsTemplate;

    let logsTemplates = document.getElementById("aw-api-data-tmpl-logs").innerHTML;
    logsTemplates = logsTemplates.replaceAll('${ID}', entry.id);
    logsTemplates = logsTemplates.replaceAll('${JOB_ID}', entry.job);
    if (is_set(entry.log_stdout)) {
        logsTemplates = logsTemplates.replaceAll('${LOG_STDOUT}', entry.log_stdout);
        logsTemplates = logsTemplates.replaceAll('${LOG_STDOUT_URL}', entry.log_stdout_url);
    } else {
        logsTemplates = logsTemplates.replaceAll('${LOG_STDOUT}', TITLE_NULL);
        logsTemplates = logsTemplates.replaceAll('${LOG_STDOUT_URL}', LINK_NULL);
    }
    if (is_set(entry.log_stderr)) {
        logsTemplates = logsTemplates.replaceAll('${LOG_STDERR}', entry.log_stderr);
        logsTemplates = logsTemplates.replaceAll('${LOG_STDERR_URL}', entry.log_stderr_url);
    } else {
        logsTemplates = logsTemplates.replaceAll('${LOG_STDERR}', TITLE_NULL);
        logsTemplates = logsTemplates.replaceAll('${LOG_STDERR_URL}', LINK_NULL);
    }
    if (is_set(entry.log_stdout_repo)) {
        logsTemplates = logsTemplates.replaceAll('${LOG_STDOUT_REPO}', entry.log_stdout_repo);
        logsTemplates = logsTemplates.replaceAll('${LOG_STDOUT_REPO_URL}', entry.log_stdout_repo_url);
    } else {
        logsTemplates = logsTemplates.replaceAll('${LOG_STDOUT_REPO}', TITLE_NULL);
        logsTemplates = logsTemplates.replaceAll('${LOG_STDOUT_REPO_URL}', LINK_NULL);
    }
    if (is_set(entry.log_stderr_repo)) {
        logsTemplates = logsTemplates.replaceAll('${LOG_STDERR_REPO}', entry.log_stderr_repo);
        logsTemplates = logsTemplates.replaceAll('${LOG_STDERR_REPO_URL}', entry.log_stderr_repo_url);
    } else {
        logsTemplates = logsTemplates.replaceAll('${LOG_STDERR_REPO}', TITLE_NULL);
        logsTemplates = logsTemplates.replaceAll('${LOG_STDERR_REPO_URL}', LINK_NULL);
    }
    row2.setAttribute("hidden", "hidden");
    row2.setAttribute("id", "aw-spoiler-" + entry.id);
    let row2Col = row2.insertCell(0);
    row2Col.setAttribute("colspan", "100%");
    row2Col.innerHTML = logsTemplates;
    let logsContainerBegin = document.getElementById("aw-execution-logs-beg-" + entry.id);
    logsContainerBegin.innerHTML = "<b>Start time:</b> " + entry.time_start + '<br>';
    if (entry.command != null) {
        logsContainerBegin.innerHTML += "<b>Running command:</b><br><small>" + entry.command + "</small><br>";
    }
    if (entry.command_repository != null) {
        logsContainerBegin.innerHTML += "<b>Creating/Updating repository:</b><br><small>" + entry.command_repository + "</small><br>";
    }

    let logsContainerMain = document.getElementById("aw-execution-logs-" + entry.id);
    if (entry.error_s != null) {
        logsContainerMain.innerHTML += ('<div class="aw-execution-errors"><h3>Error</h3>' + entry.error_s + '</div>');
        if (entry.error_m != null) {
            logsContainerMain.innerHTML += ('<br><br><div class="aw-execution-errors"><h3>Error full</h3>' + entry.error_m + '</div>');
        }
    }

    if (is_set(entry.time_fin)) {
        let logsContainerEnd = document.getElementById("aw-execution-logs-end-" + entry.id);
        logsContainerEnd.innerHTML = "<br><b>Finish time:</b> " + entry.time_fin + "<br><b>Duration:</b> " + entry.time_duration;
    }
}

$( document ).ready(function() {
    $(".aw-main").on("click", ".aw-log-read", function(){
        $this = jQuery(this);
        addLogLines($this);
        setInterval('addLogLines($this)', (DATA_REFRESH_SEC * 1000));
    });
    executionCount = 20;
    if (HTTP_PARAMS.has('filter')) {
        executionCount = 50;
    }
    apiEndpoint = "/api/job_exec?execution_count=" + executionCount;
    fetchApiTableData(apiEndpoint, updateApiTableDataJobLogs, true, null, null, null, true);
    setInterval('fetchApiTableData(apiEndpoint, updateApiTableDataJobLogs, true, null, null, null, true)', (DATA_REFRESH_SEC * 1000));
});
