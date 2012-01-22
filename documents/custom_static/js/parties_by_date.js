
//item list is the data that comes back from the ajax request, dict with letter as index
var item_dict;
var item_height = 84;
var num_rows = 0;
var current_row_index = 0;
var scroll_lock = false;
var init_day = "0";
var marker_array = [];
var marker_animate_index=0;
var num_markers;

function marker_animate(){
    if (marker_animate_index<num_markers){
        marker = marker_array[marker_animate_index];
        marker.setVisible(true);
        marker.setAnimation(google.maps.Animation.DROP);
        marker_animate_index +=1;
        setTimeout(marker_animate,30);
    }
}

function prepare_item_list(options){
    day = options['day'] || "0";
    nopushstate = options.nopushstate || false;
    //it just looks better when the button switches over immediately
    $("#date_nav_bar div a").removeClass("selected");
    $("#date_"+day+" a").addClass("selected");
    $.ajax({
        type: "GET",
        url:$("#ajax_url").html(),
        data: {
            'verb':'parties_by_date',
        'day':day,
        },
        success: function(data){
                     for (a in marker_array){
                         marker_array[a].setMap(null);
                     }
                     marker_array=[];
                     marker_animate_index=0;
                     if (data.status=='success'){
                         $("#result_list_container div").remove();
                         l = data.result_list;
                         num_rows = Math.floor((l.length+1)/2);
                         current_row_index = 0;
                         num_markers=0;
                         for (i in l){
                             item = l[i];
                             moo = $("#templates .result_item").clone(withDataAndEvents=true).appendTo("#result_list_container");
                             moo.find(".title").html(item.title);
                             moo.find(".details").attr("href", item.detail_url);
                             moo.find(".location").html(item.location);
                             icon =  marker_url(item.color + "_Marker" + item.letter);
                             moo.find("img").attr("src",icon);
                             moo.find(".class").html(item.class_nums.join(", "));
                             moo.find(".time").html(item.start_time + " - " + item.end_time);
                             console.log(item.lat + " " + item.lng);
                             loc = new google.maps.LatLng(item.lat, item.lng);
                             m = new google.maps.Marker({
                                 map: map,
                                 icon: icon,
                                 position: loc,
                                 title: item.title,
                                 visible: false,
                             });
                             marker_array.push(m);
                             num_markers+=1;
                         }
                         setTimeout(marker_animate,0);

                         if ( history.pushState && !nopushstate ){
                             history.pushState({day:day}, document.title, location.pathname+"?day="+day);
                         }
                     }
                 },
    });
}

function scroll_to(target_row){
    if (! scroll_lock){
        current_row_index = target_row;
        scroll_lock = true;
        target = target_row*item_height;
        $("#result_list_container").animate({top: -target},'slow',function(){scroll_lock = false;});
    }
}

function scroll_down(){
    scroll_to(Math.min(current_row_index + 3, num_rows-3));
}

function scroll_up(){
    scroll_to(Math.max(current_row_index - 3, 0));
}

var on_get_valid_loc = function(){
    marker = new google.maps.Marker({
        map: map,
           position: my_loc,
           title: "Me",
           draggable: true,
           icon: marker_url('pirates'),
           shadow: marker_url('default_shadow'),
    });
};

function drag_end(e){
    query_whereis(e.latLng);
}

function focus_on_letter(l){
    console.log(l + " " + letter_map[l]);
}

function result_item_clicked(e){
    $(this).addClass("active");
    focus_on_letter($(this).attr('id').split('_')[1]);
}

$(document).ready(function(){
    //The clicking of the buttons in the result_list
    $("#templates .result_item").mousedown(result_item_clicked);
    $(document).mouseup(function(){$("#result_list .result_item").removeClass("active");});
    $(".result_item .details").mousedown(function(event){event.stopPropagation();});
    //Scroll bar buttons
    $("#scroll_down_button").click(scroll_down);
    $("#scroll_up_button").click(scroll_up);
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
            day = e.state.d;
        }else{
            day = init_day;
        }
        if(loaded) prepare_item_list({day:day});
    };
});
