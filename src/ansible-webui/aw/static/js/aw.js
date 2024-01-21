// https://docs.djangoproject.com/en/5.0/howto/csrf/#using-csrf-protection-with-ajax

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

function reloadPage(ms = 50) {
    sleep(ms);  // wait for data to be processed by backend
    location.reload();
}

function reloadElement(element) {
    $(element).load(document.URL +  ' ' + element);
}

function reloadAwData(ms = 50) {
    sleep(ms);  // wait for data to be processed by backend
    reloadElement('.aw-data');
}

function autoReloadPage(sec) {
    setTimeout(function(){
        reloadPage();
    }, (sec * 1000));
}

function autoReloadData(sec) {
    setTimeout(function(){
        reloadAwData();
    }, (sec * 1000));
}


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
    let element = document.getElementById("aw-api-error-full");
    let hidden = element.getAttribute("hidden");

    if (hidden) {
       element.removeAttribute("hidden");
    } else {
       element.setAttribute("hidden", "hidden");
    }
}

const csrf_token = getCookie('csrftoken');

$( document ).ready(function() {
    $.ajaxSetup({
        headers: {'X-CSRFToken': csrf_token},
    });
    $(".aw-main").on("click", ".aw-btn-refresh", function(){
        reloadAwData(0);
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
