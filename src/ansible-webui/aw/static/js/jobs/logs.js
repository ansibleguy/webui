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

$( document ).ready(function() {
    $(".aw-main").on("click", ".aw-log-read", function(){
        let logElement = $(this).attr("aw-log");
        let job_id = $(this).attr("aw-job");
        let exec_id = $(this).attr("aw-exec");
        // let lineStart = $(this).attr("aw-line-start");
        // if(typeof lineStart === "undefined") {
        //     lineStart = 0;
        // }
        let lineStart = 0;
        $.get("/api/job/" + job_id + "/" + exec_id + "/" + lineStart, function( data ) {
          let element = document.getElementById(logElement);
          // todo: change to '+=' once line counter works (add only new lines)
          element.innerHTML = replaceLineColors(data.lines).join('');
          // $(this).attr("aw-line-start", lineStart+data.lines.length);
        });
    });
});
