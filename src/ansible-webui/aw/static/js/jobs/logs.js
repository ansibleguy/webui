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
    fixedLines = [];

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
        $.get("/api/job/" + job_id + "/" + exec_id + "/" + logLineStart, function(data) {
          let element = document.getElementById(logElement);
          element.innerHTML += replaceLineColors(data.lines).join('');
          if (data.lines.length > 0) {
            $this.attr("aw-log-line", parseInt(logLineStart) + data.lines.length);
            logElementEnd.scrollIntoView({ behavior: "smooth", block: "end", inline: "end" });
          }
        });
    };
}

$( document ).ready(function() {
    $(".aw-main").on("click", ".aw-log-read", function(){
        $this = jQuery(this);
        addLogLines($this);
        refreshSec = 1;
        setInterval('addLogLines($this)', (refreshSec * 1000));
    });
});
