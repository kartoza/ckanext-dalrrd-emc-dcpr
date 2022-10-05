ckan.module("spatial_search", function($){
    return{
        initialize:function(){
            let _this = this
            if(document.readyState == "complete"){_this.mapper()}
            else{window.addEventListener( "load", (e)=>setTimeout(_this.mapper(),1500))}
            $.proxyAll(this,/_on/);
        },
        mapper: function(){
            var _this = this
            let Lmap = window.map
            if(Lmap == undefined){
                setTimeout(this.mapper,1500)
            }
            else{
                /* although promise.all can be used with mulitple fetch
                   requests, the fact it rejects all of fetch requests if
                   one of them is rejected keeps me of using it.
                   at the same time we don't want to sequence these */

                let divisions = ["national", "provinces", "district_municipalities", "local_municipalities"]
                let divisions_overlay = {}
                divisions.forEach(division =>{
                    let _caps = division.charAt(0).toUpperCase() + division.slice(1);
                    var division_caps = _caps.replace("_", " ")
                    divisions_overlay[division_caps] = L.layerGroup()
                    let division_json = L.geoJson(null,{
                        onEachFeature:function(feature, layer){

                            /* for reasons related to browser cache
                               i put this functionality here instead
                               of in it's own function */

                            layer.on({'click':function(e){
                                let geojson_from_feature = L.geoJson(e.target.feature)
                                let bounds = geojson_from_feature.getBounds()
                                let bound_str = bounds.toBBoxString()
                                $('#ext_bbox').val(bound_str)
                                setTimeout(function() {
                                    map.fitBounds(bounds);
                                    var form = $(".search-form");
                                    form.submit();
                                  }, 200);
                            }})
                        }
                    })
                    url = `${location.origin}/sa_boundaries/sa_${division}.geojson`
                    fetch(url).then(res=>res.json()).then((data)=>{
                    data.features.forEach(item=>{
                        division_json.addData(item)
                    })
                }).then(divisions_overlay[division_caps].addLayer(division_json))
                })
                let layerControl = L.control.layers(null,divisions_overlay)
                layerControl.addTo(Lmap);
                // adding circle to leaflet draw
                $("a.leaflet-draw-draw-rectangle").parent().append(
                    $("<a class='leaflet-draw-draw-circle'></a>")
                )

                $('a.leaflet-draw-draw-circle').hover(function(e){
                    $(this).css({"cursor":"pointer"})
                })

                $('a.leaflet-draw-draw-circle').on('click', function(e){
                    // if($('body').hasClass('dataset-map-expanded')){
                    //     $('body').removeClass('dataset-map-expanded');
                    // }
                    // else{
                    //     $('body').addClass('dataset-map-expanded');
                    // }
                    $('body').toggleClass('dataset-map-expanded');
                    let drawer = new L.Draw.Circle(Lmap)
                    drawer.enable()
                  });

                  Lmap.on('draw:created', function (e) {
                    layer = e.layer;
                    layer.addTo(Lmap);
                    $('#ext_bbox').val(layer.getBounds().toBBoxString());
                });
            }
        },
        captializeFirstLetter: function(name){
            return
        },

    }
})
