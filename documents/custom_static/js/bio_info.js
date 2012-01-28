$(document).ready(function(){
    $('input[name="department"]').autocomplete({
        source: department_choices,
        delay: 300,
        minLength: 1,
    });
});
