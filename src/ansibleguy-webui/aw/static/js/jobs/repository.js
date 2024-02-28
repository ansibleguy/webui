function updateApiTableDataRepository(row, entry) {
    row.innerHTML = document.getElementById('aw-api-data-tmpl-row').innerHTML;
    row.cells[0].innerText = entry.name;
    row.cells[1].innerText = entry.rtype_name;
    if (entry.rtype_name == "Git") {
        row.cells[2].innerHTML = entry.git_origin + ':' + entry.git_branch;
    } else {
        row.cells[2].innerText = entry.static_path;
    }
    if (entry.rtype_name == "Static") {
        row.cells[3].innerText = '-';
    } else if (is_set(entry.status_name) && !entry.git_isolate) {
        if (is_set(entry.time_update)) {
            row.cells[3].innerHTML += '<b>Updated</b>: ' + entry.time_update + '<br>';
        }
        row.cells[3].innerHTML += '<b>Status</b>: <span class="aw-job-status aw-job-status-' + entry.status_name.toLowerCase() + '">' +
                                   entry.status_name + '</span>';
        let statusTemplate = document.getElementById("aw-api-data-tmpl-status").innerHTML;

        statusTemplate = statusTemplate.replaceAll('${LOG_STDOUT}', entry.log_stdout);
        statusTemplate = statusTemplate.replaceAll('${LOG_STDOUT_URL}', entry.log_stdout_url);

        if (is_set(entry.log_stderr)) {
            statusTemplate = statusTemplate.replaceAll('${LOG_STDERR}', entry.log_stderr);
            statusTemplate = statusTemplate.replaceAll('${LOG_STDERR_URL}', entry.log_stderr_url);
        } else {
            statusTemplate = statusTemplate.replaceAll('${LOG_STDERR}', TITLE_NULL);
            statusTemplate = statusTemplate.replaceAll('${LOG_STDERR_URL}', LINK_NULL);
        }

        row.cells[3].innerHTML += '<br>' + statusTemplate;
    }

    let actionsTemplate = document.getElementById("aw-api-data-tmpl-actions").innerHTML;
    row.cells[4].innerHTML = actionsTemplate.replaceAll('${ID}', entry.id);
}

$( document ).ready(function() {
    apiEndpoint = "/api/repository";
    fetchApiTableData(apiEndpoint, updateApiTableDataRepository);
    setInterval('fetchApiTableData(apiEndpoint, updateApiTableDataRepository)', (DATA_REFRESH_SEC * 1000));
});
