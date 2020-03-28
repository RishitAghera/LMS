$(document).ready(function(){
      $("#myInput").autocomplete({
        source: "ajax_calls/search/",
        minLength: 2,
        open: function(){
            setTimeout(function () {
                $('.ui-autocomplete').css('z-index', 99);
            }, 0);
        }
      });

});