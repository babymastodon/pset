
function show_all_attending(){
    $.facebox(function() {
        $.ajax({
            type: "GET",
            url: ajax_url,
            data:{
                module:'party',
            verb:'all_attendees',
                pk: party_pk,
            },
            dataType: 'html',
            success: function(data) {
                $.facebox(data);
            },
        });
    });
}
    


$(document).ready(function(){
    marker = new google.maps.Marker({
        map: map,
        position: loc,
        clickable: false,
    });
    map.panTo(loc);
    $("#show_all_attending").click(show_all_attending);
});
