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

            if(datasetFieldsets.length < 2){
                let addButton = document.querySelector('#insert-dataset-fieldset-button')
                datasetFieldsets[0].remove()
                addButton.click()
            }
            try{
                datasetFieldsets[indexToRemove -1].remove()
            }
            catch (e) {
                let index = datasetFieldsets.length-1
                datasetFieldsets[index].remove()
            }

        },
    }

})
