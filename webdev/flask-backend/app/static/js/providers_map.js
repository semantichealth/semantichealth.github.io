$(function() {
  var center = window.coordinates.center;
  var provider_array = window.coordinates.provider_array;

  console.log(center);
  console.log(provider_array);

  var mymap = L.map('mapid').setView(center, 12);
  L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
      attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
      maxZoom: 18,
      id: 'mapbox.light',
      accessToken: 'pk.eyJ1Ijoia29ubmlhbWNoYW4iLCJhIjoiY2loZjZ1aDB4MGxxaHR0bHpmMDRrczNubCJ9.42XTV2wAGebwq8n5KvJBxQ'
  }).addTo(mymap);

  var provider_coordinates;
  var provider_name;

  for (var i = 0; i < provider_array.length; i++) {
    provider_name = provider_array[i][0];
    provider_coordinates = provider_array[i][1];
    L.marker(provider_coordinates)
      .addTo(mymap)
      .bindPopup(provider_name)
      .on('mouseover', function (e) {
        this.openPopup();
      })
      .on('mouseout', function (e) {
        this.closePopup();
      });
  }
});
