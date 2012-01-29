
function init_invite_buttons(){
    $(document).bind('party.registered', function(){
        $(".invite_button").show();
    });
    $(document).bind('party.unregistered', function(){
        $(".invite_button").hide();
    });
}
