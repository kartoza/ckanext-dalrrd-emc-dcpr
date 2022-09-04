"use strict";

ckan.module("xml_parser",function($){
    /*

        handles creating datasets from xml file
        upload.

        this isn't completed yet, the idea is to show
        a flash message when the xml file is incorrect
        after the page reloads.

        usage:
        ----
        this module is used with the search page.

    */
    return{
        initialize: function(){
            $.proxyAll(this,/_on/);
            this.el.on("change", this._onChange)
        },
        _handleError:function(response) {
            if (!response.ok) {
                return response.text().then(txt => {throw new Error(txt)})
            }
            return response;
        } ,
        _onChange:function(e){
            let the_input = document.getElementById('upload_input')
            let _files = the_input.files
            let formData = new FormData();
            for(let _file of _files){
                formData.append("xml_dataset_files",_file)
            }

            let flash_box = document.getElementsByClassName("flash-messages")[0]

            let msg_box_creation = function(class_list, msg){
                // DRY
                let info_or_err = document.createElement("div")
                let close_btn = document.createElement("a")
                close_btn.classList.add("close")
                close_btn.setAttribute("href","#")
                close_btn.innerHTML = "×"
                info_or_err.classList.add(...class_list)
                info_or_err.innerHTML = msg
                info_or_err.append(close_btn)
                flash_box.append(info_or_err)
            }

            fetch(window.location.href.split('?')[0]+'xml_parser/',{method:"POST", body:formData}).
            then(res => this._handleError(res)).
            then(res=>res.json()).then(
                (data)=>{
                    console.log(data)
                    let err_msgs = data.response.err_msgs
                    let info_msgs = data.response.info_msgs
                    console.log("error messages:", err_msgs)
                    if(err_msgs == undefined && info_msgs == undefined){
                        if(data.response.includes("all packages were created")){
                            // the cause where everything went right
                            // sessionStorage.setItem("reloading", "true");
                            // document.location.reload();
                            // //window.location.reload()
                            // window.addEventListener("load", function(){
                            //     var reloading = sessionStorage.getItem("reloading");
                            //     if (reloading) {
                            //         sessionStorage.removeItem("reloading");
                            //         msg_box_creation(["alert","fade-in","alert-info"], data.response)
                            //     }

                            // })
                            msg_box_creation(["alert","fade-in","alert-info"], data.response)
                        }
                    }
                    else {
                        for(let err of err_msgs){
                            msg_box_creation(["warning-explanation","alert","alert-danger"], err)
                        }
                        for(let info of info_msgs){
                            msg_box_creation(["alert","fade-in","alert-info"], info)
                        }
                    }

                    flash_box.style.display = "block"
                    // window.location.reload()
                }
                ).catch(err=>{
                    msg_box_creation(["warning-explanation","alert","alert-danger"], err)
                    flash_box.style.display = "block"
                    console.log(err)
                })
        }
    }
})
