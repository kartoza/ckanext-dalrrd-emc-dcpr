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
            this.map = L.map("dataset-spatial-extent-map-container", this.options.mapConfig, {
                drawControl: false,
                attributionControl: false
            })

            // This is based on the base map used in ckanext-spatial
            const baseLayerUrl = 'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png';
            let leafletBaseLayerOptions = {
                subdomains: this.options.mapConfig.subdomains || "abcd",
                attribution: this.options.mapConfig.attribution || 'Map tiles by <a href="http://stamen.com">Stamen Design</a> (<a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>). Data by <a href="http://openstreetmap.org">OpenStreetMap</a> (<a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>)'
            }
            const baseLayer = new L.TileLayer(baseLayerUrl, leafletBaseLayerOptions)
            this.map.addLayer(baseLayer)

            // const ckanIcon = L.Icon.extend({options: this.options.styles.point});
            // const extentLayer = L.geoJson(this.defaultExtent, {
            //     style: this.options.styles.default_,
            //     pointToLayer: function (feature, latLng) {
            //         return new L.Marker(latLng, {icon: new ckanIcon})
            //     }});
            // this.map.addLayer(extentLayer)

            const rectangleLayer = L.rectangle([[54.559322, -5.767822], [56.1210604, -3.021240]])
            rectangleLayer.editing.enable()
            rectangleLayer.on("edit", this.handleEdits)

            this.map.addLayer(rectangleLayer)
            this.map.fitBounds(rectangleLayer.getBounds())
            // this.map.fitBounds(extentLayer.getBounds())

            // const drawnItems = new L.FeatureGroup([extentLayer])
            // const drawControl = new L.Control.Draw({
            //     draw: {
            //         polyline: false,
            //         polygon: false,
            //         rectangle: false,
            //         circle: false,
            //         marker: false,
            //         circlemarker: false,
            //     },
            //     edit: {
            //         featureGroup: drawnItems,
            //         edit: {
            //             maintainColor: true,
            //             opacity: 0.3
            //         },
            //         remove: false,
            //         allowIntersection: false
            //     }
            // })
            // this.map.addControl(drawControl)
            // this.map.addLayer(drawnItems)
        },

        handleEdits: function(event) {
            console.log(`layer ${event.layer} has just been edited!`)
        }

    }
})
