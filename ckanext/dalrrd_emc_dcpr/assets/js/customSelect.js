ckan.module("custom_select", function($){
    return{
        initialize:function(){
            $.proxyAll(this,/_on/);
            console.log("custom select loaded !")
        }
    }
})
