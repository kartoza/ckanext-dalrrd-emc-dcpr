"use strict";


ckan.module('emc-temporal-query', function (jQuery, _) {

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

    function removeParameter(key, url) {
            let returnURL = url.split("?")[0],
                parameter,
                parameters_arr = [],
                queryString = (url.indexOf("?") !== -1) ? url.split("?")[1] : "";
            if (queryString !== "") {
                parameters_arr = queryString.split("&");
                for (var i = parameters_arr.length - 1; i >= 0; i -= 1) {
                    parameter = parameters_arr[i].split("=")[0];
                    if (parameter === key) {
                        parameters_arr.splice(i, 1);
                    }
                }
                if (parameters_arr.length) returnURL = returnURL + "?" + parameters_arr.join("&");
            }
            return returnURL;

            }

      return {
          initialize: function () {
                document.getElementById("ext_start_reference_date").addEventListener('change', this._activeTemporal);
                document.getElementById("ext_end_reference_date").addEventListener('change', this._activeTemporal);
            },


          _activeTemporal: function(event) {
                let url = window.location
                let self = event.target
                if(self.value){
                    let new_parameter = self.id + '=' + self.value;
                    let new_url = ''
                    if(getUrlParameter(self.id)){
                        let old_parameter = self.id + '=' + getUrlParameter(self.id);
                        new_url = url.toString().replace(old_parameter, new_parameter);
                    }
                    else{
                        const sep = (url.toString().endsWith('/') ) ? ( '?'): ('&')
                        new_url = url + sep + new_parameter
                    }
                    window.open(new_url, "_self")
                }
                else{
                    if(getUrlParameter(self.id)){
                        let new_url = removeParameter(self.id, url.toString());
                        window.open(new_url, "_self")
                    }
                }
          }
      };
});