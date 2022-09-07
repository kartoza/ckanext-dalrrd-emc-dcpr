ckan.module("spatial_search", function($){
    return{
        initialize:function(){
            $.proxyAll(this,/_on/);
            console.log("stpail search module initialized:",this.el)
        }
    }
})
