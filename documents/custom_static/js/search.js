
var selected_index=0;
var cat_height=32;

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
});
