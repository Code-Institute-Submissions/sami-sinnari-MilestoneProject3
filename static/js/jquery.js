$(document).ready(function(){
    $('.sidenav').sidenav({edge: "left"});
    $('.collapsible').collapsible();
    $('select').formSelect();
    $('.dropdown-trigger').dropdown();
    $('.modal').modal();
    $('#message').val('');
    M.textareaAutoResize($('#message'));
  });