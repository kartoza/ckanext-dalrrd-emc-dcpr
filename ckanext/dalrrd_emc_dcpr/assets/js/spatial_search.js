ckan.module("spatial_search", function($){
    return{
        initialize:function(){
            let map_container = $("#dataset-map-container")
            let _this = this
            window.addEventListener( "load", ()=>{
                _this.mapper(window.map)
            })
            $.proxyAll(this,/_on/);
        },
        mapper: function(Lmap){
            if(Lmap == undefined){
                this.mapper(window.map)
            }
            else{
                let marker = L.marker([51.5, -0.09])
                let layerGroup1 = L.layerGroup([marker]);
                let overlay = {"Bounds" : layerGroup1}
                let layerControl = L.control.layers(null,overlay)
                layerControl.addTo(Lmap);
            }
            //
        }
    }
})
