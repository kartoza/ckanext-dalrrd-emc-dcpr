/*
this module chagnes words of dataset
to metadata record in scheming and
error template

this module is used by:
1. scheming/form_snippets/custom_select_field.html
2. templates/error_document_template.html

*/

ckan.module("change_dataset_to_metadata_record", function($){
    return{
        initialize: function(){
            $("button:contains('Update Dataset')").text("Update metadata record")
            let license_text = $(".action-info:first").text()
            let modified_license_text = license_text.replace("dataset", "metadata record")
            $(".action-info:first").text(modified_license_text)
            // error page
            let error_text = document.querySelector(".module-content").innerHTML
            let modified_error = error_text.replace(/dataset/ig, "Metadata record")
            document.querySelector(".module-content").innerHTML = modified_error
        }
    }
})
