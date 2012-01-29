
function autocomplete_callback(ob, response_callback){
    $.ajax({
        type: "GET",
        data: {
            module: "search",
            q: ob.term,
            verb: "autocomplete_person",
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


function update_box(){
    window.name_type="list";
    $("#add_button").removeClass("disabled");
}

function box_changed(){
    s = $('input[name="name"]').val();
    if (s.match(/[^@]+@mit\.edu/)){
        $("#add_button").removeClass("disabled");
        window.name_type="email";
    } else {
        $("#add_button").addClass("disabled");
        window.name_type=undefined;
    }
}

function add_to_list(){
    if (window.name_type){
        alert("moo");
    }
}

$(document).ready(function(){
    $('input[name="name"]').autocomplete({
        source: autocomplete_callback,
        delay: 300,
        minLength: 2,
        select: update_box,
    }).bind("textchange",box_changed);
    $("#add_button").click(add_to_list);
});
