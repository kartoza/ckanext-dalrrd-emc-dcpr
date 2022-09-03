"use strict";

ckan.module("xml_parser_sep",function($){
    return{
        initialize: function(){
            console.log("xml parser is loaded !")
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
