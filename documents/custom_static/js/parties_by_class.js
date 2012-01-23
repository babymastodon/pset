
function prepare_item_list(options){
    class_pk = options['class'] || "0";
    nopushstate = options.nopushstate || false;
    //it just looks better when the button switches over immediately
    $.ajax({
        type: "GET",
        url:ajax_url,
        data: {
            'verb':'parties_by_class',
        'class':class_pk,
        module: 'search',
        },
        success: load_json_parties,
    });
}

$(document).ready(function(){
    //Load the first set of events with ajax (since they are not prerendered by django), nopushstate means we don't want to make another (duplicate) history entry for the first load
    prepare_item_list({class:$("#class_pk").html(), nopushstate:true});
});
