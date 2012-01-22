
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
var loaded = false;

function marker_animate(){
    if (marker_animate_index<num_markers){
        marker = marker_array[marker_animate_index];
        marker.setVisible(true);
        marker.setAnimation(google.maps.Animation.DROP);
        marker_animate_index +=1;
        setTimeout(marker_animate,30);
    }
}

function open_detail_box(callback){
    $("#detail_box").removeClass("closed").animate({width:320, height: 180},'fast',function(callback){
        return function(){
            $("#detail_box").addClass("open");
            if (callback) callback();
        }
    }(callback));
}
function close_detail_box(callback){
    $("#detail_box").removeClass("open").animate({width:16, height: 16},'fast',function(callback){
        return function(){
            $("#detail_box").addClass("closed");
            if (callback) callback();
        }
    }(callback));
}
function toggle_detail_box(){
    if ($("#detail_box").hasClass("closed")) open_detail_box();
    else if ($("#detail_box").hasClass("open")) close_detail_box();
}
function set_detail_box_contents(letter){
    item=item_dict[letter];
    box = $("#detail_box_contents");
    box.find("#building_img").attr('src',item.building_img);
    box.find(".title").html(item.title);
    box.find("#marker_img").attr('src',item.icon);
    box.find(".description").html(item.description);
    box.find(".start_time").html(item.start_time);
    box.find(".end_time").html(item.end_time);
    box.find("location").html(item.location);
    box.find(".bldg_number").html(item.bldg_num);
    box.find(".class_numbers").html(item.class_nums.join(", "));
    box.find(".class_title").html(item.class_title);
    if (item.attending){
        box.find(".attend_button").show().click(ajax_attending(item.pk));
    }else {
        box.find(".attending").show();
    }
}
function on_marker_click(letter){
    return function(event){
        //selects the item in the list amd scrolls to it
        $("#result_list_container .selected").removeClass("selected");
        $("#result_list_container #resultitem_"+letter).addClass("selected");
        new_row = Math.floor((letter.charCodeAt() - 'A'.charCodeAt())/2);
        if (new_row < current_row_index || new_row>current_row_index+2){
            scroll_to(Math.min(new_row, num_rows-3));
        }
        open_detail_box();
        map.panTo(item.coords);
        $("#detail_box_contents").fadeOut('fast',function(l){
            return function(){
                set_detail_box_contents(l);
                $("#detail_box_contents").fadeIn('fast');
            };
        }(letter));
    }
}
function ajax_attending(pk){
    $.ajax({
        type: "POST",
    url:$("#ajax_url").html(),
    data:{
        verb: "register",
    pk: pk,
    },
    success:function(data){
                if (data.status=='success'){
                    $("#detail_box_contents .attend_button").hide().unbind('click');
                    $("#detail_box_contentd .attending").show();
                }
            },
    });
}

function prepare_item_list(options){
    loaded=true;
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
                         item_dict={};
                         $("#result_list_container div").remove();
                         l = data.result_list;
                         num_rows = Math.floor((l.length+1)/2);
                         current_row_index = 0;
                         num_markers=0;
                         for (i in l){
                             item = l[i];
                             moo = $("#templates .result_item").clone(withDataAndEvents=true).appendTo("#result_list_container").click(on_marker_click(item.letter));
                             moo.find(".title").html(item.title);
                             moo.find(".details").attr("href", item.detail_url);
                             moo.find(".location").html(item.location);
                             icon =  marker_url(item.color + "_Marker" + item.letter);
                             item['icon'] = icon;
                             moo.find("img").attr("src",icon);
                             moo.find(".class").html(item.class_nums.join(", "));
                             moo.find(".time").html(item.start_time + " - " + item.end_time);
                             moo.attr("id","resultitem_"+item.letter);
                             loc = new google.maps.LatLng(item.lat, item.lng);
                             m = new google.maps.Marker({
                                 map: map,
                               icon: icon,
                               position: loc,
                               title: item.title,
                               visible: false,
                             });
                             google.maps.event.addListener(m, 'click', on_marker_click(item.letter));
                             marker_array.push(m);
                             num_markers+=1;
                             item['coords'] = loc;
                             item_dict[item.letter]=item;
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

function result_item_clicked(e){
    $(this).addClass("active");
    focus_on_letter($(this).attr('id').split('_')[1]);
}

$(document).ready(function(){
    //The clicking of the buttons in the result_list
    $("#templates .result_item").mousedown(function(){$(this).addClass('active');});
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
            day = e.state.day;
        }else{
            day = init_day;
        }
        if(loaded){
            prepare_item_list({day:day, nopushstate:true});
        }
    };
    $("#detail_box_button").click(toggle_detail_box);
});
