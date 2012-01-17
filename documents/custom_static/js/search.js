
var selected_index=0;
var cat_height=32;
var last_pressed=null;
var search_delay_constant = 400;

String.prototype.capitalize = function() {
        return this.charAt(0).toUpperCase() + this.slice(1);
}

function append_result(name, description, img, related){
    a = $("#result_template .result_block").clone();
    console.log(name);
    a.find(".result_title").html(name);
    a.find(".result_description").html(description);
    a.find("img").attr("src",img);
    if (related!=""){
        a.find(".result_metadata .related_label").html("Related Classes: ");
        a.find(".result_metadata .result_related").html(related);
    }
    a.appendTo("#result_col");
}

function clear_result_list(){
    $("#result_col div").remove();
}

function exec_search(){
    query = val2($("#top_search_text"));
    category = $("#cat_"+selected_index).html();
    if (query==""){
        $("#search_title").hide();
        $("#no_query_title").show();
    }
    else{
        $("#search_title").show();
        $("#no_query_title").hide();
    }
    $("#cat_title").html(category.capitalize());
    $("#q_title").html(query);
    console.log("" + query + " " + category);
    clear_result_list();
   /* for (i=0; i<5; i++){
        append_result("name", "description", "/static/images/default.jpg","5.333");
    }*/
    $("#result_template .no_results_found").clone().appendTo("#result_col");
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
    exec_search();
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
