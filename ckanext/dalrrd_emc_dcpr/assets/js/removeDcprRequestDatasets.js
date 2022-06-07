"use strict";

ckan.module('remoceDcprRequestDatasets', function(jQuery, _){

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
            let lastDatasetFieldset = datasetFieldsets[indexToRemove -1]
            lastDatasetFieldset.remove()
            let datasetPanel = document.querySelector(datasetID)
            datasetPanel.style.display = 'none'
        },
    }

})