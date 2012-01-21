var map;
var mit_coord =  new google.maps.LatLng(42.35886, -71.09356);


function showCoords(position) {
    console.log("Latitude:" + position.coords.latitude + "\nLongitude:" + position.coords.longitude);
}
//Function automatically triggered on error
function showError(error) {
    console.log(error.code);
}

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
             {gamma: .7},
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

$(document).ready(function(){
    navigator.geolocation.getCurrentPosition(showCoords,showError);
    init_map();
});
