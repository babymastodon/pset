
var max_len = 800;

function load_comments(){
    $.ajax({
        type: "GET",
        url: ajax_url,
        data:{
            verb: 'load',
            module: "comments",
            pk: comments_pk,
            target: comments_target,
            last_id: window.last_comment_id || "",
        },
        dataType: 'json',
        success: function(data){
            if (data.status=='success'){
                html = data.html.replace("\n","");//check for empty response (only newlines)
                if (html.length>0){
                    $(data.html).hide().appendTo("#comment_feed").fadeIn('slow');
                }
                window.last_comment_id = data.last_id;
            }
        },
    });
}

function comment_lightbox(){
    $.facebox(function() {
        $.ajax({
            type: "GET",
            url: ajax_url,
            data:{
                module:'comments',
            verb:'get_box',
            },
            dataType: 'html',
            success: function(data) {
                $.facebox(data);
                $("#post_comment_button").click(post_comment);
                $("#comment_box").bind('textchange', max_chars);
                max_chars();
            },
        });
    });
}

function close_facebox(){
    $(document).trigger('close.facebox');
}

function delete_comment(pk){
    $.facebox(function() {
        $.ajax({
            type: "GET",
            url: ajax_url,
            data:{
                module:'comments',
                verb:'ensure_delete',
            },
            dataType: 'html',
            success: function(pk){
                return function(data) {
                    $.facebox(data);
                    $("#dialog_continue").click(really_delete(pk));
                    $("#dialog_cancel").click(close_facebox);
                };
            }(pk),
        });
    });
}

function really_delete(pk){
    return function(){
        $.ajax({
            type: "POST",
            url: ajax_url,
            data:{
                module:'comments',
                verb:'delete',
                pk:pk,
            },
            dataType: 'json',
            success: function(data) {
                if (data.status=='success'){
                    $("#comment_"+pk).fadeOut('slow', function(){$(this).remove();});
                    close_facebox();
                }
            },
        });
    };
}

function post_error(){
    alert("The server did not respond very well to your request. Who knows why? Perhaps you should try again.");
}

function post_comment(){
    if ($("#comment_box").val().length<=max_len){
        $.ajax({
            type: "POST",
            url: ajax_url,
            data:{
                verb: 'post',
                module: 'comments',
                target: comments_target,
                pk: comments_pk,
                comment: $("#comment_box").val(),
            },
            dataType: 'json',
            success: function(data){
                if (data.status=='success'){
                    close_facebox();
                    $(data.html).hide().prependTo("#comment_feed").fadeIn('slow');
                } else {
                    post_error();
                }
            },
            error: post_error,
        });
    }
}

function max_chars(){
    var len = $("#comment_box").val().length;
    if (len>max_len){
        $("#post_comment_button").addClass("disabled");
    }else{
        $("#post_comment_button").removeClass('disabled');
    }
    $("#post_char_left").html(""+(max_len-len)+"/"+max_len);
};

function init_comments(){
    load_comments();
    $("#moar_comments").click(load_comments);
    $("#post_comment").click(comment_lightbox);
}

