// https://docs.djangoproject.com/en/5.0/howto/csrf/#using-csrf-protection-with-ajax

// CONSTANTS
const DATA_REFRESH_SEC = 1;

// UTIL FUNCTIONS
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function sleep(ms = 0) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function updateReloadTime() {
    var element =  document.getElementById("aw-last-update");
    if (typeof(element) != 'undefined' && element != null) {
      element.innerHTML = "Last update: " + (new Date()).toLocaleTimeString({ hour12: false });
    }
}

function reloadPage(ms = 50) {
    sleep(ms);  // wait for data to be processed by backend
    location.reload();
    updateReloadTime();
}

function reloadElement(element) {
    $(element).load(document.URL +  ' ' + element);
    updateReloadTime();
}

function reloadAwData(ms = 50) {
    sleep(ms);  // wait for data to be processed by backend
    reloadElement('.aw-data');
}

function autoReloadPage(sec) {
    setInterval('reloadPage()', (sec * 1000));
}

function autoReloadData(sec) {
    setInterval('reloadAwData()', (sec * 1000));
}

function autoReloadToggle(button) {
  if (button.value == "OFF") {
    button.value = "ON";
    button.classList.add("btn-primary");
    button.classList.remove("btn-secondary");
  } else {
    button.value = "OFF";
    button.classList.remove("btn-primary");
    button.classList.add("btn-secondary");
  }
}

function toggleHidden(elementID) {
    let element = document.getElementById(elementID);
    let hidden = element.getAttribute("hidden");

    if (hidden) {
       element.removeAttribute("hidden");
    } else {
       element.setAttribute("hidden", "hidden");
    }
}

// API CALLS
const CSRF_TOKEN = getCookie('csrftoken');

function apiActionSuccess(result) {
    resultDiv = document.getElementById('aw-api-result');
    if (result.msg) {
        resultDiv.innerHTML = 'Success: ' + result.msg;
    } else {
        resultDiv.innerHTML = 'Success';
    }
    apiActionErrorClear();
    $('html, body').animate({ scrollTop: 0 }, 'fast');
}

function apiActionError(result, exception) {
    console.log(result);
    console.log(exception);

    // write full/verbose error message to hidden iframe (could be full html response) that can be toggled by user
    errorFullIframe = document.getElementById('aw-api-error-full').contentWindow.document;
    errorFullIframe.open();
    errorFullIframe.write('<h1><b>FULL ERROR:</b></h1><br>' + result.responseText);
    errorFullIframe.close();

    // inform user about the error and allow to toggle/show the full/verbose error message
    errorDiv =  document.getElementById('aw-api-error');
    let errorHTML = "Got error: " + result.statusText + ' (' + result.status + ')<br>' +
    '<button class="btn btn-warning aw-btn-action" title="Full error" onclick="apiActionFullError()">Show full error</button><br>';
    errorDiv.innerHTML = errorHTML;

    apiActionSuccessClear();
    $('html, body').animate({ scrollTop: 0 }, 'fast');
}

function apiActionErrorClear() {
    errorFullIframe = document.getElementById('aw-api-error-full').contentWindow.document;
    errorFullIframe.open();
    errorFullIframe.write('');
    errorFullIframe.close();
    document.getElementById('aw-api-error').innerHTML = '';
}

function apiActionSuccessClear() {
     resultDiv =  document.getElementById('aw-api-result').innerHTML = '';
}

function apiActionFullError() {
    toggleHidden("aw-api-error-full");
    document.getElementById("aw-api-error-full").scrollIntoView();
}

function apiBrowseDirUpdateChoices(inputElement, choicesElement, searchType, result) {
    choices = result[searchType];
    inputElement.attr("pattern", '(.*\\/|^)(' + choices.join('|') + ')$');

    let title = "";
    if (choices.length == 0) {
        title += "No available " + searchType + " found."
    } else if (choices.length > 0) {
        title += "You might choose one of the existing " + searchType + ": '" + choices.join(', ') + "'";
    }
    dirs = result['directories'];
    if (searchType != 'directories' && dirs.length > 0) {
        title += " Available directories: '" + dirs.join(', ') + "'";
    }
    inputElement.attr("title", title);

    choicesHtml = "";
    for (i = 0, len = choices.length; i < len; i++) {
        let choice = choices[i];
        choicesHtml += "<li>" + choice + "</li>";
    }
    if (searchType != 'directories') {
        for (i = 0, len = dirs.length; i < len; i++) {
            let dir = dirs[i];
            choicesHtml += '<li><i class="fa fa-folder" aria-hidden="true"></i> ' + dir + "</li>";
        }
    }
    choicesElement.innerHTML = choicesHtml;
}

function apiBrowseDirRemoveChoices(inputElement, choicesElement, searchType, exception) {
    console.log(exception);
    inputElement.attr("pattern", '^\\b$');
    inputElement.attr("title", "You need to choose one of the existing " + searchType);
}

function apiBrowseDir(inputElement, choicesElement, selector, base, searchType) {
    $.ajax({
        url: "/api/fs/browse/" + selector + "?base=" + base,
        type: "GET",
        success: function (result) { apiBrowseDirUpdateChoices(inputElement, choicesElement, searchType, result); },
        error: function (exception) { apiBrowseDirRemoveChoices(inputElement, choicesElement, searchType, exception); },
    });
}

