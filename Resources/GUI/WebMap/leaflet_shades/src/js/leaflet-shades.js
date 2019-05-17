var L = require('leaflet');
require('leaflet-editable');
require('leaflet.path.drag');

var LeafletShades = L.Layer.extend({
	includes: L.Evented ? L.Evented.prototype : L.Mixin.Events,

	options: {
		bounds: null
	},

	initialize: function(options) {
		L.setOptions(this, options);
	},

	onAdd: function(map) {
		this._map = map;
		this._addEventListeners();

		this._shadesContainer = L.DomUtil.create('div', 'leaflet-areaselect-container leaflet-zoom-hide');
		this._topShade = L.DomUtil.create('div', 'leaflet-areaselect-shade', this._shadesContainer);
		this._bottomShade = L.DomUtil.create('div', 'leaflet-areaselect-shade', this._shadesContainer);
		this._leftShade = L.DomUtil.create('div', 'leaflet-areaselect-shade', this._shadesContainer);
		this._rightShade = L.DomUtil.create('div', 'leaflet-areaselect-shade', this._shadesContainer);

		map.getPanes().overlayPane.appendChild(this._shadesContainer);
		if (this.options.bounds) this._updateShades(this.options.bounds)
	},

	_addEventListeners: function() {
		this._map.on('editable:drawing:commit', this._onBoundsChanged.bind(this));
		this._map.on('editable:vertex:dragend', this._onBoundsChanged.bind(this));
  		this._map.on('editable:dragend', this._onBoundsChanged.bind(this));
  		this._map.on('moveend', this._updatedMapPosition.bind(this));
	},

	_onBoundsChanged: function (event) {
		var _bounds = event.layer.getBounds();
		this.fire('shades:bounds-changed', {
			bounds: _bounds
		});
		this._updateShades(_bounds);
	},

	_updatedMapPosition: function(event) {
		if (this._bounds) {
			this.fire('shades:bounds-changed', {
				bounds: this._bounds
			});
			this._updateShades(this._bounds);
		}
	},

	_getOffset: function() {
  		// Getting the transformation value through style attributes
  		var transformation = this._map.getPanes().mapPane.style.transform
  		const startIndex = transformation.indexOf('(')
  		const endIndex = transformation.indexOf(')')
  		transformation = transformation.substring(startIndex + 1, endIndex).split(',')
		const offset = {
			x: parseInt(transformation[0], 10) * -1,
		    y: parseInt(transformation[1], 10) * -1
		}
  		return offset
	},

	_updateShades: function (bounds) {
		if (bounds !== this._bounds) this._bounds = bounds;

		const size = this._map.getSize();
		const northEastPoint = this._map.latLngToContainerPoint(bounds.getNorthEast());
		const southWestPoint = this._map.latLngToContainerPoint(bounds.getSouthWest());
		const offset = this._getOffset();

		this.setDimensions(this._topShade, {
		    width: size.x,
		    height: (northEastPoint.y < 0) ? 0 : northEastPoint.y,
		    top: offset.y,
		    left: offset.x
	  	})

	  	this.setDimensions(this._bottomShade, {
		    width: size.x,
		    height: size.y - southWestPoint.y,
		    top: southWestPoint.y + offset.y,
		    left: offset.x
		})

		this.setDimensions(this._leftShade, {
		    width: (southWestPoint.x < 0) ? 0 : southWestPoint.x,
		    height: southWestPoint.y - northEastPoint.y,
		    top: northEastPoint.y + offset.y,
		    left: offset.x
		})

		this.setDimensions(this._rightShade, {
		    width: size.x - northEastPoint.x,
		    height: southWestPoint.y - northEastPoint.y,
		    top: northEastPoint.y + offset.y,
		    left: northEastPoint.x + offset.x
		})
	},

	setDimensions: function(element, dimensions) {
		element.style.width = dimensions.width + 'px';
		element.style.height = dimensions.height + 'px';
		element.style.top = dimensions.top + 'px';
		element.style.left = dimensions.left + 'px';
	},

	onRemove: function(map) {
		map.getPanes().overlayPane.removeChild(this._shadesContainer);
		map.off('editable:drawing:commit', this._onBoundsChanged.bind(this));
		map.off('editable:vertex:dragend', this._onBoundsChanged.bind(this));
  		map.off('editable:dragend', this._onBoundsChanged.bind(this));
  		map.off('moveend', this._updatedMapPosition.bind(this));
	}
});

module.exports = LeafletShades;
