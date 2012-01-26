
comments_page = 1;

function load_comments(){
    $.ajax({
        type: "GET",
        url: ajax_url,
        data:{
            verb: 'load',
            module: "comments",
            pk: comments_pk,
            target: comments_target,
            page: comments_page,
        },
        dataType: 'json',
        success: function(data){
            if (data.status=='success'){
                html = data.html.replace("\n","");//check for empty response (only newlines)
                if (html.length>0){
                    $(data.html).hide().appendTo("#comment_feed").fadeIn('slow');
                }
                comments_page+=1;
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
        },
        });
    });
}

function post_error(){
    alert("The server did not accept your comment. Who knows why? Perhaps you should try again.");
}

function post_comment(){
    $.ajax({
        type: "POST",
        url: ajax_url,
        data:{
            verb: 'post',
            module: 'comments',
            target: comments_target,
            pk: comments_pk,
            comment: $("#comment_box").html(),
            },
        dataType: 'json',
        success: function(data){
            if (data.status=='success'){
                $(document).trigger('close.facebox');
                $(data.html).hide().prependTo("#comment_feed").fadeIn('slow');
            } else {
                post_error();
            }
        },
        error: post_error,
    });
}

function init_comments(){
    load_comments();
    $("#moar_comments").click(load_comments);
    $("#post_comment").click(comment_lightbox);
}

