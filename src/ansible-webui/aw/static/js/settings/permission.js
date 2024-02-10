function updateApiTableDataPermission(row, entry) {
    row.insertCell(0).innerText = entry.name;
    row.insertCell(1).innerText = entry.permission_name;
    if (entry.jobs_name.length == 0) {
        row.insertCell(2).innerText = '-';
    } else {
        row.insertCell(2).innerText = entry.jobs_name.join(', ');
    }
    if (entry.users_name.length == 0) {
        row.insertCell(3).innerText = '-';
    } else {
        row.insertCell(3).innerText = entry.users_name.join(', ');
    }
    if (entry.groups_name.length == 0) {
        row.insertCell(4).innerText = '-';
    } else {
        row.insertCell(4).innerText = entry.groups_name.join(', ');
    }

    actionsTemplate = document.getElementById("aw-api-data-tmpl-actions").innerHTML;
    row.insertCell(5).innerHTML = actionsTemplate.replaceAll('${ID}', entry.id);
}

$( document ).ready(function() {
    apiEndpoint = "/api/permission";
    fetchApiTableData(apiEndpoint, updateApiTableDataPermission);
    setInterval('fetchApiTableData(apiEndpoint, updateApiTableDataPermission)', (DATA_REFRESH_SEC * 1000));
});
