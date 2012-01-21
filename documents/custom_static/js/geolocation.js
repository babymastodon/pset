var map;
var mit_coord =  new google.maps.LatLng(42.35886, -71.09356);
var top_left = new google.maps.LatLng(42.36425, -71.10798);
var bottom_right = new google.maps.LatLng(42.35068, -71.07030);
var my_loc = new google.maps.LatLng(0,0);

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
        alert("you are in the box");
        me = new google.maps.Marker({
            map: map,
            position: my_loc,
            title:"My Location",
        });
    }
    else{
        alert("you are not in the box " + my_loc.toString() + " " + top_left.toString() + " " + bottom_right.toString());
    }
}
//Function automatically triggered on error
function showError(error) {
    console.log(error.code);
}

function in_box(coord, tl, br){
    return coord.lat() < tl.lat() && coord.lng() > tl.lng() && coord.lat() > br.lat() && coord.lng() < br.lng();
}

$(document).ready(function(){
    navigator.geolocation.getCurrentPosition(showCoords,showError);
    init_map();
});
