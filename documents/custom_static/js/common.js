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
});
