

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
    if (ob.val()=="" || ob.val()==ob.attr("title")){
        ob.addClass("blank");
        ob.val(ob.attr("title"));
    }
}

function val2(object){
    if (object.hasClass("label_if_blank") && object.val()==object.attr("title")){
        return "";
    }
    return object.val();
}

$(document).ready(function(){
    $(".label_if_blank").each(addBlankHandlers);
});
