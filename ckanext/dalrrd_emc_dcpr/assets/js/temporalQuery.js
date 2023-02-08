"use strict";



ckan.module('emc-temporal-query', function (jQuery, _) {

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
                    if(url.toString().includes(self.id)){
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
