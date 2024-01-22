$( document ).ready(function() {
    $(".aw-api-key-add").click(function(){
        $.post("/api/key", function(data, status){
            prompt("Your new API key:\n\nToken: " + data.token + "\nKey:",data.key);
            reloadAwData();
        });
    });
});