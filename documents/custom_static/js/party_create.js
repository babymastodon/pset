
var marker;

function set_detail_box_contents(item){
    box = $("#detail_box_contents");
    box.find(".building_img").attr('src',item.bldg_img);
    box.find('[name="building_img"]').val(item.bldg_img);
    if (item.bldg_num) l = item.bldg_num + ": " + item.bldg_name;
    else l = item.bldg_name;
    box.find('[name="location"]').val(l);
    box.find('[name="lat"]').val(item.query_loc.lat());
    box.find('[name="lng"]').val(item.query_loc.lng());
}

function location_lookup(loc){
    query_whereis(loc, set_detail_box_contents);
}

function on_get_valid_loc(loc, isvalid){
    if (isvalid){
        marker.setPosition(loc);
        map.panTo(loc);
        location_lookup(loc);
    }
}

function on_marker_drag(event){
    location_lookup(event.latLng);
}

function autocomplete_callback(ob, response_callback){
    $.ajax({
        type: "GET",
        data: {
            module: "search",
            q: ob.term,
            verb: "autocomplete_class",
        },
        url: ajax_url,
        dataType: "json",
        success: function(response_callback){
                     return function(data){
                         if (data.status=="success"){
                            response_callback(data.result)
                         } else {
                             response_callback([]);
                         }
                     };
                 }(response_callback),
        error: function(response_callback){
                   return function(){
                       response_callback([]);
                   }
               }(response_callback),
    });
}

function save_refresh(){
    $('input[name="class-refresh"]').val($('input[name="klass"]').val());
}

$(document).ready(function(){
    r = $('input[name="refresh_token"]');
    if (r.val()=="" && $(".errors").length==0){
      get_current_position(on_get_valid_loc);
      r.val("visited");
    }
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
    class_input = $('input[name="klass"]').autocomplete({
        source: autocomplete_callback,
        autoFocus: true,
        delay: 300,
        minLength: 2,
        close: save_refresh,
    }).bind("textchange",save_refresh).val($('input[name="class-refresh"]').val());
    init_blank_text_box(class_input);
});
