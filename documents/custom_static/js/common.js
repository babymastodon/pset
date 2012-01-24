$.facebox.settings.closeImage = static_url + 'images/css/closelabel.png'
$.facebox.settings.loadingImage = static_url + 'images/css/loading.gif'

function init_blank_text_box(ob){    
    if (ob.val()=="" || ob.val()==ob.attr("title")){
        ob.addClass("blank");
        ob.val(ob.attr("title"));
    }
}
function addBlankHandlers(){
    ob=$(this);
    ob.focus(function(){
        t= $(this);
        if (t.hasClass("blank")){
            t.val("");
        }
        t.removeClass("blank");
    });
    ob.blur(function(){
        t=$(this);
        if (t.val()==""){
            t.addClass("blank");
            t.val(t.attr("title"));
        }
    });
    init_blank_text_box(ob);
}

function val2(object){
    if (object.hasClass("label_if_blank") && object.val()==object.attr("title")){
        return "";
    }
    return object.val();
}

function submit_top_search_form(){
    b = $("#top_search_text");
    b.val(val2(b));
    $("#top_search_box").submit();
}

function loginPressed(event){
    event.preventDefault();
    if (!$(this).hasClass('selected')){
        $(".dropdown").removeClass("selected");
        $(this).addClass('selected').find(":input").first().focus();
        event.stopPropagation();
    }
}

function closeDropdown(event){
    $(".dropdown").removeClass('selected');
}

function preventDropdownClose(event){
    event.stopPropagation();
}

var meta_pressed=false;

function limit_text(){
    $(this).click(function(event){
        num = parseInt($(this).attr("ref"));
        l = $(this).val().length;
        if (l==num){
            keycode = (event.keyCode ? event.keyCode : event.which);
            if (((keycode >= 48 && keycode <= 90) || (keycode >=107 && keycode <=111) || (keycode>=186 && keycode<=222)) && !meta_pressed){
                event.preventDefault();
                console.log('moo');
            }
        }
    });
    $(this).bind('textchange',function(event){
        l = $(this).val().length;
        if (l>num) $(this).val($(this).val().substring(0,num));
    });
}

function check_meta(event){
    keycode = (event.keyCode ? event.keyCode : event.which);
    if (keycode >=16 && keycode <=18){
        meta_pressed=true;
    } else {
        meta_pressed=false;
    }
}

function undo_meta(event){
    meta_pressed=false;
}

function clean_data(event){
    $('.label_if_blank').each(function(){
        $(this).val(val2($(this)));
    });
}

$(document).ready(function(){
    $(".label_if_blank").each(addBlankHandlers);
    $("#top_search_button").click(submit_top_search_form);
    $("#top_search_text").keypress(function(e){
        var code = (e.keyCode ? e.keyCode : e.which);
        if (code==13){submit_top_search_form}
    });
    $(".dropdown").click(loginPressed);
    $("body").click(closeDropdown);
    $(".dropdown_list").click(preventDropdownClose);
    $(".limit_text").each(limit_text);
    $("body").keydown(check_meta).keyup(undo_meta);
    $("form").submit(clean_data);
});
