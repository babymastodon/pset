

function toggle_add_drop_buttons(){
    a = $("#add_this_class");
    d = $("#drop_this_class");
    if (a.is(":visible")){
        a.hide();
        d.show();
    } else {
        a.show();
        d.hide();
    }
}

function add_drop(action){
    return function(){
        $.ajax({
            type: 'POST',
            url: ajax_url,
            data:{
                module:'class',
                verb: action,
                pk: class_pk,
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
    map.setZoom(14);
    $("#add_this_class").click(add_drop('add_class'));
    $("#drop_this_class").click(add_drop('drop_class'));
});
