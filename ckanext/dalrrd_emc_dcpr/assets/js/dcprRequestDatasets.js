"use strict";

ckan.module('dcprRequestDatasets', function(jQuery, _){
    return {

        options: {
            render_remove_button: true
        },

        _renderedTemplateReceived: false,

        initialize: function() {
            jQuery.proxyAll(this, /_on/);
            console.log('inside the initialize function for module dcprRequestDatasets')
            this.el.on('click', this._onAddDatasetFieldset)
            let removeButtonEl = document.querySelector('#remove-previous-dataset-button')
            removeButtonEl.addEventListener('pointerdown', this._onRemoveDatasetFieldset)
        },

        _onAddDatasetFieldset: function () {
            let numExisting = this._getNumDatasetFieldsets()
            this.options.index = numExisting + 1
            if (!this._renderedTemplateReceived) {
                this.sandbox.client.getTemplate(
                    'dcpr_request_dataset_form_fieldset.html',
                    this.options,
                    this._onReceiveRenderedTemplate,
                )
                this._renderedTemplateReceived = true
            }
        },

        _onReceiveRenderedTemplate: function (renderedHtml) {
            let parent = document.querySelector('#insert-dataset-fieldset-button')
            parent.insertAdjacentHTML('beforebegin', renderedHtml)
            this._renderedTemplateReceived = false
            let removeButtonEl = document.querySelector('#remove-previous-dataset-button')
            removeButtonEl.removeAttribute('disabled')
        },

        // _onReceiveRenderedTemplateError: function (error) {
        //     console.log(error)
        // },

        _onRemoveDatasetFieldset: function (event) {
            let datasetFieldsets = document.querySelectorAll('dynamic-dataset-fieldset')
            if (datasetFieldsets.length > 1) {
                let indexToRemove = datasetFieldsets.length - 1
                console.log(`Was asked to remove previous dataset, which has index ${indexToRemove}`)
            }
        },

        _getNumDatasetFieldsets: function () {
            let parent = document.querySelector('fieldset#dcpr-request-owner-fields')
            return parent.querySelectorAll('fieldset').length
        }
    }
})
