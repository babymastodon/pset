
var selected_index=0;
var cat_height=32;
var last_pressed=null;
var search_delay_constant = 400;

function exec_search(){
    query = val2($("#top_search_text"));
    category = $("#cat_"+selected_index).html();
    console.log("" + query + " " + category);
}

function check_for_pause_then_search(){
    d =  new Date().getTime();
    delta = d - last_pressed;
    if (delta>search_delay_constant - 10){
        exec_search();
        last_pressed=d;
    }
}

function search_if_pause(e){
    last_pressed= new Date().getTime();
    setTimeout(check_for_pause_then_search, search_delay_constant);
}

function change_cat(){
    new_index = parseInt($(this).attr('id').split('_')[1]);
    if (new_index!=selected_index){
        $("#cat_selector").animate({top:cat_height*new_index}, 'fast');
        selected_index=new_index;
    }
    $(".selected_cat").removeClass("selected_cat");
    $(this).addClass("selected_cat");
}

function init_search_slider(){
    selected_index = parseInt($(".selected_fallback").removeClass("selected_fallback").attr("id").split('_')[1]);
    $("#cat_selector").show().css("top",cat_height*selected_index);
    $(".category_button").click(change_cat).parent().removeAttr("href");
}

$(document).ready(function(){
    init_search_slider();
    $("#top_search_button").bind('click', function(e){
        e.preventDefault();
        exec_search();
    });
    $("#top_search_text").bind('keypress', function(e){
        var code = (e.keyCode ? e.keyCode : e.which);
        if (code==13){
            exec_search();
            e.preventDefault();
        }
        else{
            search_if_pause(e);
        }
    });
    $("#top_search_box").bind('submit',function(e){
        return false;
    });
});
