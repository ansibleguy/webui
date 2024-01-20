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

var sleepSetTimeout_ctrl;

function sleep(ms) {
    clearInterval(sleepSetTimeout_ctrl);
    return new Promise(resolve => sleepSetTimeout_ctrl = setTimeout(resolve, ms));
}

function refreshPage(ms = 50) {
    sleep(ms);  // wait for data to be processed by backend
    window.location = window.location;
}

function autoRefreshPage(sec) {
    setTimeout(function(){
        refreshPage();
    }, (sec * 1000));
}

const csrf_token = getCookie('csrftoken');

$( document ).ready(function() {
    $.ajaxSetup({
        headers: {'X-CSRFToken': csrf_token},
    });
    $(".aw-btn-refresh").click(function(){
        refreshPage(0);
    });
    $(".aw-api-add").click(function(){
        let endpoint = $(this).attr("aw-api-endpoint");
        $.post("/api/" + endpoint, function(data, status){
            refreshPage();
        });
    });
    $(".aw-api-del").click(function(){
        let endpoint = $(this).attr("aw-api-endpoint");
        let item = $(this).attr("aw-api-item");
        $.post("/api/" + endpoint + "/" + item, function(data, status){
            refreshPage();
        });
    });
});
