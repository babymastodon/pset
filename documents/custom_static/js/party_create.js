
var marker;

function set_detail_box_contents(item){
    box = $("#detail_box_contents");
    box.find(".building_img").attr('src',item.bldg_img);
    box.find('[name="building_img"]').val(item.bldg_img);
    box.find('[name="location"]').val(item.bldg_num + ": " + item.bldg_name);
    box.find('[name="lat"]').val(item.query_loc.lat());
    box.find('[name="lng"]').val(item.query_loc.lng());
}

function location_lookup(loc){
    query_whereis(loc, set_detail_box_contents);
}

function on_get_valid_loc(loc, isvalid){
    if (isvalid){
        location_lookup(loc);
    }
}

function on_marker_drag(event){
    location_lookup(event.latLng);
}

$(document).ready(function(){
    get_current_position(on_get_valid_loc);
    default_lat = $('#detail_box_contents [name="lat"]').val();
    default_lng = $('#detail_box_contents [name="lng"]').val();
    marker = new google.maps.Marker({
        clickable: false,
        draggable: true,
        map: map,
        position: new google.maps.LatLng(default_lat, default_lng),
        title: "Party Location",
    });
    google.maps.event.addListener(marker, 'dragend', on_marker_drag);
    box = $("#detail_box_contents");
    box.find(".building_img").attr('src',box.find('[name="building_img"]').val());
    open_detail_box();
});
