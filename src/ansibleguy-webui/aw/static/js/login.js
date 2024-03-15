const ELEM_ID_USER = "id_username";
const ELEM_ID_REMEMBER = "aw-login-remember";

function loadUsername() {
    if (localStorage.login_remember == 1) {
        let usernameField = document.getElementById(ELEM_ID_USER);
        if (is_set(localStorage.login_username)) {
            usernameField.value = localStorage.login_username;
        }
    }
}

function saveUserName() {
    if (localStorage.login_remember == 1) {
        let usernameField = document.getElementById(ELEM_ID_USER);
        if (is_set(usernameField.value)) {
            localStorage.login_username = usernameField.value;
        }
    }
}

function forgetUserName() {
    localStorage.login_remember = 0;
    localStorage.login_username = "";
}

function handleRememberUsername(checkbox) {
    if (checkbox.checked == true) {
        localStorage.login_remember = 1;
        saveUserName();
    } else {
        forgetUserName();
   }
}

$( document ).ready(function() {
    $(".aw-login").on("click", "#" + ELEM_ID_REMEMBER, function(){
        saveUserName();
    });
    $(".aw-login").on("click", "#" + ELEM_ID_REMEMBER, function(){
        if (this.checked == true) {
            localStorage.login_remember = 1;
            saveUserName();
        } else {
            forgetUserName();
       }
    });
    $(".aw-login").on("submit", ".aw-login-form", function(){
        saveUserName();
    });
    if (localStorage.login_remember == 1) {
        document.getElementById(ELEM_ID_REMEMBER).setAttribute("checked", "checked");
        loadUsername();
    }
});
