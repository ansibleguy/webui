// https://docs.djangoproject.com/en/5.0/howto/csrf/#using-csrf-protection-with-ajax

// CONSTANTS
const DATA_REFRESH_SEC = 1;
const HTTP_PARAMS = new URLSearchParams(window.location.search);

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

function is_set(data) {
    if (typeof(data) != 'undefined' && data != null && data != "") {
        return true;
    }
    return false;
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

function shortExecutionStatus(execution) {
    return execution.time_start + '<br>' + execution.user_name +
           '<br><div class="aw-job-status aw-job-status-' + execution.status_name.toLowerCase() + '">' +
           execution.status_name + '</div>';
}

// source: https://stackoverflow.com/questions/7616461/generate-a-hash-from-string-in-javascript
function hashString(data) {
    var hash = 0,
        i, chr;
    if (data.length === 0) return hash;
    for (i = 0; i < data.length; i++) {
        chr = data.charCodeAt(i);
        hash = ((hash << 5) - hash) + chr;
        hash |= 0; // Convert to 32bit integer
    }
    return hash;
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
    let errorHTML = "Got error: " + result.statusText + ' (' + result.status + ')';
    if (is_set(result.responseJSON.msg)) {
        errorHTML += ' - ' + result.responseJSON.msg;
    } else {
        errorHTML += '<br><button class="btn btn-warning aw-btn-action" title="Full error" onclick="apiActionFullError()">Show full error</button><br>';
    }
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
    for (choice of choices) {
        choicesHtml += "<li>" + choice + "</li>";
    }
    if (searchType != 'directories') {
        for (dir of dirs) {
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

function fetchApiTableDataPlaceholder(dataTable, placeholderId) {
    tmpRow = dataTable.insertRow(1);
    tmpRow.setAttribute("aw-api-entry", placeholderId);
    tmplRow = document.getElementById('aw-api-data-tmpl-row');
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

// for example with second (hidden) child-row - see: 'job-manage'
// for example with two tables - see: 'job-credentials'
function fetchApiTableData(apiEndpoint, updateFunction, secondRow = false, placeholderFunction = null, targetTable = null, dataSubKey = null, reverseData = false) {
    // NOTE: data needs to be list of dict and include an 'id' attribute
    if (targetTable == null) {
        targetTable = "aw-api-data-table";
    }
    let dataTable = document.getElementById(targetTable);
    let secondRowAppendix = '_2';
    let placeholderExists = false;
    let placeholderId = 'placeholder';

    $.get(apiEndpoint, function(data) {
        if (dataSubKey != null) {
            var data = data[dataSubKey];
        }
        if (reverseData) {
            var data = data.reverse();
        }
        existingEntryIds = [];
        // for each existing entry
        for (entry of data) {
            let entryId = String(entry.id);
            let entryId2 = String(entry.id) + secondRowAppendix;
            if (dataSubKey != null) {
                entryId += dataSubKey;
                entryId2 += dataSubKey;
            }
            existingEntryIds.push(entryId);
            if (secondRow) {
                existingEntryIds.push(entryId2);
            }
            let entryChanged = false;
            let entryRow = null;
            let entryRow2 = null;
            let lastDataHash = null;
            // check if the entry existed before
            for (existingRow of dataTable.rows) {
                let existingRowId = existingRow.getAttribute("aw-api-entry");
                if (String(existingRowId) == entryId) {
                    entryRow = existingRow;
                    lastDataHash = entryRow.getAttribute("aw-api-last");
                }
                if (String(existingRowId) == entryId2) {
                    entryRow2 = existingRow;
                }
                if (entryRow != null && !secondRow) {break}
                if (entryRow != null && entryRow2 != null) {break}
            }
            // if new entry - insert new row
            if (entryRow == null) {
                if (secondRow && entryRow2 == null) {
                    entryRow2 = dataTable.insertRow(1);
                    entryRow2.setAttribute("aw-api-entry", entryId2);
                }
                entryRow = dataTable.insertRow(1);
                entryRow.setAttribute("aw-api-entry", entryId);
                entryChanged = true;
            }
            // if new entry or data changed - update the row-content
            newDataHash = hashString(JSON.stringify(entry));
            if (entryChanged || lastDataHash != newDataHash) {
                console.log("Data entry changed:", entry);
                entryRow.innerHTML = "";
                entryRow.setAttribute("aw-api-last", newDataHash);
                if (secondRow) {
                    entryRow2.innerHTML = "";
                    updateFunction(entryRow, entryRow2, entry);
                } else {
                    updateFunction(entryRow, entry);
                }
            }
        }
        // remove rows of deleted entries
        let rowsToDelete = [];
        for (rowIdx = 0, rowCnt = dataTable.rows.length; rowIdx < rowCnt; rowIdx++) {
            let existingRow = dataTable.rows[rowIdx];
            let existingRowId = existingRow.getAttribute("aw-api-entry");
            if (typeof(existingRowId) == 'undefined' || existingRowId == null) {
                continue
            }
            if (existingRowId == placeholderId) {
                placeholderExists = true;
                if (data.length > 0) {
                    rowsToDelete.push(rowIdx);
                }
            } else if (!existingEntryIds.includes(String(existingRowId))) {
                rowsToDelete.push(rowIdx);
            }
        }
        for (rowIdx of rowsToDelete) {
            console.log("Removing entry row", rowIdx);
            dataTable.deleteRow(rowIdx);
        }
        // add placeholder row if empty
        if (data.length == 0 && !placeholderExists) {
            if (placeholderFunction == null) {
                fetchApiTableDataPlaceholder(dataTable, placeholderId);
            } else {
                placeholderFunction(dataTable, placeholderId);
            }
        }
    });
    updateReloadTime();
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
