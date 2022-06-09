"use strict";

ckan.module('removeDcprRequestDatasets', function(jQuery, _){

    return {
        initialize: function (){
            this.el.on('click', this._onRemoveDatasetFieldset)
        },

        _onRemoveDatasetFieldset: function (event) {
            let fieldsetSelector = '.dynamic-dataset-fieldset'
            let datasetFieldsets = document.querySelectorAll(fieldsetSelector)
            let self = this
            let indexToRemove = self.dataset['moduleIndex']
            let datasetID = '#dataset'+indexToRemove
            console.log(`Was asked to remove previous dataset, which has index ${indexToRemove}`)
            let index = indexToRemove -1
            if(datasetFieldsets.length == 1){
                index = 0
                let addButton = document.querySelector('#insert-dataset-fieldset-button')
                addButton.click()
            }
            try {
                datasetFieldsets[index].remove()
            }
            catch (e) {
                datasetFieldsets[index - 1].remove()
            }
            let datasetPanel = document.querySelector(datasetID)
            datasetPanel.style.display = 'none'

        },
    }

})
