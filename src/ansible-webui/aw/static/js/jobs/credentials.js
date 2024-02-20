function updateApiTableDataCreds(row, entry) {
    row.innerHTML = document.getElementById('aw-api-data-tmpl-row').innerHTML;
    row.cells[0].innerText = entry.name;

    let users = [];
    if (is_set(entry.connect_user)) {
        users.push('<b>Connect User</b>: ' + entry.connect_user);
    }
    if (is_set(entry.become_user)) {
        users.push('<b>Become User</b>: ' + entry.become_user);
    }
    if (users.length == 0) {
        row.cells[1].innerText = '-';
    } else {
        row.cells[1].innerHTML = users.join('<br>');
    }

    let vaults = [];
    if (is_set(entry.vault_file)) {
        vaults.push('<b>Vault-File</b>: ' + entry.vault_file);
    }
    if (is_set(entry.vault_id)) {
        vaults.push(('<b>Vault-ID</b>: ' + entry.vault_id));
    }
    if (vaults.length == 0) {
        row.cells[2].innerText = '-';
    } else {
        row.cells[2].innerHTML = vaults.join('<br>');
    }

    secrets = [];
    if (entry.ssh_key_is_set) {
        secrets.push('<b>SSH private key</b>');
    }
    if (entry.connect_pass_is_set) {
        secrets.push('<b>Connect password</b>');
    }
    if (entry.become_pass_is_set) {
        secrets.push('<b>Become password</b>');
    }
    if (entry.vault_pass_is_set) {
        secrets.push('<b>Vault password</b>');
    }
    if (secrets.length == 0) {
        row.cells[3].innerText = '-';
    } else {
        row.cells[3].innerHTML = secrets.join('<br>');
    }
}

function updateApiTableDataUserCreds(row, entry) {
    updateApiTableDataCreds(row, entry);
    let actionsTemplate = document.getElementById("aw-api-data1-tmpl-actions").innerHTML;
    row.cells[4].innerHTML = actionsTemplate.replaceAll('${ID}', entry.id);
}

function updateApiTableDataGlobalCreds(row, entry) {
    updateApiTableDataCreds(row, entry);
    let actionsTemplate = document.getElementById("aw-api-data2-tmpl-actions").innerHTML;
    row.cells[4].innerHTML = actionsTemplate.replaceAll('${ID}', entry.id);
}

function updateUserCreds() {
    let apiEndpoint = "/api/credentials?global=false";
    let targetTable = "aw-api-data1-table";
    let dataSubkey = "user";
    fetchApiTableData(apiEndpoint, updateApiTableDataUserCreds, false, null, targetTable, dataSubkey);
}

function updateGlobalCreds() {
    let apiEndpoint = "/api/credentials?global=true";
    let targetTable = "aw-api-data2-table";
    let dataSubkey = "shared";
    fetchApiTableData(apiEndpoint, updateApiTableDataGlobalCreds, false, null, targetTable, dataSubkey);
}

$( document ).ready(function() {
    updateGlobalCreds();
    setInterval('updateGlobalCreds()', (DATA_REFRESH_SEC * 1000));

    updateUserCreds();
    setInterval('updateUserCreds()', (DATA_REFRESH_SEC * 1000));
});
