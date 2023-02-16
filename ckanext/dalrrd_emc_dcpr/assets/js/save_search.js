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
            let _this=  this;
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
            .catch(err=>console.warn(err))
            previous_query = query
        }

    }
})


ckan.module("implement_saved_search", function($){
    // applies a saved search
    return{
        initialize:function(){
            $(".saved-search-card").each(function(i,el){
                el.querySelector(".apply-saved-search").addEventListener("click", function(e){
                    let query_str = el.querySelector("#saved_search_query").innerText
                    window.location.href = location.origin + "/dataset/?" + query_str
                })

            })
        }
    }

})

ckan.module("delete_saved_search", function($){
    return{
        initialize:function(){
            $.proxyAll(this,/_on/);
            this.el.on("click", this._onClick)
        },

        _onClick:function($){
            let saved_search_id = this.el.data("search_id")
            let url = `${location.origin}/saved_searches/delete_saved_search`
            let _this = this
            fetch(url, {method:"POST", headers:{'Content-Type': 'application/json'}, body:JSON.stringify({saved_search_id})})
            .then(res=>res.json())
            .then((data)=>{
                _this.el.parent().parent().remove()
                let searches_container = document.querySelector(".saved-searches-holder")
                if(searches_container.childElementCount <= 0){
                    let empty_paragraph = document.createElement("p")
                    empty_paragraph.innerHTML = "Currently you don't have any saved searches"
                    searches_container.appendChild(empty_paragraph)
                    empty_paragraph.style.color= "#6e6e6e"
                    empty_paragraph.style.fontStyle = "italic"
                    empty_paragraph.style.marginTop = "30px"
                }
            })
            .catch(err=>console.warn(err))
        }

    }
})
