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
                'vocab_sasdi_themes': 'SASDITheme',
                'vocab_iso_topic_categories': 'ISOTopicCategory',
                'tags': 'Tags'
            };
            const keys = Object.keys(filters);

            for(let i=0; i<keys.length; i++){
                if(getUrlParameter(keys[i])){
               document.getElementById(filters[keys[i]]).classList.add("in")
           }
       }
        }
    }

})
