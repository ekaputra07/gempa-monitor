jQuery(document).ready(function($){

    // ----------------- Earth Quake data model -----------------  //
    var EQModel = Backbone.Model.extend({});

    var EQCollection = Backbone.Collection.extend({
        url: '/api/v1/earthquakes/?source=latest60',
        model: EQModel
    });

    var EQItemView = Backbone.View.extend({
        tagName: 'a',
        className: 'eq-item',
        template: _.template('\
            <div class="magnitude"><%= obj.magnitude %></div>\
            <div class="location"><span class="glyphicon glyphicon-map-marker"></span> <%= obj.region %></div>\
            <div class="time"><span class="glyphicon glyphicon-time"></span> <%= obj.time %></div>\
            <div class="depth"><span class="glyphicon glyphicon-resize-vertical"></span>Depth: <%= obj.depth %> KM</div>\
            <div class="clearfix"></div>\
        '),

        initialize: function(){
            this.model.on('change:active', this.setActive, this);
        },

        render: function(){
            this.$el.attr('title', this.model.get('region'));
            this.$el.attr('href', '#eq-'+this.model.get('eqid'));

            this.$el.html(this.template({obj: this.model.toJSON()}));
            return this;
        },

        setActive: function(){
            if(this.model.get('active') == true){
                this.$el.addClass('active');
            }else{
                this.$el.removeClass('active');
            }
        }
    });

    var mapdata = new EQCollection;

    // ----------------- Videos data model -----------------  //


    var VideoModel = Backbone.Model.extend({});

    var VideoCollection = Backbone.Collection.extend({
        url: '/api/v1/quakevideos/',
        model: VideoModel
    });

    var VideoItemView = EQItemView.extend({
        template: _.template('\
            <img src="<%= obj.thumbnail %>"/>\
            <div class="title"><%= obj.title %></div>\
            <div class="clearfix"></div>\
        '),

        render: function(){
            this.$el.attr('title', this.model.get('title'));

            this.$el.html(this.template({obj: this.model.toJSON()}));
            return this;
        },

        events: {
            'click': 'open_player'
        },

        open_player: function(){
            var that = this;
            $.magnificPopup.open({
                items: {
                    src: that.model.get('url')
                },
                    type: 'iframe'
            });
        }
    });

    var videos = new VideoCollection;


    // ----------------- MAin Router -----------------  //

    var MainRouter = Backbone.Router.extend({

        initialize: function(){
            var that = this;

            google.maps.visualRefresh = true;
            this.indo_latlng = new google.maps.LatLng(-1.337954,110.300781);
            var mapOptions = {
                zoom: 5,
                minZoom: 3,
                center: this.indo_latlng,
                mapTypeId: google.maps.MapTypeId.HYBRID,
                mapTypeControlOptions: {
                    position: google.maps.ControlPosition.TOP_CENTER,
                    style: google.maps.MapTypeControlStyle.DEFAULT
                },
                zoomControlOptions: {
                    position: google.maps.ControlPosition.TOP_RIGHT
                },
                panControlOptions: {
                    position: google.maps.ControlPosition.TOP_RIGHT
                }
            };

            this.markers = [];
            this.heatmap = null;
            this.heatmapData = [];
            this.map = new google.maps.Map(document.getElementById('map'), mapOptions);
            this.map.setZoom(5);

            that.show_eq_list();

            $('.list-tab a').click(function(){
                $('.list-tab li').removeClass('active');
                $(this).parent().addClass('active');

                var target = $(this).data('target');
                if(target == 'eqs') that.show_eq_list();
                if(target == 'videos') that.show_video_list();
                if(target == 'bmkg') alert('Not yet implemented.');
            });
        },

        routes: {
            '': 'show_scalemap',
            'scalemap': 'show_scalemap',
            'heatmap': 'show_heatmap',
            'eq-:eqid': 'show_single_eq',
            'about': 'show_about'
        },

        on_loaded_mapdata: function(callback){

            if(mapdata.length > 0){
                callback();
                return;
            }

            mapdata.fetch({
                success: function(col, resp){
                    callback();
                }
            });
        },

        on_loaded_videos: function(callback){
            if(videos.length > 0){
                callback();
                return;
            }

            videos.fetch({
                success: function(col, resp){
                    callback();
                }
            });
        },

        circle_marker: function (magnitude) {
            return {
                path: google.maps.SymbolPath.CIRCLE,
                fillColor: 'red',
                fillOpacity: .5,
                scale: Math.pow(2, magnitude) / Math.PI,
                strokeColor: 'red',
                strokeOpacity: 1,
                strokeWeight: 1
            };
        },

        add_marker: function(model, animate){
            var that = this;

            var marker = new google.maps.Marker({
                position: new google.maps.LatLng(model.get('lat'), model.get('lon')),
                map: this.map,
                icon: this.circle_marker(model.get('magnitude'))
            });

            var infowindow = new google.maps.InfoWindow({
              content: model.get('magnitude')+' SR, '+model.get('region')+'<br>Waktu: '+model.get('time')+'<br>Kedalaman : '+model.get('depth')+' KM.'
            });

            google.maps.event.addListener(marker, 'mouseover', function() {
                infowindow.open(that.map, marker);
            });

            google.maps.event.addListener(marker, 'mouseout', function() {
                infowindow.close(that.map, marker);
            });

            this.markers.push(marker);

            if(animate){
                var marker2 = new google.maps.Marker({
                  position: new google.maps.LatLng(model.get('lat'), model.get('lon')),
                  map: that.map,
                });

                var infowindow2 = new google.maps.InfoWindow({
                  content: 'Latest EQ'
                });

                google.maps.event.addListener(marker2, 'mouseover', function() {
                    infowindow2.open(that.map, marker2);
                });

                google.maps.event.addListener(marker2, 'mouseout', function() {
                    infowindow2.close(that.map, marker2);
                });

                marker2.setAnimation(google.maps.Animation.BOUNCE);
                this.markers.push(marker2);
            }
        },

        clear_markers: function(){
            if (this.markers) {
                for (i in this.markers) {
                    this.markers[i].setMap(null);
                }
                this.markers.length = 0;
            }

            if(this.heatmap){
                this.heatmap.setMap(null);
                this.heatmap = null;
            }
        },

        show_scalemap: function(){
            var that = this;

            this.on_loaded_mapdata(function(){
                that.clear_markers();

                mapdata.each(function(model){
                    that.add_marker(model, false);
                });
            });
        },

        show_heatmap: function(){
            var that = this;
            this.on_loaded_mapdata(function(){
                that.clear_markers();
                if(that.heatmapData.length < 1){
                    mapdata.each(function(model){

                        var latLng = new google.maps.LatLng(model.get('lat'), model.get('lon'));
                        var weightedLoc = {
                            location: latLng,
                            weight: model.get('magnitude')/30
                        };
                        that.heatmapData.push(weightedLoc);
                    });
                }

                that.heatmap = new google.maps.visualization.HeatmapLayer({
                    data: that.heatmapData,
                    dissipating: false,
                    map: that.map
                });
            });
        },

        show_eq_list: function(){
            var that = this;
            this.on_loaded_mapdata(function(){
                $('#sidebar .list').empty();

                mapdata.each(function(model){
                    var eq_item = new EQItemView({model: model});
                    $('#sidebar .list').append(eq_item.render().el);
                });

                // $('#sidebar .list').jScrollPane({
                //     mouseWheelSpeed: 60,
                //     autoReinitialise: true
                // });
            });
        },

        show_video_list: function(){
            var that = this;
            this.on_loaded_videos(function(){
                $('#sidebar .list').empty();

                videos.each(function(model){
                    var video_item = new VideoItemView({model: model});
                    $('#sidebar .list').append(video_item.render().el);
                });
                // $('#sidebar .list').jScrollPane({
                //     mouseWheelSpeed: 60,
                //     autoReinitialise: true
                // });
            });
        },

        show_single_eq: function(eqid){
            var that = this;
            this.on_loaded_mapdata(function(){
                var eq = mapdata.findWhere({eqid: eqid});
                if(eq){
                    // Unset all models to inactive
                    mapdata.each(function(model){
                        model.set({active: false});
                    });
                    // Set only this one
                    eq.set({active: true});
                    var center = new google.maps.LatLng(eq.get('lat'), eq.get('lon'));
                    that.clear_markers();

                    var marker = new google.maps.Marker({
                        position: new google.maps.LatLng(eq.get('lat'), eq.get('lon')),
                        map: that.map,
                        icon: '/static/img/wave.gif',
                        optimized: false
                    });
                    that.markers.push(marker);
                    that.map.panTo(center);
                }
            });
        },

        show_about: function(){

        }

    });


    // Set sidebar area height correctly
    var sh = $(window).height() - 92;
    $('#sidebar .list').css('height', sh);

    $('#sidebar .list').hover(function(){
        $(this).css('overflow', 'auto');
    },function(){
        $(this).css('overflow', 'hidden');
    });

    // Make sure start everything after map data fetching success
    mapdata.fetch({
        success: function(col, resp){
            app = new MainRouter();
            Backbone.history.start();
        }
    });

});
