
var init_day = "0";
var loaded = false;

function prepare_item_list(options){
    loaded=true;
    day = options['day'] || "0";
    nopushstate = options.nopushstate || false;
    //it just looks better when the button switches over immediately
    $("#date_nav_bar div a").removeClass("selected");
    $("#date_"+day+" a").addClass("selected");
    $.ajax({
        type: "GET",
        url:ajax_url,
        data: {
            'verb':'parties_by_date',
        'day':day,
        module: 'search',
        },
        success: function(day, nopushstate){
                     return function(data){
                         load_json_parties(data);
                         if ( history.pushState && !nopushstate ){
                             history.pushState({day:day}, document.title, location.pathname+"?day="+day);
                         }
                     };
                 }(day, nopushstate),
    });
}

$(document).ready(function(){
    //when the user clicks on a new day, call the ajax function
    $("#date_nav_bar div").click(function(event){
        day = $(this).attr("id").split('_')[1];
        prepare_item_list({day:day});
    });
    //Load the first set of events with ajax (since they are not prerendered by django), nopushstate means we don't want to make another (duplicate) history entry for the first load
    init_day = $("#date_nav_bar .selected").parent().attr("id").split('_')[1];
    prepare_item_list({day:init_day, nopushstate:true});
    //back button functionality
    window.onpopstate = function(e){
        if (e.state!=null){
            day = e.state.day;
        }else{
            day = init_day;
        }
        if(loaded){
            prepare_item_list({day:day, nopushstate:true});
        }
    };
});
