"use strict";

/* datasetSpatialExtentMap
*
* Displays a leaflet map
*
* */
var LeafletMapFromExtentModule
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
            this.formInputElement = document.getElementById(this.options.formInputId)


            // console.log(
            //     `Hi there, I'm running inside the emcDatasetSpatialExtentMap module. ` +
            //     `Oh, and my bound element is ${this.el} and the Jinja template passed me this as the default extent: ${this.options.defaultExtent}`
            // )

            jQuery.proxyAll(this, /_on/);
            this.el.ready(this._onReady);

        },

        _onReady: function() {
            this.map = L.map("dataset-spatial-extent-map-container", this.options.mapConfig, {
                attributionControl: false
            })
            this.map.pm.addControls({
                position: "topleft",
                drawMarker: false,
                drawCircleMarker: false,
                drawPolyline: false,
                drawRectangle: true,
                drawPolygon: false,
                drawCircle: false,
                cutPolygon: false,
                removalMode: true,
                rotateMode: false,
                pinningOption: false,
                snappingOption: false,
                splitMode: false,
                scaleMode: false,
            })

            // This is based on the base map used in ckanext-spatial
            const baseLayerUrl = 'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png';
            let leafletBaseLayerOptions = {
                subdomains: this.options.mapConfig.subdomains || "abcd",
                attribution: this.options.mapConfig.attribution || 'Map tiles by <a href="http://stamen.com">Stamen Design</a> (<a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>). Data by <a href="http://openstreetmap.org">OpenStreetMap</a> (<a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>)'
            }
            const baseLayer = new L.TileLayer(baseLayerUrl, leafletBaseLayerOptions)
            this.map.addLayer(baseLayer)

            this.rectangleLayer = L.rectangle(
                [
                    [this.options.defaultExtent[2], this.options.defaultExtent[1]],
                    [this.options.defaultExtent[0], this.options.defaultExtent[3]],
                ],
                {pmIgnore: false}
            )
            this.map.on("pm:drawstart", this._onDrawStart)
            this.map.on("pm:create", this._onCreate)
            this.map.on("pm:remove", this._onRemove)
            this.rectangleLayer.on("pm:edit", this._onLayerEdit)
            this.rectangleLayer.on("pm:dragend", this._onLayerDrag)
            this.formInputElement.addEventListener("change", this._onBoundingBoxManuallyUpdated)

            //this.map.addLayer(this.rectangleLayer)
            this.map.fitBounds(this.rectangleLayer.getBounds())

            LeafletMapFromExtentModule = this.map
        },

        _onRemove: function (event) {
            this.formInputElement.setAttribute("value", "")
        },

        _onCreate: function (event) {
            // console.log("Created new")
            event.layer.on("pm:edit", this._onLayerEdit)
            event.layer.on("pm:dragend", this._onLayerDrag)
            this.formInputElement.setAttribute("value", this._getBboxString(event.layer.getBounds()))
            this.rectangleLayer = event.layer
        },

        _onDrawStart: function (event) {
            // console.log("Started drawing")
            this.map.removeLayer(this.rectangleLayer)
        },

        _onLayerEdit: function (event) {
            this.formInputElement.setAttribute("value", this._getBboxString(event.layer.getBounds()))
        },

        _onLayerDrag: function (event) {
            this.formInputElement.setAttribute("value", this._getBboxString(event.layer.getBounds()))
        },

        _onBoundingBoxManuallyUpdated: function (event) {
            const userInput = event.target.value.split(",").map(Number)
            if (!Number.isNaN(userInput[0])) {
                const newBounds = [
                    [userInput[0], userInput[1]],
                    [userInput[2], userInput[3]],
                ]
                this.rectangleLayer.setBounds(newBounds)
            }
        },

        _getBboxString: function (bounds) {
            return `${bounds.getNorth()}, ${bounds.getWest()}, ${bounds.getSouth()}, ${bounds.getEast()}`
        },

        captializeFirstLetter: function(name){
            return name.charAt(0).toUpperCase() + name.slice(1);
        }

    }
})
