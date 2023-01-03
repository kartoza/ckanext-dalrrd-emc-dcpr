ckan.module("custom_select", function($){
    /**
     hide and show the other input field according
     to selection result with maintenance field,
     if the user selected "other" an input shows up
     to include the other option from the user.
     */

    var other_input_id = "maintenance_information-0-custom_other_choice_select"
    return{
        initialize:function(){
            $.proxyAll(this,/_on/);
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


ckan.module("custom_select_display", function($){
    /*
        this works in the display field, by default
        the display doesn't show the extra custom
        input, it only shows "other".
    */

    return{
        initialize: function(){
            $.proxyAll(this,/_on/);
            other_inputs_class = $(".dataset-label")
            for(let other_input of other_inputs_class){
                if(other_input.innerHTML.includes("Maintenance and update frequency")){
                    other_field = other_input.nextElementSibling
                    if(other_field.innerHTML.includes("other")){
                        other_field.innerHTML = this.options.text
                    }
                }
            }
        }
    }
})
