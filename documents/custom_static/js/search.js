
var selected_index=0;
var cat_height=32;
var last_pressed=null;
var search_delay_constant = 400;
var lock=false;

//creates a new result block from the hidden template and adds it to the bottom of the result column
function append_result(name, description, img, meta){
    a = $("#result_template .result_block").clone();
    a.find(".result_title").html(name);
    a.find(".result_description").html(description);
    a.find("img").attr("src",img);
    a.find(".result_metadata").html(meta);
    a.appendTo("#result_col");
}

//anchor click function
function anchor_click(event){
    event.preventDefault();
    $("#page_nums a").removeClass("selected");
    $(this).addClass("selected");
    exec_search();
}

function manage_nav_arrows(){
    $("#search_prev_page").unbind('click').attr("href","").addClass("hidden").click(function(event){event.preventDefault()});
    if ($("#page_nums .selected").next().length > 0){
        $("#search_prev_page").click(function(event){
            $("#page_nums .selected").removeClass("selected").next().addClass("selected");
            exec_search();
        }).removeClass('hidden');
    }
    $("#search_next_page").unbind('click').attr("href","").addClass("hidden").click(function(event){event.preventDefault()});
    if ($("#page_nums .selected").prev().length > 0){
        $("#search_next_page").click(function(event){
            $("#page_nums .selected").removeClass("selected").prev().addClass("selected");
            exec_search();
        }).removeClass('hidden');
    }
}

//resets the pagination based on the give pagelist and pagenumber
function reset_pagination(pagelist, page){
    $("#page_nums a").remove();
    for (i=0; i<pagelist.length; i++){
        p = pagelist[i]
            pg = $("#result_template a.page_num").clone().attr('href',window.location.href + '&page=' + p).html(p).prependTo("#page_nums");
        if (p==page){
            pg.addClass("selected");
        }
    }
    $("#page_nums .page_num").click(anchor_click);
    manage_nav_arrows();
}

//ajax search function: clears the list, ajax request, updates the screen, pushes the new state into the browser history (if push_state is true (by default)) it does not move the slider
function exec_search(options){
    if (options.category){
        goto_cat(options.category);
        category=options.category.html();
        alert('moo');
    }else{
        category = $("#cat_"+selected_index).html();
    }
    push_state = options.push_state || true;
    query = val2($("#top_search_text"));
    $.ajax({
        type:'GET',
        url:$("#ajax_url").html(),
        data: {
            'verb': 'search_page',
        'q':query,
        'c':category,
        'page':parseInt($("#page_nums a.selected").html()),
        },
        success: function(data){
                     //toggle the title of the page depending on whether there is a query
                     if (query==""){
                         $("#search_title").hide();
                         $("#no_query_title").show();
                     }
                     else{
                         $("#search_title").show();
                         $("#no_query_title").hide();
                     }
    $("#cat_title").html(category);
    $("#q_title").html(query);
    //empty out the search results page
    $("#result_col div").remove();
    //push the new page into the history
    if ( history.pushState && push_state ){
        history.pushState({q:query,c:category}, document.title, location.pathname+"?q="+query+"&c="+category);
    }
    //add teh new search results to the page
    result = data['results']
        reset_pagination(result['pagerange'], result['page']);
    if (parseInt(result['pageresults'])==0){
        $("#result_template .no_results_found").clone().appendTo("#result_col");
    }else{
        for (i=0; i<result['pageresults']; i++){
            r = result['result_items'][i]
                append_result(r['title'], r['description'], "/static/images/default.jpg",r['metadata']);
        }
        $("#result_num").html(result['totalresults']);
        $("#result_plural").html(result['totalresults']==1 ? '' : 's');
    }
                 }
    });
}

//the following two functions will initiate a search when there is a keypress event, and then a short delay of no more keypresses (aka, when the user presumably finishes typing a word or pauses for some other reason)
function check_for_pause_then_search(){
    d =  new Date().getTime();
    delta = d - last_pressed;
    if (delta>search_delay_constant - 10){
        exec_search();
        last_pressed=d;
    }
}

function search_if_pause(e){
    last_pressed= new Date().getTime();
    setTimeout(check_for_pause_then_search, search_delay_constant);
}

//moves the dynamic slider to the category given by the object
function goto_cat(new_index){
    new_index = parseInt(ob.attr('id').split('_')[1]);
    if (new_index!=selected_index){
        $("#cat_selector").animate({top:cat_height*new_index}, 'fast');
        selected_index=new_index;
    }
    $(".selected_cat").removeClass("selected_cat");
    $(this).addClass("selected_cat");
}

//removes the selected_fallback classes from the cats, shows the dynamic slider thingy, makes clicking the cat do an ajax update rather than a redirect
function init_search_slider(){
    selected_index = parseInt($(".selected_fallback").removeClass("selected_fallback").attr("id").split('_')[1]);
    $("#cat_selector").show().css("top",cat_height*selected_index);
    $(".category_button").click(function(){
        exec_search({category:$(this)});
    }).parent().removeAttr("href");
}

$(document).ready(function(){
    init_search_slider();
    //these two functions call the ajax search when either the enter button is pressed into the top search box, or when the search button is pressed, or when text is entered into the search box and a there is a short delay of no more input
    $("#top_search_button").bind('click', function(e){
        e.preventDefault();
        exec_search();
    });
    $("#top_search_text").bind('keypress', function(e){
        var code = (e.keyCode ? e.keyCode : e.which);
        if (code==13){
            exec_search();
            e.preventDefault();
        }
        else{
            search_if_pause(e);
        }
    });
    //we don't want the top search box to redirect to a new page when submitted
    $("#top_search_box").bind('submit',function(e){
        return false;
    });
    //This is the function for when the user click the browser's back button
    window.onpopstate = function(e) {
        console.log(e.state);
        init_blank_text_box($("#top_search_text").val(e.state.q));
        exec_search({pushstate:false, category:$('.category_button[name="'+e.state.c+'"]')});
    };
    $("#page_nums .page_num").click(anchor_click);
    manage_nav_arrows();

});
