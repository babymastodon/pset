

$(document).ready(function(){
    marker = new google.maps.Marker({
        map: map,
        position: loc,
        clickable: false,
    });
    map.panTo(loc);
});
