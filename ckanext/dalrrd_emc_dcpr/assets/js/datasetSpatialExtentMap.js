"use strict";

/* datasetSpatialExtentMap
*
* Displays a leaflet map
*
* */
ckan.module("emcDatasetSpatialExtentMap", function(jQuery, _){
    return {
        options: {
            i18n: {
            },
            styles: {
                point:{
                    iconUrl: '/img/marker.png',
                    iconSize: [14, 25],
                    iconAnchor: [7, 25]
                },
                default_:{
                    color: '#B52',
                    weight: 2,
                    opacity: 1,
                    fillColor: '#FCF6CF',
                    fillOpacity: 0.4
                }
            }
        },

        initialize: function() {
            this.defaultExtent = this.options.defaultExtent

            console.log(
                `Hi there, I'm running inside the emcDatasetSpatialExtentMap module. ` +
                `Oh, and my bound element is ${this.el} and the Jinja template passed me this as the default extent: ${this.defaultExtent}`
            )

            jQuery.proxyAll(this, /_on/);
            this.el.ready(this._onReady);

        },

        _onReady: function() {
            this.map = ckan.commonLeafletMap(
                "dataset-spatial-extent-map-container",
                this.options.mapConfig,
                {
                    drawControl: true,
                    attributionControl: false
                }
            )
            this.map.on("click", this._onMapClick)
            const ckanIcon = L.Icon.extend({options: this.options.styles.point});
            const extentLayer = L.geoJson(this.defaultExtent, {
                style: this.options.styles.default_,
                pointToLayer: function (feature, latLng) {
                    return new L.Marker(latLng, {icon: new ckanIcon})
                }});
            extentLayer.addTo(this.map);

            const drawnItemsLayer = new L.FeatureGroup()
            this.map.addLayer(drawnItemsLayer)

            const drawControl = new L.Control.Draw({
                edit: {
                    featureGroup: drawnItemsLayer
                }
            })
            this.map.addControl(drawControl)

            this.map.fitBounds(extentLayer.getBounds())
        },
    }
})
