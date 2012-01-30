
var user_meta;
var people_list = {};

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
                            response_callback(data.result);
                            user_meta = {};
                            for (i in data.metadata){
                                d = data.metadata[i];
                                user_meta[d['name']]=d;
                            }
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

function auto_search(){
    s = $('input[name="name"]').autocomplete("search");
}

function on_delete(ob, i){
    return function(){
        ob.fadeOut('slow',function(i){
            return function(){
                $("this").remove();
                delete people_list[i];
                if ($.isEmptyObject(people_list)){
                    $(".submit_button").hide();
                }
            };
        }(i));
    };
}

function add_people_item(name, id, type, img){
    if (! (id in people_list)){
        li = $(".templates .list_item").clone().hide().prependTo("#people_list").fadeIn('slow');
        li.find(".list_text").html(name);
        if (img) li.find(".list_icon").attr("src", img);
        people_list[id] =type;
        li.find(".delete_button").click(on_delete(li, id));
        $(".submit_button").show();
    }
}


function add_to_list(){
    t = $('input[name="name"]');
    if (window.name_type=='list'){
        u = user_meta[t.val()];
        if (u) add_people_item(u.summary, u.pk, 'pk', u.img);
    } else if (window.name_type=="email"){
        u = t.val();
        add_people_item("Email to: " + u, u, 'email');
    }
}


function submit_form(){
    if (!$.isEmptyObject(people_list)){
        p = $('input[name="people_data"]');
        p.val(JSON.stringify(people_list));
        $("#invite_form").submit();
    }
}

$(document).ready(function(){
    $('input[name="name"]').autocomplete({
        source: autocomplete_callback,
        delay: 300,
        minLength: 2,
        select: update_box,
        close: add_to_list,
        autoFocus: true,
    }).bind("textchange",box_changed).click(auto_search).keydown(function(e){
        var code = (e.keyCode ? e.keyCode : e.which);
        if (code==13){
            add_to_list();
        }
    }).focus();
    $("#add_button").click(add_to_list);
    $(".submit_button").click(submit_form);
});
