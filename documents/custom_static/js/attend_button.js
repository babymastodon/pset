
function ajax_attending(){
    return function(event){
        $.ajax({
            type: "POST",
        url:ajax_url,
        data:{
            verb: "register",
        pk: pk,
        module: 'party',
        },
        success:function(data){
                    if (data.status=='success'){
                        $("#detail_box_contents .attend_button").hide().unbind('click');
                        $("#detail_box_contentd .attending").show();
                    }
                },
        });
    }
}

function show_attend_button(ob){
}

function show_attend_button_error(ob){
}

function show_attend_button_already_attending(ob){
}

function make_attend_button_error_callback(ob){
    return function(){
        show_attend_button_error(ob);
    };
}

function make_attend_button_callback(ob){
    return function(data){
        if (data.status=="success"){
            if (data.attending){
                show_attend_button_already_attending(ob);
            }else{
                show_attend_button(ob);
            }
        }
        }else{
            show_attend_button_error(ob);
        }
    };
}

function init_one_attend_button(ob){
    ob.removeClass("not_intialized");
    pk = ob.find(".pk").html();
    $.ajax({
        type: "POST",
        url:ajax_url,
        data:{
            verb: "isregistered",
            pk: pk,
            module: 'party',
        },
        success: make_attend_button_callback(ob),
        error: make_attend_button_error_callback(ob),
    });
}

function init_attend_buttons(){
    $(".attend_button.not_initialized").each(init_one_attend_button);
}
