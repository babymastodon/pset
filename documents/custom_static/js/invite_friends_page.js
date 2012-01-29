
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
}

$(document).ready(function(){
    $('input[name="name"]').autocomplete({
        source: autocomplete_callback,
        delay: 300,
        minLength: 2,
        close: update_box,
    });
});
