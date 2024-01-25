// https://docs.djangoproject.com/en/5.0/howto/csrf/#using-csrf-protection-with-ajax


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
function apiActionSuccess(result) {
    // todo: fix success message not showing after refresh
    reloadAwData();

    resultDiv =  document.getElementById('aw-api-result');
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
    errorFullIframe =  document.getElementById('aw-api-error-full').contentWindow.document;
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
    errorFullIframe =  document.getElementById('aw-api-error-full').contentWindow.document;
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
}

const csrf_token = getCookie('csrftoken');

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
            console.log("OK");
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
        headers: {'X-CSRFToken': csrf_token},
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
});