function fetchApiTableData(apiEndpoint, updateFunction) {
    // NOTE: data needs to be list of dict and include an 'id' attribute
    dataTable = document.getElementById("aw-api-data-table");

    $.get(apiEndpoint, function(data) {
        existingEntryIds = [];
        // for each existing entry
        for (i = 0, len = data.length; i < len; i++) {
            let entry = data[i];
            existingEntryIds.push(String(entry.id));
            entryChanged = false;
            entryRow = null;
            lastData = null;
            // check if the entry existed before
            for (i2 = 0, len2 = dataTable.rows.length; i2 < len2; i2++) {
                let existingRow = dataTable.rows[i2];
                let existingRowId = existingRow.getAttribute("aw-api-entry");
                if (String(existingRowId) == String(entry.id)) {
                    entryRow = existingRow;
                    lastData = entryRow.getAttribute("aw-api-last");
                    break
                }
            }
            // if new entry - insert new row
            if (entryRow == null) {
                entryRow = dataTable.insertRow(1);
                entryRow.setAttribute("aw-api-entry", entry.id);
                entryChanged = true;
            }
            // if new entry or data changed - update the row-content
            newData = JSON.stringify(data);
            if (entryChanged || lastData != newData) {
                console.log("Data entry changed:", entry);
                entryRow.innerHTML = "";
                entryRow.setAttribute("aw-api-last", newData);
                updateFunction(entryRow, entry);
            }
        }
        // remove rows of deleted entries
        rowsToDelete = [];
        for (i3 = 0, len3 = dataTable.rows.length; i3 < len3; i3++) {
            let rowIdx = i3;
            let existingRow = dataTable.rows[rowIdx];
            let existingRowId = existingRow.getAttribute("aw-api-entry");
            if (typeof(existingRowId) == 'undefined' || existingRowId == null) {
                continue
            }
            if (!existingEntryIds.includes(String(existingRowId))) {
                rowsToDelete.push(rowIdx);
            }
        }
        for (i4 = 0, len4 = rowsToDelete.length; i4 < len4; i4++) {
            let rowIdx = rowsToDelete[i4];
            console.log("Removing entry row", rowIdx);
            dataTable.deleteRow(rowIdx);
        }
    });
}

// EVENTHANDLER
$( document ).ready(function() {
    // UTIL
    updateReloadTime();
    $(".aw-main").on("click", ".aw-btn-refresh", function(){
        reloadAwData();
    });
    $(".aw-main").on("click", ".aw-btn-autorefresh", function(){
        sleep(50);
        if ($(this).attr("value") == "ON") {
            autoReloadData(2);
        }
    });
    $(".aw-main").on("click", ".aw-btn-expand", function(){
        let spoiler = $(this).attr("aw-expand");
        toggleHidden(spoiler);
    });
    $(".aw-main").on("click", ".aw-btn-collapse", function(){
        let spoiler = $(this).attr("aw-collapse");
        toggleHidden(spoiler);
    });

    // API
    $.ajaxSetup({
        headers: {'X-CSRFToken': CSRF_TOKEN},
    });
    $(".aw-main").on("click", ".aw-api-click", function(){
        let endpoint = $(this).attr("aw-api-endpoint");
        let method = $(this).attr("aw-api-method");

        if (this.hasAttribute("aw-api-item")) {
            let item = $(this).attr("aw-api-item");
            $.ajax({
                url: "/api/" + endpoint + "/" + item,
                type: method,
                success: function (result) { apiActionSuccess(result); },
                error: function (result, exception) { apiActionError(result, exception); },
            });
        } else {
            $.ajax({
                url: "/api/" + endpoint,
                type: method,
                success: function (result) { apiActionSuccess(result); },
                error: function (result, exception) { apiActionError(result, exception); },
            });
        }
    });
    $(".aw-main").on("submit", ".aw-api-form", function(event) {
        event.preventDefault();

        var form = $(this);
        var actionUrl = form.attr('action');
        var method = form.attr('method');
        var refresh = false;

        $.ajax({
            type: method,
            url: actionUrl,
            data: form.serialize(),
            success: function (result) { apiActionSuccess(result); },
            error: function (result, exception) { apiActionError(result, exception); },
        });

        return false;
    });
    $(".aw-main").on("input", ".aw-fs-browse", function(){
        let searchType = $(this).attr("aw-fs-type");
        let apiSelector = $(this).attr("aw-fs-selector");
        let apiChoices = document.getElementById($(this).attr("aw-fs-choices"));

        $(this).attr("value", "");
        let pattern = $(this).attr("pattern");
        if (pattern == ".*") {
            $(this).attr("pattern", '^\\b$');
        }

        if (this.checkValidity() == false) {

            let userInput = $(this).val();
            if (typeof(userInput) == 'undefined' || userInput == null) {
                userInput = "";
            }

            userInputLevels = userInput.split('/');
            userInputLevels.pop();
            apiBase = userInputLevels.join('/');

            apiBrowseDir(jQuery(this), apiChoices, apiSelector, apiBase, searchType);
        } else {
            apiChoices.innerHTML = ""
        }
    });
});
