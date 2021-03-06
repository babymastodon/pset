
//item list is the data that comes back from the ajax request, dict with letter as index
var item_dict;
var item_height = 84;
var num_rows = 0;
var current_row_index = 0;
var scroll_lock = false;
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

function string_trim(s, n){
    if (s.length>n+3){
        return s.substring(0,n) + "...";
    }
    return s;
}

function set_detail_box_contents(letter){
    item=item_dict[letter];
    hide_instruction_box();
    box = $("#detail_box_contents");
    box.find(".building_img").attr('src',item.bldg_img);
    box.find(".details").attr("href",item.detail_url);
    box.find(".title").html(item.title).attr("title",item.title);
    box.find(".agenda").html(string_trim(item.agenda, 32)).attr("title",item.agenda);
    box.find(".location").html(item.location);
    box.find(".room").html(item.room);
    $.ajax({
        type: "GET",
        url: ajax_url,
        data:{
            pk:item.pk,
        module:"party",
        verb:"get_attend_button",
        },
        dataType:"html",
        success:function(data){
            $(".attend_button_container_container").html(data);
        },
    });
}
function on_marker_click(letter){
    return function(event){
        //selects the item in the list amd scrolls to it
        $("#result_list_container .selected").removeClass("selected");
        $("#result_list_container #resultitem_"+letter).addClass("selected");
        index = letter.charCodeAt() - 'A'.charCodeAt();
        new_row = Math.floor((index)/2);
        if (new_row < current_row_index || new_row>current_row_index+2){
            scroll_to(Math.min(new_row, num_rows-3));
        }
        open_detail_box();
        map.panTo(item_dict[letter].coords);
        marker_array[index].setAnimation(google.maps.Animation.BOUNCE);
        setTimeout(function(m){return function(){m.setAnimation(null);}}(marker_array[index]), 2200);
        $("#detail_box_contents").fadeOut('fast',function(l){
            return function(){
                set_detail_box_contents(l);
                $("#detail_box_contents").fadeIn('fast');
            };
        }(letter));
    }
}
function load_json_parties(data){
    if (data.status=='success'){
        for (a in marker_array){
            marker_array[a].setMap(null);
        }
        marker_array=[];
        marker_animate_index=0;
        map.panTo(mit_coord);
        close_detail_box();
        item_dict={};
        $("#result_list_container div").remove();
        l = data.result_list;
        num_rows = Math.floor((l.length+1)/2);
        current_row_index = 0;
        num_markers=0;
        for (i in l){
            item = l[i];
            moo = $(".templates .result_item").clone(withDataAndEvents=true).appendTo("#result_list_container").click(on_marker_click(item.letter));
            moo.find(".title").html(item.title);
            icon =  marker_url(item.color + "_Marker" + item.letter);
            item['icon'] = icon;
            moo.find("img").attr("src",icon);
            class_nums = item.class_nums.join(", ");
            moo.find(".class").html(class_nums);
            moo.attr("title",item.class_title + ": " + class_nums);
            moo.find(".time").html(item.start_time + " - " + item.end_time);
            moo.find(".day").html(item.day);
            moo.attr("id","resultitem_"+item.letter);
            loc = new google.maps.LatLng(item.lat, item.lng);
            m = new google.maps.Marker({
                map: map,
              icon: icon,
              position: loc,
              title: item.title,
              shadow: marker_url("default_shadow"),
              visible: false,
            });
            google.maps.event.addListener(m, 'click', on_marker_click(item.letter));
            marker_array.push(m);
            num_markers+=1;
            item['coords'] = loc;
            item_dict[item.letter]=item;
        }
        if (l.length==0){
            $(".templates .empty").clone().appendTo("#result_list_container");
        }
        setTimeout(marker_animate,0);
    }
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
    scroll_to(Math.min(current_row_index + 3, Math.max(num_rows-3,0)));
}

function scroll_up(){
    scroll_to(Math.max(current_row_index - 3, 0));
}

$(document).ready(function(){
    //The clicking of the buttons in the result_list
    $(".templates .result_item").mousedown(function(){$(this).addClass('active');});
    $(document).mouseup(function(){$("#result_list .result_item").removeClass("active");});
    $(".result_item .details").mousedown(function(event){event.stopPropagation();});
    //Scroll bar buttons
    $("#scroll_down_button").click(scroll_down);
    $("#scroll_up_button").click(scroll_up);
});
