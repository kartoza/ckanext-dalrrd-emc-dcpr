"use strict";


ckan.module('emc-factes-avtive', function (jQuery, _) {

    function getUrlParameter(param) {
          let sPageURL = window.location.search.substring(1),
                URLVariables = sPageURL.split('&'),
                sParameterName,
                i;

            for (i = 0; i < URLVariables.length; i++) {
                sParameterName = URLVariables[i].split('=');

                if (sParameterName[0] === param) {
                    return sParameterName[1];
                }
            }
            return false;
    }

    return {
        initialize: function () {

            const filters = {
                'organization': 'Organizations',
                '_organization_limit': 'Organizations',
                'vocab_sasdi_themes': 'SASDITheme',
                '_vocab_sasdi_themes_limit': 'SASDITheme',
                'vocab_iso_topic_categories': 'ISOTopicCategory',
                '_vocab_iso_topic_categories_limit': 'ISOTopicCategory',
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
