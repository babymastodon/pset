

function toggle_add_drop_buttons(){
    a = $("#add_this_class");
    d = $("#drop_this_class");
    if (a.is(":visible")){
        a.hide();
        d.show();
    } else {
        a.show();
        d.hide();
    }
}

function add_drop(action){
    return function(){
        $.ajax({
            type: 'POST',
            url: ajax_url,
            data:{
                module:'class',
                verb: action,
                pk: class_pk,
            },
            dataType: 'json',
            success: function(data){
                if (data.status=='success'){
                    toggle_add_drop_buttons();
                }
            },
        });
    };
}


$(document).ready(function(){
    map.setZoom(14);
    for (a in party_list){
        i = party_list[a];
        marker = new google.maps.Marker({
            map: map,
            icon: marker_url(i.color + "_Marker"+i.letter),
            position: new google.maps.LatLng(i.lat, i.lng),
            title: i.class_title,
            shadow: marker_url("default_shadow"),
            clickable: false,
        });
    }
    $("#add_this_class").click(add_drop('add_class'));
    $("#drop_this_class").click(add_drop('drop_class'));
});
