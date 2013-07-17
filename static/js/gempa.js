var markers = [];

var add_circle_marker = function(latlng, map_obj, pop_data){
    var options = {
      strokeColor: 'red',
      strokeOpacity: 1,
      strokeWeight: 1,
      fillColor: 'red',
      fillOpacity: 0.5,
      map: map_obj,
      center: latlng,
      radius: 30000
    };
    new google.maps.Circle(options);
    var options = {
      strokeColor: 'red',
      strokeOpacity: 1,
      strokeWeight: 1,
      fillColor: 'red',
      fillOpacity: 0,
      map: map_obj,
      center: latlng,
      radius: 60000
    };
    new google.maps.Circle(options);
    var options = {
      strokeColor: 'red',
      strokeOpacity: 1,
      strokeWeight: 1,
      fillColor: 'red',
      fillOpacity: 0,
      map: map_obj,
      center: latlng,
      radius: 90000
    };
    new google.maps.Circle(options);
    var options = {
      strokeColor: 'red',
      strokeOpacity: 1,
      strokeWeight: 1,
      fillColor: 'red',
      fillOpacity: 0,
      map: map_obj,
      center: latlng,
      radius: 120000
    };
    new google.maps.Circle(options);
};


var add_standard_marker = function(map_obj, data, animate){

    var marker = new google.maps.Marker({
      position: new google.maps.LatLng(data.lat, data.lon),
      map: map_obj
    });

    var infowindow = new google.maps.InfoWindow({
      content: data.magnitude+' SR, '+data.region+'<br>Waktu: '+data.time+'<br>Kedalaman : '+data.depth+' KM.'
    });

    google.maps.event.addListener(marker, 'mouseover', function() {
        infowindow.open(map_obj, marker);
    });
    google.maps.event.addListener(marker, 'mouseout', function() {
        infowindow.close(map_obj, marker);
    });

    if(animate != false) marker.setAnimation(google.maps.Animation.BOUNCE);
    
    markers.push(marker);
    marker.setMap(map_obj);
};


var clear_markers = function(){
    if (markers) {
        for (i in markers) {
        markers[i].setMap(null);
        }
        markers.length = 0;
    }
};


jQuery(document).ready(function($){
    google.maps.visualRefresh = true;
    var map;
    var indo_latlng = new google.maps.LatLng(-3.337954,118.300781);
    var mapOptions = {
        zoom: 5,
        minZoom: 3,
        maxZoom: 5,
        center: indo_latlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        disableDefaultUI: true
    };

    map = new google.maps.Map(document.getElementById('map'), mapOptions);

    $('.map-selector a').click(function(){
        $('.map-loading').show();
        $('.map-selector li').removeClass('active');
        $(this).parent().addClass('active');
        map.setZoom($(this).data('zoom'));

        $.ajax({
            type: 'get',
            url: '/api/v1/earthquakes/?source=' + $(this).data('source'),
            dataType: 'json',
            success: function(resp){
                $('.map-loading').hide();
                // clear previous markers 
                clear_markers();
                //Add markers
                $.each(resp, function(index, value){
                    if(index == 0){
                        //Animate latest quake
                        add_standard_marker(map, value, true);
                    }else{
                        add_standard_marker(map, value, false);
                    }
                });
            },
            error: function(){
                $('.map-loading').hide();
                alert('Ups! gagal memproses data gempa.');
            }
        });
    });

    $('li.active a').click();
});