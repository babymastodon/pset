
var current_slide=0;
var moving=false;
var counter=0;
var slide_delay=10;

function slide_to(i){
    if (moving==true) return;
    pos=i*$("#slide_container").width()/5;
    $(".dopple.selected").removeClass("selected");
    $("#dopple_"+i).addClass("selected");
    current_slide=i;
    counter=0;
    moving=true;
    $("#slide_container").animate({left:-pos},'slow', function(){
        moving=false;
    });
}

function slide_next(){
    if (counter==slide_delay){
        slide_to((current_slide+1)%5);
        counter=0;
    }
    counter+=1;
    setTimeout(slide_next,1000);
}

function slide_to_dopple(){
    i=parseInt($(this).attr('id').split("_")[1]);
    slide_to(i);
}

$(document).ready(function(){
    $(".dopple").click(slide_to_dopple);
    $("#dopple_"+current_slide).addClass("selected");
    slide_next()
});
