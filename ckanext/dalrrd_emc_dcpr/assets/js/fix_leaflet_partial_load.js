/*
    it seems leaflet is not loading full tiles on
    stats page, refer to
    https://stackoverflow.com/questions/72990190/leaflet-js-map-not-showing-fully-on-page-load
    https://laracasts.com/index.php/index.php/discuss/channels/code-review/leaflet-js-map-not-showing-fully-on-page-load?page=1&replyId=811318

    we are triggering a resize event on the map to fix this
*/

ckan.module("trigger_resize_window_for_leaflet", function($){
    return{
        initialize:function($){
            document.querySelector("#granularStatsByArea").addEventListener("click", function(){
                window.dispatchEvent(new Event('resize'));
            })

        }
    }
})
