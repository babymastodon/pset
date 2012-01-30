

function toggle_add_drop_buttons(){
    a = $("#follow");
    d = $("#unfollow");
    if (a.is(":visible")){
        a.hide();
        d.show();
    } else {
        a.show();
        d.hide();
    }
}

function follow_unfollow(action){
    return function(){
        $.ajax({
            type: 'POST',
            url: ajax_url,
            data:{
                module:'people',
                verb: action,
                pk: person_pk,
            },
            dataType: 'json',
            success: function(data){
                if (data.status=='success'){
                    toggle_add_drop_buttons();
                }
            },
        });
    };
}


$(document).ready(function(){
    $("#follow").click(follow_unfollow('follow'));
    $("#unfollow").click(follow_unfollow('unfollow'));
});
