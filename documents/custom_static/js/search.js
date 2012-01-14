function fix_list_height(){
    a = $("#category_list_container");
    b=$("#result_list");
    a.height("auto");
    b.height("auto");
    height=Math.max(400, a.height(),b.height());
    a.height(height);
    b.height(height);
}
    

function clear_category_list(){
}

function slide_to_subjects(){
    c = $("#category_list_container").add("#category_head_container");
    if (c.hasClass("shifted")){
        c.animate({left:0},'fast');
    }
}

function slide_to_topics(){
    c = $("#category_list_container").add("#category_head_container");
    if (!c.hasClass("shifted")){
        c.animate({left:-220});
    }
}

function back_button(){
    slide_to_subjects();
}

function subject_handlers(){
    $(this).click(slide_to_topics);
}

function search(){
}

$(document).ready(function(){
    fix_list_height();
    $("#search_button").click(search);
    $("#big_search_bar").keypress(function(event){
        var code = (e.keyCode ? e.keyCode : e.which);
        if (code==13){search()}
    });
    $("#cat_back").click(back_button);
    $("#cat_col div").each(subject_handlers);
});
