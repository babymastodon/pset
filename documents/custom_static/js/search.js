
var selected_index=0;
var cat_height=32;
var last_pressed=null;
var search_delay_constant = 200;
var lock=false;

var prev_query="";
var prev_category="";
var prev_page="";

var init_query="";
var init_category="";
var init_page="";

var loaded=false;

//creates a new result block from the hidden template and adds it to the bottom of the result column
function append_result(name, description, img, meta, href){
    a = $("#result_template .result_block").clone();
    a.find('a').attr('href',href);
    a.find(".result_title").html(name);
    a.find(".result_description").html(description);
    a.find("img").attr("src",img);
    a.find(".result_metadata").html(meta);
    a.appendTo("#result_col");
}

function manage_nav_events(){
    n = $("#search_prev_page").unbind('click').attr("href","");
    if ($("#page_nums .selected").next().length > 0){
        n.click(function(event){
            event.preventDefault();
            exec_search({page:$("#page_nums .selected").next().html()});
        }).removeClass('hidden');
    }else{
        n.click(function(event){
            event.preventDefault();
        }).addClass('hidden');
    }

    n = $("#search_next_page").unbind('click').attr("href","");
    if ($("#page_nums .selected").prev().length > 0){
        n.click(function(event){
            event.preventDefault();
            exec_search({page:$("#page_nums .selected").prev().html()});
        }).removeClass('hidden');
    }else{
        n.click(function(event){
            event.preventDefault();
        }).addClass('hidden');
    }

    $("#page_nums .page_num").click(function(event){
        event.preventDefault();
        exec_search({page:$(this).html()});
    });
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
    manage_nav_events();
}

function mkstate(query, category, page){
    if ( history.pushState && !nopushstate ){
        history.pushState({q:query,c:category, page:page}, document.title, location.pathname+"?q="+query+"&c="+category+"&page="+page);
    }
}

//ajax search function: clears the list, ajax request, updates the screen, pushes the new state into the browser history (if push_state is true (by default)) it does not move the slider
function exec_search(options){
    options = options || {};
    if (options.category){
        category=options.category;
    }else{
        category = $("#cat_"+selected_index).html();
    }
    nopushstate = options.nopushstate || false;
    query = val2($("#top_search_text"));
    page = parseInt(options.page || $("#page_nums a.selected").html())
        if (page!=prev_page || query!=prev_query || category!=prev_category){
            $.ajax({
                type:'GET',
                url:ajax_url,
                data: {
                    'verb': 'search_page',
                'q':query,
                'c':category,
                'page': page,
                'module': 'search',
                },
                success: function(data){
                             if (data['status']=='success'){
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
            result = data
            mkstate(query, result['category'],result['page']);
            loaded=true;
            //add teh new search results to the page
            reset_pagination(result['pagerange'], result['page']);
            if (parseInt(result['pageresults'])==0){
                $("#result_template .no_results_found").clone().appendTo("#result_col");
            }else{
                for (i=0; i<result['pageresults']; i++){
                    r = result['result_items'][i]
                        append_result(r['title'], r['description'], "/static/images/default.jpg",r['metadata'], r['link']);
                }
            }
            $("#result_num").html(result['totalresults']);
            $("#result_plural").html(result['totalresults']==1 ? '' : 's');
            $("#rmin").html(result['rmin']);
            $("#rmax").html(result['rmax']);
            goto_cat(result['category']);
            prev_query = query;
            prev_category = result['category'];
            prev_page = result['page'];
                             }
                         }
            });
        }
}

//the following two functions will initiate a search when there is a keypress event, and then a short delay of no more keypresses (aka, when the user presumably finishes typing a word or pauses for some other reason)
function check_for_pause_then_search(){
    d =  new Date().getTime();
    delta = d - last_pressed;
    if (delta>search_delay_constant - 30){
        exec_search({page:'1', nopushstate:true});
        last_pressed=d;
    }
}

function search_if_pause(e){
    last_pressed= new Date().getTime();
    setTimeout(check_for_pause_then_search, search_delay_constant);
}

//moves the dynamic slider to the category given by the object
function goto_cat(name){
    new_index = parseInt($('.category_button[name="'+name+'"]').attr('id').split('_')[1]);
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
        exec_search({category:$(this).attr('name'), page:'1'});
    }).parent().removeAttr("href");
}

//jquery snippet to set the selection of a text box
jQuery.fn.setSelection = function(selectionStart, selectionEnd) {
    if(this.lengh == 0) return this;
    input = this[0];

    if (input.createTextRange) {
        var range = input.createTextRange();
        range.collapse(true);
        range.moveEnd('character', selectionEnd);
        range.moveStart('character', selectionStart);
        range.select();
    } else if (input.setSelectionRange) {
        input.focus();
        input.setSelectionRange(selectionStart, selectionEnd);
    }

    return this;
}

$(document).ready(function(){
    ts=$("#top_search_text");
    init_query = val2(ts);
    init_category=$(".selected_cat").attr("name");
    init_page=$("#page_nums .selected").html();
    init_search_slider();
    //these two functions call the ajax search when either the enter button is pressed into the top search box, or when the search button is pressed, or when text is entered into the search box and a there is a short delay of no more input
    $("#top_search_button").bind('click', function(e){
        e.preventDefault();
        exec_search({page:'1'});
    });
    $("#top_search_text").bind('keypress', function(e){
        var code = (e.keyCode ? e.keyCode : e.which);
        if (code==13){
            exec_search({page:'1'});
            e.preventDefault();
        }
    }).bind('textchange', search_if_pause);
    //we don't want the top search box to redirect to a new page when submitted
    $("#top_search_box").bind('submit',function(e){
        return false;
    });
    //This is the function for when the user click the browser's back button
    window.onpopstate = function(e) {
        if (e.state!=null){
            q = e.state.q;
            c = e.state.c;
            p = e.state.page;
        }else{
            q=init_query;
            c=init_category;
            p=init_page;
        }
        init_blank_text_box($("#top_search_text").val(q));
        if (loaded) exec_search({nopushstate:true, category:c, page: p});
    };
    manage_nav_events();
    //set cursor to end of text box
    l=ts.val().length;
    ts.focus().setSelection(l,l);
});
