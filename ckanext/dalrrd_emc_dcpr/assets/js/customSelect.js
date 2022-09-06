ckan.module("custom_select", function($){
    return{
        initialize:function(){
            console.log("custom select loaded !")
            $.proxyAll(this,/_on/);
            if(this.el.val() != "other"){
                this.el.parent().children("#custom_other_choice_select").hide()
            }
            this.el.on("change", this._onHandleSelectChange)

        },
        _onHandleSelectChange:function(e){
            let custom_input = this.el.parent().children("#custom_other_choice_select")
            if(e.target.value != "other"){
                custom_input.hide()
            }
            else{
                custom_input.show()
            }
        }
    }
})
