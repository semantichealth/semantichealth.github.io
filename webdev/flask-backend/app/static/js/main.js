$(function() {
  $('#demo_button').on("click", function() {
    $('#state').val('FL');
    $('#age').val('35');
    $('#zipcode').val('33130');
    $('#health').val('diabetes');
    $('#income').val(28725);
    $('#hhsize').val(1);
  });

  $('#health').attr("autocomplete", "off");
  $.getJSON('/static/data/conditions.json', function(data) {
    $('#health').typeahead({
      source: data
    });
  });

});
