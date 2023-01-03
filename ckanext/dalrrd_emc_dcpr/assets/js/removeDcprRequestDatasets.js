"use strict";

ckan.module('removeDcprRequestDatasets', function(jQuery, _){

    return {
        initialize: function (){

            this.el.on('click', '.remove-dataset', this._onRemoveDatasetFieldset)
        },

        _onRemoveDatasetFieldset: function (event) {
            let fieldsetSelector = '.dynamic-dataset-fieldset'
            let datasetFieldsets = document.querySelectorAll(fieldsetSelector)
            let self = this
            let indexToRemove = self.dataset['moduleIndex']
            console.log(`Was asked to remove previous dataset, which has index ${indexToRemove}`)
            try{
                datasetFieldsets[indexToRemove -1].remove()
            }
            catch (e) {
                let index = datasetFieldsets.length-1
                datasetFieldsets[index].remove()
            }
             if(document.querySelectorAll(fieldsetSelector).length  < 2){
                let removeButton = document.querySelector('#remove-previous-dataset-button')
                removeButton.setAttribute('disabled', true)
            }

        },
    }

})
