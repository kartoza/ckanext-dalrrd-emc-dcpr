"use strict";


ckan.module('emc-facets-active', function (jQuery, _) {
    var searchInput = document.querySelector("#field-giant-search")

    return {

        initialize: function () {
            $.proxyAll(this,/_on/);
            searchInput.addEventListener("change", this._onSearchInputValueChange)
            const filters = {
                'organization': 'Organizations',
                '_organization_limit': 'Organizations',
                'vocab_sasdi_themes': 'SASDIThemes',
                '_vocab_sasdi_themes_limit': 'SASDIThemes',
                'vocab_iso_topic_categories': 'ISOTopicCategories',
                '_vocab_iso_topic_categories_limit': 'ISOTopicCategories',
                'tags': 'Tags',
                '_tags_limit': 'Tags',
                'featured': "FeaturedMetadatarecords"
            };
            const keys = Object.keys(filters);

            for(let i=0; i<keys.length; i++){
                if(getUrlParameter(keys[i])){
                    document.getElementById(filters[keys[i]]).classList.add("in")
                    const link = "a[href='#"+filters[keys[i]]+"']";
                    const a = document.querySelectorAll(link);
                    a[0].setAttribute('aria-expanded', 'true')

                }
                const head = document.getElementById('head' + filters[keys[i]]);
                const title = head.querySelector('.panel-title');
                const link = title.querySelector('.panel-title-link');
                if(link.getAttribute('aria-expanded')==true){
                    alert(head);
                }
       }
        },
        _onSearchInputValueChange:function(e){
            let searchUrl = this.el.get(0).href
            let searchUrlSplit = searchUrl.split("&",2)[0]
            let inputSearchTerm = searchUrlSplit.split("?q=",2)[1]
            this.el.get(0).href = searchUrl.replace(inputSearchTerm, e.target.value)
        }
    }

})

ckan.module("emc-filter-expand", function ($){
    return {
        initialize: function(){

            $.proxyAll(this,/_on/);
            this.el.on('click', this._onClick);

        },

        _onClick: function (event) {
            const parents = event.target.parentNode.parentNode.parentNode;
            const expand = event.target.getAttribute('aria-expanded');
            const classes = parents.classList
            if(parents.classList.contains('expanded')){
                parents.classList.remove('expanded');
            }
            else {
                parents.classList.add('expanded')
            }
        }
    }


})

ckan.module("emc-facets-pagination", function ($){

    return{

        initialize: function(){

            $.proxyAll(this,/_on/);
            this.el.on('click', this._showMoreFacets);

        },

        _showMoreFacets: function (e){
            let self = this
            let pagination = 10;
            let ulClassname = '.'+self.dataset['classname']
            let allItems = document.querySelectorAll(ulClassname)
            let itemsNotShow = []
            for(let i=0; i<allItems.length;i++){
                if( allItems[i].style.display===''){
                    itemsNotShow.push(allItems[i])
                }
            }
            for (let i = 0; i < (pagination); i++) {
                if(i<itemsNotShow.length){
                    itemsNotShow[i].style.display= 'block';
                }
                else{
                    self.style.display = 'none'
                }
            }

        }



    }

})
