
function register_success(ob){
    return function(data){
        if (data.status=="success"){
            if (data.registered=='true') show_attend_button_already_attending(ob);
            $.facebox({ ajax: data.link }, 'my_style')
        }
    };
}

function register_error(o){
    alert("Sorry, your registration was unsuccessful. Please try again. If this problem continues, please don't attempt to contact the site administrator. He would rather not waste his time dealing with you.");
}

function ajax_attending(ob){
    return function(event){
        $.ajax({
            type: "POST",
        url:ajax_url,
        data:{
            verb: "register",
        pk: pk,
        module: 'party',
        },
        success:register_success(ob),
        error: register_error,
        });
    }
}

function show_attend_button(ob){
    ob.children().hide();
    ob.children(".attend_button").show().click(ajax_attending(ob));
}

function show_attend_button_error(ob){
    ob.children().hide();
    ob.children(".attend_error").show();
}

function show_attend_button_already_attending(ob){
    ob.children().hide();
    ob.children(".already_attending").show();
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
        }else{
            show_attend_button_error(ob);
        }
    };
}

function init_one_attend_button(){
    ob=$(this);
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
    $(".attend_button_container.not_initialized").each(init_one_attend_button);
}
