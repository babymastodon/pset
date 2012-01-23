var map;
var mit_coord =  new google.maps.LatLng(42.35886, -71.09356);
var top_left = new google.maps.LatLng(42.36425, -71.10798);
var bottom_right = new google.maps.LatLng(42.35068, -71.07030);

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

function showCoords(callback){
    return function(position){
        my_loc = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
        if (in_box(my_loc, top_left, bottom_right)){
            callback(my_loc, true);
        }else{
            callback(my_loc, false);
        }
    };
}
//Function automatically triggered on error
function showError(error) {
    console.log(error.code);
}

function in_box(coord, tl, br){
    return coord.lat() < tl.lat() && coord.lng() > tl.lng() && coord.lat() > br.lat() && coord.lng() < br.lng();
}

//the callback function will get a dictionary of terms as it's only argument
function query_whereis(callback){
    return function(loc){
        $.ajax({
            type: 'GET',
        url:"http://whereis.mit.edu/search",
        dataType: 'jsonp',
        data: {
            type: 'coord',
        output: 'json',
        q: loc.lng()+','+loc.lat(),
        },
        success: function(loc){
                     return function(data){
                         d = data[0];
                         last_query={}
                         last_query['bldg_img'] = (d.bldgimg) ? d.bldgimg : null;
                         last_query['bldg_name'] = d.name;
                         last_query['bldg_num'] = d.bldgnum;
                         last_query['bldg_loc'] = new google.maps.LatLng(d.lat_wgs84,d.long_wgs84);
                         last_query['query_loc'] = tmp_loc;
                         if (on_loc_query) on_loc_query();
                     };
                 }(loc),
        });
    };
}
//adds the static url and other path info to the front of name
function marker_url(name){
    return "http://www.mit.edu/~zdrach/static/marker/"+name+".png";
}

//the callback function will get 2 arguments: the location, and whether it's valid
function get_current_position(callback){
    navigator.geolocation.getCurrentPosition(showCoords(callback),showError);
}

function open_detail_box(callback){
    d = $("#detail_box_container");
    $("#detail_box").removeClass("closed").animate({width:d.width(), height: d.height()},'fast',function(callback){
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
$(document).ready(function(){
    init_map();
    $("#detail_box_button").click(toggle_detail_box);
    /*google.maps.event.addListener(map, 'click', function(ob){
      query_whereis(ob.latLng);
      });*/
});
