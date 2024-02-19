function updateApiTableDataRepository(row, entry) {
    row.innerHTML = document.getElementById('aw-api-data-tmpl-row').innerHTML;
    row.cells[0].innerText = entry.name;
    row.cells[1].innerText = entry.rtype_name;
    if (entry.rtype_name == "Git") {
        row.cells[2].innerText = entry.git_origin + ':' + entry.git_branch;
    } else {
        row.cells[2].innerText = entry.static_path;
    }

    actionsTemplate = document.getElementById("aw-api-data-tmpl-actions").innerHTML;
    row.cells[3].innerHTML = actionsTemplate.replaceAll('${ID}', entry.id);
}

$( document ).ready(function() {
    apiEndpoint = "/api/repository";
    fetchApiTableData(apiEndpoint, updateApiTableDataRepository);
    setInterval('fetchApiTableData(apiEndpoint, updateApiTableDataRepository)', (DATA_REFRESH_SEC * 1000));
});
