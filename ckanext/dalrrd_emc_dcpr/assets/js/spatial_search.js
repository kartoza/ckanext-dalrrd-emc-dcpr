ckan.module("spatial_search", function($){
    return{
        initialize:function(){
            let _this = this
            console.log($("#dataset-search-form"))
            window.addEventListener( "load", (e)=>setTimeout(_this.mapper(_this),1500))
            $.proxyAll(this,/_on/);
        },
        mapper: function(globalContext){
            let Lmap = window.map
            let _this = globalContext
            if(Lmap == undefined){
                this.mapper()
            }
            else{
                // although promise.all can be used with mulitple fetch
                // requests, the fact it rejects all of fetch requests if
                // one of them is rejected keeps me of using it.
                // at the same time we don't want to sequence these
                let divisions = ["national", "provinces", "district_municipalities", "local_municipalities"]
                let divisions_overlay = {}
                divisions.forEach(division =>{
                    divisions_overlay[division] = L.layerGroup()
                    let division_json = L.geoJson(null,{
                        onEachFeature:function(feature, layer){
                            layer.on({'click':_this._onActivateSearch})
                        }
                    })
                    url = `http://localhost:5000/sa_boundaries/sa_${division}.geojson`
                    fetch(url).then(res=>res.json()).then((data)=>{
                    data.features.forEach(item=>{
                        // this code is compact, went one by one first
                        division_json.addData(item)
                    })
                }).then(divisions_overlay[division].addLayer(division_json))
                })
                // let national_boundaries =  L.geoJson()
                // let provinces = L.geoJson()
                // fetch("http://localhost:5000/sa_boundaries/sa_national.geojson").then(res=>res.json()).then((data)=>{
                //     data.features.forEach(item=>{
                //         national_boundaries.addData(item)
                //     })
                // })
                // fetch("http://localhost:5000/sa_boundaries/sa_provinces.geojson").then(res=>res.json()).then((data)=>{
                //     data.features.forEach(item=>{
                //         provinces.addData(item)
                //     })
                // })

                // let layerGroup1 = L.layerGroup([national_boundaries]);
                // let layerGroup2 = L.layerGroup([provinces]);
                // let overlay = {"Bounds" : layerGroup1, "Provinces":layerGroup2}
                let layerControl = L.control.layers(null,divisions_overlay)
                layerControl.addTo(Lmap);
            }
            //
        },
        _onActivateSearch:function(e){
            let geojson_from_feature = L.geoJson(e.target.feature)
            let bounds = geojson_from_feature.getBounds()
            let bound_str = bounds.toBBoxString()
            $('#ext_bbox').val(bound_str)
            setTimeout(function() {
                map.fitBounds(bounds);
                var form = $("#dataset-search");
                console.log(form)
                form.submit();
              }, 200);
        }
    }
})
