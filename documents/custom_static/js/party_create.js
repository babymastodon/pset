

function set_detail_box_contents(letter){
    item=item_dict[letter];
    box = $("#detail_box_contents");
    box.find("#building_img").attr('src',item.building_img);
    box.find(".title").html(item.title);
    box.find("#marker_img").attr('src',item.icon);
    box.find(".description").html(item.description);
    box.find(".start_time").html(item.start_time);
    box.find(".end_time").html(item.end_time);
    box.find(".location").html(item.location);
    box.find(".bldg_number").html(item.bldg_num);
    box.find(".class_numbers").html(item.class_nums.join(", "));
    box.find(".class_title").html(item.class_title);
    if (!item.attending){
        box.find(".attend_button").show().click(ajax_attending(item.pk));
    }else {
        box.find(".attending").show();
    }
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

$(document).ready(function(){
});
