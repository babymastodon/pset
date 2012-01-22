var map;
var mit_coord =  new google.maps.LatLng(42.35886, -71.09356);
var top_left = new google.maps.LatLng(42.36425, -71.10798);
var bottom_right = new google.maps.LatLng(42.35068, -71.07030);
var my_loc = new google.maps.LatLng(0,0);
var valid_loc = false;

var tmp_loc;

var last_query={};

//function that gets called when the page receives the user information
var on_get_valid_loc = function(){return;};

function init_map(){
    var mapdiv = $("#mapdiv");
    MAP_TYPE_ID = 'MY_MAP_TYPE';

    var stylez = [{
        featureType: "landscape.man_made",
        elementType: "geometry",
        stylers: [
            { hue: "#FFF5D9" },
            { gamma: .6},
            { saturation: 30},
        ]
        },{
        featureType: "landscape.man_made",
        elementType: "labels",
        stylers: [
        ]
        },{
        featureType: "road",
        elementType: "all",
        stylers: [
            { hue: "#DCB6B5" },
            { gamma: 2},
            { saturation: -30 },
        ]
        },{
        featureType: "road",
        elementType: "labels",
        stylers: [
            {saturation: -60},
            {lightness: 60},
        ]
        },{
        featureType: "poi.sports_complex",
        elementType: "geometry",
        stylers: [
            {saturation: 30},
            {lightness: -10},
        ]
        },{
        featureType: "poi",
        elementType: "geometry",
        stylers: [
            {hue: "#40E83A"},
            {lightness: 40},
        ]
        }];
    mapoptions= {
        zoom: 16,
        maxZoom: 18,
        minZoom: 14,
        center:mit_coord,
        mapTypeControl: false,
        mapTypeId: MAP_TYPE_ID,
        overviewMapControl: false,
        backgroundColor: '#FFF5D9',
        streetViewControl: false,
    };
    mapStyle = new google.maps.StyledMapType(stylez, {});
    map = new google.maps.Map(mapdiv.get(0), mapoptions);
    map.mapTypes.set(MAP_TYPE_ID, mapStyle);
}

function showCoords(position) {
    my_loc = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
    console.log("Latitude:" + my_loc.lat() + "\nLongitude:" + my_loc.lng());
    if (in_box(my_loc, top_left, bottom_right)){
        me = new google.maps.Marker({
            map: map,
            position: my_loc,
            title:"My Location",
        });
        valid_loc = true;
        on_get_valid_loc();
    }
}
//Function automatically triggered on error
function showError(error) {
    console.log(error.code);
}

function in_box(coord, tl, br){
    return coord.lat() < tl.lat() && coord.lng() > tl.lng() && coord.lat() > br.lat() && coord.lng() < br.lng();
}

function query_whereis(loc, on_loc_query){
    if (!loc.lat) return false;
    tmp_loc = loc;
    $.ajax({
        type: 'GET',
        url:"http://whereis.mit.edu/search",
        dataType: 'jsonp',
        data: {
            type: 'coord',
            output: 'json',
            q: loc.lng()+','+loc.lat(),
        },
        success: function(data){
            d = data[0];
            last_query={}
            last_query['bldg_img'] = (d.bldgimg) ? d.bldgimg : null;
            last_query['bldg_name'] = d.name;
            last_query['bldg_num'] = d.bldgnum;
            last_query['bldg_loc'] = new google.maps.LatLng(d.lat_wgs84,d.long_wgs84);
            last_query['query_loc'] = tmp_loc;
            if (on_loc_query) on_loc_query();
        }
    });
}

//the click function get an event object with an attr latLng
function add_marker(loc, text, click){
    text = text || "";
    marker = new google.maps.Marker({
        map: map,
        position: loc,
        title: text,
    });
    if (click) google.maps.event.addListener(marker, 'click', click);
}

//add a marker that is draggable
function add_draggable_marker(loc, text, dragend){
    text = text || "";
    marker = new google.maps.Marker({
        map:map,
        position: loc,
        title: text,
        clickable: false,
        draggable: true,
    });
    if (dragend)google.maps.event.addListener(marker, 'dragend', dragend);
    return marker;
}

//adds the static url and other path info to the front of name
function marker_url(name){
    return "http://www.mit.edu/~zdrach/static/marker/"+name+".png";
}

$(document).ready(function(){
    navigator.geolocation.getCurrentPosition(showCoords,showError);
    init_map();
    /*google.maps.event.addListener(map, 'click', function(ob){
        query_whereis(ob.latLng);
    });*/
});
