"use strict";


ckan.module('emc-facets-active', function (jQuery, _) {


    return {
        initialize: function () {

            const filters = {
                'organization': 'Organizations',
                '_organization_limit': 'Organizations',
                'vocab_sasdi_themes': 'SASDIThemes',
                '_vocab_sasdi_themes_limit': 'SASDIThemes',
                'vocab_iso_topic_categories': 'ISOTopicCategories',
                '_vocab_iso_topic_categories_limit': 'ISOTopicCategories',
                'tags': 'Tags',
                '_tags_limit': 'Tags'
            };
            const keys = Object.keys(filters);

            for(let i=0; i<keys.length; i++){
                if(getUrlParameter(keys[i])){
                    document.getElementById(filters[keys[i]]).classList.add("in")
                    const link = "a[href='#"+filters[keys[i]]+"']";
                    const a = document.querySelectorAll(link);
                    a[0].setAttribute('aria-expanded', 'true')

                }
                const head = document.getElementById('head' + filters[keys[i]]);
                const title = head.querySelector('.panel-title');
                const link = title.querySelector('.panel-title-link');
                if(link.getAttribute('aria-expanded')==true){
                    alert(head);
                }
       }
        }
    }

})

ckan.module("emc-filter-expand", function ($){
    return {
        initialize: function(){

            $.proxyAll(this,/_on/);
            this.el.on('click', this._onClick);

        },

        _onClick: function (event) {
            const parents = event.target.parentNode.parentNode.parentNode;
            const expand = event.target.getAttribute('aria-expanded');
            const classes = parents.classList
            if(parents.classList.contains('expanded')){
                parents.classList.remove('expanded');
            }
            else {
                parents.classList.add('expanded')
            }
        }
    }


})

ckan.module("emc-facets-pagination", function ($){

    return{

        initialize: function(){
            let itemsTags, itemsOrganizations, itemsSASDIThemes, itemsISOTopicCategories, itemsDCPRRequest, itemsHarvestsource;
            itemsTags = itemsOrganizations = itemsSASDIThemes = itemsISOTopicCategories =
                itemsDCPRRequest = itemsHarvestsource= 10;
            let allOrganizations = $('.facet-outer-Organizations li').length;
            let allSASDIThemes = $('.facet-outer-SASDIThemes li').length;
            let allISOTopicCategories = $('.facet-outer-ISOTopicCategories li').length;
            let allTags = $('.facet-outer-Tags li').length;
            let allDCPRRequest = $('.facet-outer-DCPRRequest li').length;
            let allHarvestsource = $('.facet-outer-Harvestsource li').length;
            const pagination = 10;
            if (itemsSASDIThemes > allSASDIThemes) {
                     $('#showMoreSASDIThemes').hide();
                 }
            if (itemsISOTopicCategories > allISOTopicCategories) {
                     $('#showMoreISOTopicCategories').hide();
                 }
            if (itemsOrganizations > allOrganizations) {
                     $('#showMoreOrganizations').hide();
                 }
            if (itemsTags > allTags) {
                     $('#showMoreTags').hide();
                 }
            if (itemsDCPRRequest > allDCPRRequest) {
                     $('#showMoreDCPRRequest').hide();
                 }
            if (itemsHarvestsource > allHarvestsource) {
                $('#showMoreHarvestsource').hide();
            }
            for(let i = 0; i<pagination; i++){
                $('.facet-outer-Organizations li:eq(' + i + ')').show();
                $('.facet-outer-SASDIThemes li:eq(' + i + ')').show();
                $('.facet-outer-ISOTopicCategories li:eq(' + i + ')').show();
                $('.facet-outer-Tags li:eq(' + i + ')').show();
                $('.facet-outer-DCPRRequest li:eq(' + i + ')').show();
                $('.facet-outer-Harvestsource li:eq(' + i + ')').show();
            }

            $('#showMoreSASDIThemes').on('click', function () {
                console.log(itemsSASDIThemes)
                for (let i = itemsSASDIThemes; i < (itemsSASDIThemes + pagination); i++) {
                    $('.facet-outer-SASDIThemes li:eq(' + i + ')').show();
                }
                itemsSASDIThemes += pagination;
                 if (itemsSASDIThemes > allSASDIThemes) {
                     $('#showMoreSASDIThemes').hide();
                 }
            }
            );

            $('#showMoreISOTopicCategories').on('click', function () {

                for (let i = itemsISOTopicCategories; i < (itemsISOTopicCategories + pagination); i++) {
                    $('.facet-outer-ISOTopicCategories li:eq(' + i + ')').show();
                }
                itemsISOTopicCategories += pagination;
                 if (itemsISOTopicCategories > allISOTopicCategories) {
                     $('#showMoreISOTopicCategories').hide();
                 }
            }
            );

            $('#showMoreOrganizations').on('click', function () {

                for (let i = itemsOrganizations; i < (itemsOrganizations + pagination); i++) {
                    $('.facet-outer-Organizations li:eq(' + i + ')').show();
                }
                itemsOrganizations += pagination;
                 if (itemsOrganizations > allOrganizations) {
                     $('#showMoreOrganizations').hide();
                 }
            }
            );

            $('#showMoreTags').on('click', function () {
                for (let i = itemsTags; i < (itemsTags + pagination); i++) {
                    $('.facet-outer-Tags li:eq(' + i + ')').show();
                }
                itemsTags += pagination;
                 if (itemsTags > allTags) {
                     $('#showMoreTags').hide();
                 }
            }
            );
            $('#showMoreDCPRRequest').on('click', function () {
                for (let i = itemsDCPRRequest; i < (itemsDCPRRequest + pagination); i++) {
                    $('.facet-outer-DCPRRequest li:eq(' + i + ')').show();
                }
                itemsDCPRRequest += pagination;
                 if (itemsDCPRRequest > allDCPRRequest) {
                     $('#showMoreDCPRRequest').hide();
                 }
            }
            );
            $('#showMoreHarvestsource').on('click', function () {
                for (let i = itemsHarvestsource; i < (itemsHarvestsource + pagination); i++) {
                    $('.facet-outer-Harvestsource li:eq(' + i + ')').show();
                }
                itemsHarvestsource += pagination;
                 if (itemsHarvestsource > allHarvestsource) {
                     $('#showMoreHarvestsource').hide();
                 }
            }
            );

        },



    }

})
