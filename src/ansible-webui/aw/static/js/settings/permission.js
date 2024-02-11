function updateApiTableDataPermission(row, entry) {
    row.innerHTML = document.getElementById('aw-api-data-tmpl-row').innerHTML;
    row.cells[0].innerText = entry.name;
    row.cells[1].innerText = entry.permission_name;
    if (entry.jobs_name.length == 0) {
        row.cells[2].innerText = '-';
    } else {
        row.cells[2].innerText = entry.jobs_name.join(', ');
    }
    if (entry.credentials_name.length == 0) {
        row.cells[3].innerText = '-';
    } else {
        row.cells[3].innerText = entry.credentials_name.join(', ');
    }
    if (entry.users_name.length == 0) {
        row.cells[4].innerText = '-';
    } else {
        row.cells[4].innerText = entry.users_name.join(', ');
    }
    if (entry.groups_name.length == 0) {
        row.cells[5].innerText = '-';
    } else {
        row.cells[5].innerText = entry.groups_name.join(', ');
    }

    actionsTemplate = document.getElementById("aw-api-data-tmpl-actions").innerHTML;
    row.cells[6].innerHTML = actionsTemplate.replaceAll('${ID}', entry.id);
}

$( document ).ready(function() {
    apiEndpoint = "/api/permission";
    fetchApiTableData(apiEndpoint, updateApiTableDataPermission);
    setInterval('fetchApiTableData(apiEndpoint, updateApiTableDataPermission)', (DATA_REFRESH_SEC * 1000));
});
