
function show_all_attending(event){
    event.preventDefault();
    $.facebox({ajax:$(this).attr("href")});
}

function init_people_buttons(){
    $("a.show_all").click(show_all_attending);
}
