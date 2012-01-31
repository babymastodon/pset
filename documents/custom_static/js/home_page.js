

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
});
