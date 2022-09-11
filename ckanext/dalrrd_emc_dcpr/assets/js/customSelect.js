ckan.module("custom_select", function($){
    var other_input_id = "maintenance_information-0-custom_other_choice_select"
    return{
        initialize:function(){
            $.proxyAll(this,/_on/);
            console.log(this.el.val())
            if(this.el.val() != "other"){
                this.el.parent().children(`#${other_input_id}`).hide()
            }
            this.el.on("change", this._onHandleSelectChange)

        },
        _onHandleSelectChange:function(e){
            let custom_input = this.el.parent().children(`#${other_input_id}`)
            if(e.target.value != "other"){
                custom_input.hide()
            }
            else{
                custom_input.show()
            }
        }
    }
})
