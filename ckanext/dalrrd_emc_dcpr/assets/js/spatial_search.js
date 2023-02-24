ckan.module("spatial_search", function($){
    let divisions_unit = [
        {"unit_name":"sa_national", "number_of_files":1},
        {"unit_name":"sa_provinces", "number_of_files":1},
        {"unit_name":"sa_district_municipalities", "number_of_files":1},
        {"unit_name":"sa_local_municipalities", "number_of_files":1},
    ]
    var division_caps
    var divisionCapsOb = {
        "sa_national":"National", "sa_provinces":"Provinces", "sa_district_municipalities":"District municipalities",
         "sa_local_municipalities":"Local municipalities"
    }
    var divisions_json = {}
    var drawer
    var drawerEnabled = false

    let path = location.pathname;

    return{
        initialize:function(){
            console.log("spatial search loaded!")
            let _this = this
            if(document.readyState == "complete"){_this.mapper(); }
            else{window.addEventListener("load", (e)=>{
                setTimeout(_this.mapper(),1500);
            })}
            $.proxyAll(this,/mapper/);
        },
        mapper: function(){
            var _this = this
            let Lmap
            if(path.includes("dataset/new") || path.includes("dcpr/request/new")){
                Lmap = LeafletMapFromExtentModule
            }
            else{
                Lmap = window.map
            }
            let getDivisionCaps = function(division){
                let _caps = division.charAt(0).toUpperCase() + division.slice(1);
                division_caps = _caps.replace("_", " ")
                return division_caps
            }
            if(Lmap == undefined){
                setTimeout(this.mapper,1500);
            }
            else{
                bound1 = L.latLng(-34.921971, 9.580078)
                bound2 = L.latLng(-21.002471, 37.001953)
                Lmap.setMaxBounds([
                    bound1, bound2
                    ])

                Lmap.options.minZoom = 4;


                Lmap.eachLayer(lyr=>{
                    if( lyr instanceof L.TileLayer ) {
                        lyr.options.noWrap = true
                    }
            })
                let divisions = ["national", "provinces", "district_municipalities", "local_municipalities"]
                let divisions_overlay = {}
                divisions.forEach(division =>{
                    division_caps = getDivisionCaps(division)
                    divisions_overlay[division_caps] = L.layerGroup()
                    let division_json = L.geoJson(null,{
                        style:{

                            "color": "#008000",
                            "weight": 1,
                            "opacity": 0.65

                        },
                        onEachFeature:function(feature, layer){

                            /* for reasons related to browser cache
                               i put this functionality here instead
                               of in it's own function */

                            layer.on({'click':function(e){
                                let geojson_from_feature = L.geoJson(e.target.feature)
                                let bounds = geojson_from_feature.getBounds()
                                let bound_str = bounds.toBBoxString()
                                $('#ext_bbox').val(bound_str)
                                $('#field-spatial').val(bound_str)
                                $('#field-spatial_extent').val(bound_str)
                                if(! location.pathname.includes("dataset/new") && ! path.includes("dcpr/request/new")){setTimeout(function() {
                                    map.fitBounds(bounds);
                                    var form = $(".search-form");
                                    form.submit();
                                  }, 200)};
                                }})
                            }
                        },)

                    let prefixed_json = "sa_" + division
                    divisions_json[prefixed_json] = division_json
                })

                for(let unit of divisions_unit){
                    let urls_list = []
                    let unit_name = unit["unit_name"]
                    let files_number = unit["number_of_files"]
                    for(let i=1;i<=files_number;i++){
                        url = `${location.origin}/sa_boundaries/${unit_name}/${unit_name}${i}.geojson`
                        urls_list.push(url)
                    }
                    Promise.all(urls_list.map(url=>{
                      fetch(url).then(res=> res.json()).then(data=>{
                        data.features.forEach(item=>{
                            divisions_json[unit_name].addData(item)
                        })
                    })
                    })).then(()=>{divisions_overlay[divisionCapsOb[unit_name]].addLayer(divisions_json[unit_name])})
                }

                let layerControl = L.control.layers(divisions_overlay)
                layerControl.addTo(Lmap);
                // handle drawer

                $("a.leaflet-draw-draw-rectangle").attr("title", "search with rectangle bounds")
                // $("a.leaflet-draw-draw-rectangle").on("click", function(e){
                // })



                $("a.leaflet-draw-draw-rectangle").parent().append(
                    $("<a class='leaflet-draw-draw-circle'></a>")
                )

                $("a.leaflet-draw-draw-circle").attr("title", "search with circular buffer")

                $('a.leaflet-draw-draw-circle').hover(function(e){
                    $(this).css({"cursor":"pointer"})
                })

                $('a.leaflet-draw-draw-circle').on('click', function(e){
                    $('body').toggleClass('dataset-map-expanded');
                    Lmap.invalidateSize();
                    if(drawerEnabled == true){
                        drawer.disable()
                        drawerEnabled = false
                    }
                    else{
                        console.log("drawer is enabled now!")
                        drawer = new L.Draw.Circle(Lmap)
                        drawer.enable()
                        drawerEnabled = true
                    }
                });

                  $(".cancel").on("click",function(e){
                      if(drawerEnabled == true){
                        drawer.disable()
                        drawerEnabled = false
                      }
                  })


                  Lmap.on('draw:created', function (e) {
                    console.log(e)
                    layer = e.layer;
                    layer.addTo(Lmap);
                    $('#ext_bbox').val(layer.getBounds().toBBoxString());
                });
            }
        }
    }
})
