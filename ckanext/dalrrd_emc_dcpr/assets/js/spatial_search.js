ckan.module("spatial_search", function($){
    return{
        initialize:function(){
            let _this = this
            if(document.readyState == "complete"){_this.mapper()}
            else{window.addEventListener( "load", (e)=>setTimeout(_this.mapper(),1500))}
            $.proxyAll(this,/_on/);
        },
        mapper: function(){
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
                    divisions_overlay[division] = L.layerGroup()
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
                }).then(divisions_overlay[division].addLayer(division_json))
                })
                let layerControl = L.control.layers(null,divisions_overlay)
                layerControl.addTo(Lmap);
            }
        },
    }
})
