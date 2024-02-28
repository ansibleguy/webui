const CHOICE_SEPARATOR = ',';
const MULTI_CHOICE_FIELDS = ['id_inventory_file'];

function apiBrowseDirFilteredChoices(choices, userInputCurrent, allowEmpty = false) {
    let choicesFiltered = [];
    for (choice of choices) {
        if (choice.startsWith(userInputCurrent)) {
            choicesFiltered.push(choice);
        }
    }
    choicesFiltered.sort();
    return choicesFiltered;
}

function apiBrowseDirUpdateChoices(inputElement, choicesElement, searchType, userInputCurrent, result, base) {
    let choices = result[searchType];
    let parentID = 'aw-fs-parent="' + $(inputElement).attr("id") + '"'

    if (choices.length == 0) {
        inputElement.attr("title", "No available " + searchType + " found.");
    } else if (choices[0] == '.*') {
        // isolated repository does not exist - cannot validate files
        return
    }

    let fileChoices = apiBrowseDirFilteredChoices(choices, userInputCurrent);
    let dirChoices = apiBrowseDirFilteredChoices(result['directories'], userInputCurrent);

    if (fileChoices.includes(userInputCurrent) || dirChoices.includes(userInputCurrent)) {
        hideChoices();
        return;
    }

    let choicesHtml = "";
    for (choice of fileChoices) {
        let choiceHtml = choice;
        if (is_set(userInputCurrent) && choice.startsWith(userInputCurrent)) {
            choiceHtml = "<b>" + userInputCurrent + "</b>" + choice.replace(userInputCurrent, '');
        }
        let fullChoice = '';
        if (is_set(base)) {
            fullChoice = base + '/' +  choice;
        } else {
            fullChoice = choice;
        }
        choicesHtml += '<li class="aw-fs-choice aw-fs-choice-' + searchType + '"' + parentID + ' aw-fs-value="' + fullChoice + '">' + choiceHtml + "</li>";
    }
    if (searchType != 'directories') {
        for (dir of dirChoices) {
            let choiceHtml = dir;
            if (is_set(userInputCurrent) && dir.startsWith(userInputCurrent)) {
                choiceHtml = "<b>" + userInputCurrent + "</b>" + dir.replace(userInputCurrent, '');
            }
            let fullDir = '';
            if (is_set(base)) {
                fullDir = base + '/' +  dir;
            } else {
                fullDir = dir;
            }
            choicesHtml += '<li class="aw-fs-choice aw-fs-choice-dir" ' + parentID + ' aw-fs-value="' + fullDir + '"><i class="fa fa-folder" aria-hidden="true"></i> ' + choiceHtml + "</li>";
        }
    }
    choicesElement.innerHTML = choicesHtml;
}

function apiBrowseDirRemoveChoices(inputElement, choicesElement, searchType, exception) {
    console.log(exception);
    inputElement.attr("title", "You need to choose one of the existing " + searchType);
}

function apiBrowseDir(inputElement, choicesElement, repository, searchType) {
    if (!is_set(repository)){
        repository = '0';
    }

    let userInput = $(inputElement).val();
    if (typeof(userInput) == 'undefined' || userInput == null) {
        userInput = "";
    }

    let userInputListLast = '';
    let userInputLevels = '';

    if (MULTI_CHOICE_FIELDS.includes($(inputElement).attr("id"))) {
        userInputListLast = userInput.split(CHOICE_SEPARATOR);
        userInputLevels = userInputListLast.pop().split('/');
    } else {
        if (userInput.includes(CHOICE_SEPARATOR)) {
            hideChoices();
            return;
        }
        userInputLevels = userInput.split('/');
    }
    let userInputCurrent = userInputLevels.pop();
    let base = userInputLevels.join('/');

    $.ajax({
        url: "/api/fs/browse/" + repository + "?base=" + base,
        type: "GET",
        success: function (result) { apiBrowseDirUpdateChoices(inputElement, choicesElement, searchType, userInputCurrent, result, base); },
        error: function (exception) { apiBrowseDirRemoveChoices(inputElement, choicesElement, searchType, exception); },
    });
}

function getRepositoryToBrowse() {
    let selectedRepository = document.getElementById('id_repository').value;
    document.getElementById('id_playbook_file').setAttribute("aw-fs-repository", selectedRepository);
    document.getElementById('id_inventory_file').setAttribute("aw-fs-repository", selectedRepository);
}

function updateChoices($this) {
    let searchType = $this.attr("aw-fs-type");
    let repository = $this.attr("aw-fs-repository");
    let apiChoices = document.getElementById($this.attr("aw-fs-choices"));

    apiBrowseDir($this, apiChoices, repository, searchType);
}

function hideChoices() {
    for (browseChoices of document.querySelectorAll('.aw-fs-choices')) {
        browseChoices.setAttribute("hidden", "hidden");
    }
}

$( document ).ready(function() {
    getRepositoryToBrowse();
    setInterval('getRepositoryToBrowse()', (DATA_REFRESH_SEC * 500));

    $(".aw-main").on("input", ".aw-fs-browse", function(){
        document.getElementById($(this).attr("aw-fs-choices")).removeAttribute("hidden");
        updateChoices(jQuery(this));
    });
    $(".aw-main").on("click", ".aw-fs-choice", function(){
        let inputElement = document.getElementById($(this).attr("aw-fs-parent"));
        let choice = $(this).attr("aw-fs-value");
        let currentChoices = inputElement.value.split(CHOICE_SEPARATOR);
        currentChoices.pop();
        currentChoices = currentChoices.join(CHOICE_SEPARATOR);
        if (is_set(currentChoices)) {
            inputElement.value = currentChoices + CHOICE_SEPARATOR + choice;
        } else {
            inputElement.value = choice;
        }
        hideChoices();
    });
    $(".aw-main").on("focusin", ".row", function(){
        for (browseChoices of document.querySelectorAll('.aw-fs-choices')) {
            browseChoices.setAttribute("hidden", "hidden");
        }
    });
    $(".aw-main").on("focusin", ".aw-fs-browse", function(){
        document.getElementById($(this).attr("aw-fs-choices")).removeAttribute("hidden");
        updateChoices(jQuery(this));
    });
});
