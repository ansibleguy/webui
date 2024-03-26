function updateApiTableDataAlerts(row, entry) {
    row.innerHTML = document.getElementById(ELEM_ID_TMPL_ROW).innerHTML;
    row.cells[0].innerText = entry.name;
    row.cells[1].innerText = entry.alert_type_name;
    row.cells[2].innerText = entry.condition_name;
}

function placeholderAlertPlugins(dataTable, placeholderId) {
    let tmpRow = dataTable.insertRow(1);
    tmpRow.setAttribute("aw-api-entry", placeholderId);
    tmplRow = document.getElementById('aw-api-data-tmpl-row2');
    if (is_set(tmplRow)) {
        tmpRow.innerHTML = tmplRow.innerHTML;
    }

    tableHead = dataTable.rows[0];
    for (i = 0, len = tableHead.cells.length; i < len; i++) {
        if (is_set(tmplRow)) {
            tmpRow.cells[i].innerText = '-';
        } else {
            tmpRow.insertCell(i).innerText = '-';
        }
    }
}

function updateApiTableDataUserAlerts(row, entry) {
    updateApiTableDataAlerts(row, entry);
    let actionsTemplate = document.getElementById("aw-api-data1-tmpl-actions").innerHTML;
    row.cells[3].innerHTML = actionsTemplate.replaceAll('${ID}', entry.id);
}

function updateApiTableDataGroupAlerts(row, entry) {
    updateApiTableDataAlerts(row, entry);
    let actionsTemplate = document.getElementById("aw-api-data2-tmpl-actions").innerHTML;
    row.cells[3].innerHTML = actionsTemplate.replaceAll('${ID}', entry.id);
}

function updateApiTableDataGlobalAlerts(row, entry) {
    updateApiTableDataAlerts(row, entry);
    let actionsTemplate = document.getElementById("aw-api-data3-tmpl-actions").innerHTML;
    row.cells[3].innerHTML = actionsTemplate.replaceAll('${ID}', entry.id);
}

function updateApiTableDataAlertPlugins(row, entry) {
    row.innerHTML = document.getElementById('aw-api-data-tmpl-row2').innerHTML;
    row.cells[0].innerText = entry.name;
    row.cells[1].innerText = entry.executable;
    let actionsTemplate = document.getElementById("aw-api-data4-tmpl-actions").innerHTML;
    row.cells[2].innerHTML = actionsTemplate.replaceAll('${ID}', entry.id);
}

function updateUserAlerts() {
    let apiEndpoint = "/api/alert/user";
    let targetTable = "aw-api-data1-table";
    fetchApiTableData(apiEndpoint, updateApiTableDataUserAlerts, false, null, targetTable);
}

function updateGroupAlerts() {
    let apiEndpoint = "/api/alert/group";
    let targetTable = "aw-api-data2-table";
    fetchApiTableData(apiEndpoint, updateApiTableDataGroupAlerts, false, null, targetTable);
}

function updateGlobalAlerts() {
    let apiEndpoint = "/api/alert/global";
    let targetTable = "aw-api-data3-table";
    fetchApiTableData(apiEndpoint, updateApiTableDataGlobalAlerts, false, null, targetTable);
}

function updateAlertPlugins() {
    let apiEndpoint = "/api/alert/plugin";
    let targetTable = "aw-api-data4-table";
    fetchApiTableData(apiEndpoint, updateApiTableDataAlertPlugins, false, placeholderAlertPlugins, targetTable);
}

$( document ).ready(function() {
    updateGlobalAlerts();
    setInterval('updateGlobalAlerts()', (DATA_REFRESH_SEC * 1000));

    updateUserAlerts();
    setInterval('updateUserAlerts()', (DATA_REFRESH_SEC * 1000));

    updateGroupAlerts();
    setInterval('updateGroupAlerts()', (DATA_REFRESH_SEC * 1000));

    updateAlertPlugins();
    setInterval('updateAlertPlugins()', (DATA_REFRESH_SEC * 1000));
});
