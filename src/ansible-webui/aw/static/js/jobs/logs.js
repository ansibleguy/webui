const colorMapping = {
    '[0m': '</span>',
    '[0;32m': '<span class="aw-log-ok">',
    '[0;36m': '<span class="aw-log-skip">',
    '[1;35m': '<span class="aw-log-warn">',
    '[0;31m': '<span class="aw-log-err">',
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
}

function replaceAll(str, search, replace) {
    return str.replace(new RegExp(escapeRegExp(search), 'g'), replace);
}

function replaceLineColors(rawLines) {
    var fixedLines = [];

    for (i = 0, len = rawLines.length; i < len; i++) {
        let line = rawLines[i];
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
          let element = document.getElementById(logElement);
          element.innerHTML += replaceLineColors(data.lines).join('');
          if (data.lines.length > 0) {
            $this.attr("aw-log-line", parseInt(logLineStart) + data.lines.length);
            logElementEnd.scrollIntoView({ behavior: "smooth", block: "end", inline: "end" });
          }
        });
    };
}

function updateApiTableDataJobLogs(row, row2, entry) {
    row.insertCell(0).innerHTML = shortExecutionStatus(entry);
    row.insertCell(1).innerText = entry.job_name;
    if (entry.job_comment == "") {
        row.insertCell(2).innerText = "-";
    } else {
        row.insertCell(2).innerText = entry.job_comment;
    }

    let actionsTemplate = document.getElementById("aw-api-data-tmpl-actions").innerHTML;
    actionsTemplate = actionsTemplate.replaceAll('${ID}', entry.id);
    actionsTemplate = actionsTemplate.replaceAll('${JOB_ID}', entry.job);
    row.insertCell(3).innerHTML = actionsTemplate;

    let logsTemplates = document.getElementById("aw-api-data-tmpl-logs").innerHTML;
    logsTemplates = logsTemplates.replaceAll('${ID}', entry.id);
    logsTemplates = logsTemplates.replaceAll('${JOB_ID}', entry.job);
    logsTemplates = logsTemplates.replaceAll('${LOG_STDOUT_URL}', entry.log_stdout_url);
    logsTemplates = logsTemplates.replaceAll('${LOG_STDERR_URL}', entry.log_stderr_url);
    logsTemplates = logsTemplates.replaceAll('${LOG_STDERR}', entry.log_stderr);
    logsTemplates = logsTemplates.replaceAll('${LOG_STDOUT}', entry.log_stdout);
    row2.setAttribute("hidden", "hidden");
    row2.setAttribute("id", "aw-spoiler-" + entry.id);
    let row2Col = row2.insertCell(0);
    row2Col.setAttribute("colspan", "100%");
    row2Col.innerHTML = logsTemplates;
}

$( document ).ready(function() {
    $(".aw-main").on("click", ".aw-log-read", function(){
        $this = jQuery(this);
        addLogLines($this);
        setInterval('addLogLines($this)', (DATA_REFRESH_SEC * 1000));
    });
    apiEndpoint = "/api/job_exec";
    fetchApiTableData(apiEndpoint, updateApiTableDataJobLogs, true);
    setInterval('fetchApiTableData(apiEndpoint, updateApiTableDataJobLogs, true)', (DATA_REFRESH_SEC * 1000));
});
