ckan.module("change_save_search_icon", function($){
    /*
        changes the icon of the save search after the user
        clicks on it to save a search.
    */

    let search_icon = $(".save_search_button_icon")
    var previous_query = ""
    var query = undefined
    return{
        initialize:function(){
            $.proxyAll(this,/_on/);
            let _this=  this
            $(".save_search_button").on("click",function(){
                if(previous_query != query){
                search_icon.toggleClass("fa-bookmark-o fa-bookmark");
                _this._onSaveSearch()
            }
            })
        },

        _onSaveSearch:function(){
            if(location.href.includes("?") == false){
                return
            }
            query = location.href.split('?')[1]
            fetch(`${window.location.origin}/saved_searches/save_search`,{method:"POST",
            headers:{'Content-Type': 'application/json'}, body:JSON.stringify(query)})
            .then(res=>res.json())
            .then(data=>console.log(data))
            .catch(err=>console.warn(err))
            previous_query = query
        }

    }
})
