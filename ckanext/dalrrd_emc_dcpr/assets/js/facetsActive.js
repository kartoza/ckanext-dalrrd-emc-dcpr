"use strict";


ckan.module('emc-facets-active', function (jQuery, _) {


    return {
        initialize: function () {

            const filters = {
                'organization': 'Organizations',
                '_organization_limit': 'Organizations',
                'vocab_sasdi_themes': 'SASDIThemes',
                '_vocab_sasdi_themes_limit': 'SASDIThemes',
                'vocab_iso_topic_categories': 'ISOTopicCategories',
                '_vocab_iso_topic_categories_limit': 'ISOTopicCategories',
                'tags': 'Tags',
                '_tags_limit': 'Tags'
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
        }
    }

})


ckan.module("xml_parser",function($){
    return{
        initialize: function(){
            $.proxyAll(this,/_on/);
            this.el.on("change", this._onChange)
        },
        _onChange:function(e){
            let the_input = document.getElementById('upload_input')
            let _files = the_input.files
            let formData = new FormData();
            for(let _file of _files){
                formData.append("xml_dataset_files",_file)
            }
            fetch(window.location.href.split('?')[0]+'xml_parser/',{method:"POST", body:formData}).
            then(()=>{window.location.reload()})
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
