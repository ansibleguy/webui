function updateApiTableDataKey(row, entry) {
    entryRow.insertCell(0).innerText = entry.token;
    actionsTemplate = document.getElementById("aw-api-data-tmpl-actions").innerHTML;
    entryRow.insertCell(1).innerHTML = actionsTemplate.replaceAll('${TOKEN}', entry.token);
}

$( document ).ready(function() {
    apiEndpoint = "/api/key";
    $(".aw-api-key-add").click(function(){
        $.post(apiEndpoint, function(data, status){
            prompt("Your new API key:\n\nToken: " + data.token + "\nKey:", data.key);
        });
    });
    fetchApiTableData(apiEndpoint, updateApiTableDataKey);
    setInterval('fetchApiTableData(apiEndpoint, updateApiTableDataKey)', (DATA_REFRESH_SEC * 1000));
});
