//
// Script Name:     WebMap2.js
// Script Author:   Kevin Foley, Civil Engineer, Reclamation
// Last Modified:   Dec 20, 2018
//
// Description:     'WebMap2.js' is the javascript portion of a web map application used
//                  to select stations and datasets in the PyForecast application. This
//                  script uses the MapboxGL javascript API to map GeoJSON files located
//                  in the GIS folder



///////////////// DEFINE STARTUP VARIABLES /////////////////////////////////
// This section defines all the variables that are called when the webpage
// initially loads. These variables are available to the javascript as
// global variables (with the 'window' handle) throughout the session
var initialLoad = false;
var rect1 = null;
var hucLayer = null;
var hucList = null;
var loaded = false;

// Set up an initial map with a basic basemap
var grayMap = L.tileLayer('http://{s}.tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'});
var terrainMap =  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri'});
var streetMap =  L.tileLayer('https://{s}.tile.openstreetmap.de/tiles/osmde/{z}/{x}/{y}.png', {
	maxZoom: 18,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'});

var map = L.map('map',
    {zoomControl: true,
    editable: true,
    layers: [grayMap]}).setView([ 43, -113], 7); // Set up a map centered on the U.S. at zoom level 4

// Store the basemaps in a dict
var baseMaps = {'Grayscale': grayMap,
                'Terrain': terrainMap, 
                'Streets': streetMap};

// Create map panes
map.createPane("HUCPane")
map.createPane('ClimPane')
map.createPane("PointsPane")

// Add controls
var layerControl = L.control.layers(baseMaps).addTo(map);

// Create a layer Group
var layerGrp = L.layerGroup();
loadWatersheds();
//loadClimateDivisions();

map.on('zoomend', function() {
    updateApplication()});
map.on('moveend', function() {
    updateApplication()});
map.on('baselayerchange', function() {
    updateApplication()});
map.on('overlayadd', function() {
    updateApplication()});
map.on('overlayremove', function() {
    updateApplication()});

function addPopups(layerG) {
    layerG.eachLayer(function (layer) {
        layer.on("click", function(e) {
            var hiddenID = String(e.layer.feature.properties.DatasetInternalID);
            var id = e.layer.feature.properties.DatasetExternalID;
            var agency = e.layer.feature.properties.DatasetAgency;
            var typ = e.layer.feature.properties.DatasetType;
            var name = e.layer.feature.properties.DatasetName;
            var param = e.layer.feature.properties.DatasetParameter;
            var elev = e.layer.feature.properties.DatasetElevation;

            var popHTML = `<strong>${agency} ${typ}</strong>` + 
                            `<p>Name: ${name}` + 
                            `</br>ID: ${id}`
            popHTML = popHTML + `</br>Elevation: ${elev}`
            
            if (hiddenID.includes('|')) {
                popHTML = popHTML + `</br><select id='param' onchange="updatePOR()">`;
                var params = param.split('|');
                params.forEach( function(parameter){
                    popHTML = popHTML + `<option>${parameter}</option>`
                });
                popHTML = popHTML + '</select>';
                var sdates = e.layer.feature.properties.DatasetPORStart.split('|');
                var edates = e.layer.feature.properties.DatasetPOREnd.split('|');
                var firststart = new Date(sdates[0]);
                var firstend = new Date(edates[0]);
                var dates = firststart.getFullYear() + ' - ' + firstend.getFullYear();
                popHTML = popHTML + `</br><span data-pors="${sdates}||${edates}" id='por' style='margin:0; padding:0;'>POR: ${dates}</span>`

            } else {
                popHTML = popHTML + `</br>Parameter: ${param}`
                var sdate = new Date(e.layer.feature.properties.DatasetPORStart);
                var edate = new Date(e.layer.feature.properties.DatasetPOREnd);
                var por = sdate.getFullYear() + ' - ' + edate.getFullYear();
                popHTML = popHTML + `</br>POR: ${por}`
            };

            

            if (agency == 'USGS') {
                var url = "https://waterdata.usgs.gov/nwis/inventory/?site_no="+id;
                popHTML = popHTML + `</br><a href = ${url}>Website</a></p>`
            } else if (agency == 'NRCS' && typ == 'SNOTEL') {
                var url = "https://wcc.sc.egov.usda.gov/nwcc/site?sitenum="+id;
                popHTML = popHTML + `</br><a href = ${url}>Website</a></p>`
            } else {
                var url = 'No Website';
                popHTML = popHTML + `</p>`
            };
            popHTML = popHTML + '<button type="button" onclick="buttonPress()">Add Dataset</button>' + `<p hidden id="ids" style="margin:0">${hiddenID}</p>` ;
            
            var pop = L.popup().setLatLng(e.latlng).setContent(popHTML).addTo(window.map);
        });
    });
};


/////////////////// DEFINE FUNCTIONS ///////////////////////////////////////
// This section defines javascript functions that are called from within this
// script or from outside of the script by the web browser

function updatePOR() {
    var idx = document.getElementById('param').selectedIndex;
    var pors = document.getElementById('por').getAttribute('data-pors');
    var sdates = pors.split('||')[0].split(',');
    var edates = pors.split('||')[1].split(',');
    //var sdates = document.getElementById('pstarts').innerHTML.split(',');
    //var edates = document.getElementById('pends').innerHTML.split(',');
    var y1 = new Date(sdates[idx]);
    var y2 = new Date(edates[idx]);
    var por = y1.getFullYear() + ' - ' + y2.getFullYear();
    document.getElementById('por').innerHTML = `POR: ${por}`;
};


function buttonPress() {
    
    var id = document.getElementById('ids').innerHTML;
    if (id.includes('|')) {
        var idx = document.getElementById('param').selectedIndex;
        id = id.split('|');
        id = id[idx];
        console.log('ID:'+id);
    } else {
        console.log('ID:'+id);
    }
    
};

// This function loads the dataset directory from the datasetString.
// For each feature in the geojson string, it determines
// the type of dataset and assigns a color accordingly
function loadJSONData(datasetString) {
    if (window.initialLoad == true) {
        return
    };
    window.initialLoad = true;
    var types = ['STREAMGAGE','SNOTEL','SNOWCOURSE','SCAN', 'RESERVOIR'];
    var data = datasetString;
    //var data = JSON.parse(datasetString);
    types.forEach(function(type) {
        var layer = L.geoJSON(data, {
            filter: function(feature, layer) {
                return feature.properties.DatasetType == type;
            },
            pointToLayer: function (feature, latlng) {
                var fillColor = "#cf56ff";
                switch (feature.properties.DatasetType) {
                    case 'STREAMGAGE': 
                        fillColor = '#23ff27';
                        break;
                    case 'SNOTEL': 
                        fillColor = '#4cffed';
                        break;
                    case 'SNOWCOURSE': 
                        fillColor = '#00beff';
                        break;
                    case 'SCAN': 
                        fillColor = '#604fa5';
                        break;
                    case 'RESERVOIR':
                        fillColor = '#005dff';
                        break;
                };
                var markr = L.circleMarker (latlng, {
                    pane: "PointsPane",
                    fillColor: fillColor,
                    color: "#000000",
                    weight: 1,
                    radius: 7,
                    fillOpacity: 1
                    }
                );
                return markr;
            }
        }).addTo(window.map);
        window.layerGrp.addLayer(layer);
        window.layerControl.addOverlay(layer, type);
        
    });
    addPopups(window.layerGrp);
};

function HUCPress() {
    var id = document.getElementById('hucNum').innerHTML;
   
    console.log('HUC:'+id);
   
}

function PDSIPress() {
    var id = document.getElementById('pdsiNum').innerHTML;
    console.log('PDSI:'+id);
}

function loadWatersheds() {
    window.hucLayer = L.esri.featureLayer({
        url: "https://geodata.epa.gov/arcgis/rest/services/r4/Watersheds/MapServer/2",
        simplifyFactor: 0.4,
        precision: 4,
        pane: "HUCPane",
        fields: ['OBJECTID','HUC_8', 'SUBBASIN'],
        renderer: L.canvas(),
        style: {
            color: '#4286f4',
            fillOpacity: 0,
            weight: 1,
            opacity: 0.8,
        }
    }).addTo(window.map);
    window.hucLayer.on('mouseout', function(e){
        window.hucLayer.resetFeatureStyle(e.layer.feature.id)
    });
    window.hucLayer.on('click', function(e){
        var coordinates = getCenter(e.layer.feature, e);
        var name = e.layer.feature.properties.SUBBASIN;
        var num = e.layer.feature.properties.HUC_8;
        var popHTML = "<strong>HUC8: " + num + "</strong><p>Name: " + name + "</p>"
        popHTML = popHTML + '<button type="button" onclick="HUCPress()">Add Temp/Precip</button>' + `<p hidden id="hucNum" style="margin:0">${num}</p>` ;
        var pop = L.popup().setLatLng(coordinates).setContent(popHTML).addTo(window.map);
    });
    window.hucLayer.on("mouseover", function(e){
        window.hucLayer.setFeatureStyle(e.layer.feature.id, {
            color: "#0000ff",
            weight: 3,
            fillOpacity: 0
        })
    });
    window.layerControl.addOverlay(window.hucLayer, 'Watersheds')
}

function loadClimateDivisions() {
    window.climLayer = L.esri.featureLayer({
        url: "https://services1.arcgis.com/hLJbHVT9ZrDIzK0I/arcgis/rest/services/ClimateDivisionsOnly/FeatureServer/0",
        simplifyFactor: 1.2,
        precision: 3,
        pane: "ClimPane",
        fields: ['OBJECTID','STATE', 'CLIMDIV', 'NAME'],
        renderer: L.canvas(),
        style: {
            color: '#ce7a2b',
            fillOpacity: 0,
            weight: 1,
            opacity: 0.8,
        }
    }).addTo(window.map);

    window.climLayer.on('mouseout', function(e){
        window.climLayer.resetFeatureStyle(e.layer.feature.id)
    });

    window.climLayer.on("mouseover", function(e){
        window.climLayer.setFeatureStyle(e.layer.feature.id, {
            color: "#ff7b00",
            weight: 3,
            fillOpacity: 0
        })
    });

    window.climLayer.on('click', function(e){
        var coordinates = getCenter(e.layer.feature, e);
        var name = e.layer.feature.properties.NAME;
        var num = e.layer.feature.properties.CLIMDIV;
        var popHTML = "<strong>NAME: " + name + "</strong><p>Number: " + num + "</p>"
        popHTML = popHTML + '<button type="button" onclick="PDSIPress()">Add PDSI</button>' + `<p hidden id="pdsiNum" style="margin:0">${num}</p>` ;
        var pop = L.popup().setLatLng(coordinates).setContent(popHTML).addTo(window.map);
    });
    window.layerControl.addOverlay(window.climLayer, 'Climate Divisions')
}

function moveToMarker(lat, lng) {
    window.map.setView([lat, lng], 12)
}

function enableHUCSelect() {
    window.hucList = [];
    window.hucLayer.setStyle({
        color: '#4286f4',
        fillOpacity: 0,
        weight: 1,
        opacity: 0.8, 
    });
    window.hucLayer.off('click');
    window.hucLayer.off('mouseout');
    window.hucLayer.off('mouseover');
    window.hucLayer.on('click', function(e) {
        var HUC = e.layer.feature.properties.HUC_8;
        if (window.hucList.includes(HUC)) {
            var idx = window.hucList.indexOf(HUC);
            if (idx > -1) {
                window.hucList.splice(idx, 1);
                window.hucLayer.resetFeatureStyle(e.layer.feature.id);
            }
        } else {
            window.hucLayer.setFeatureStyle(e.layer.feature.id, {
                fillColor: '#ff0000',
                weight: 2,
                fillOpacity: 0.4
            });
            window.hucList.push(HUC);
        };
    })
}

function getSelectedHUCs() {
    window.hucLayer.setStyle({
            color: '#4286f4',
            fillOpacity: 0,
            weight: 1,
            opacity: 0.8, 
    });
    window.hucLayer.on('mouseout', function(e){
        window.hucLayer.resetFeatureStyle(e.layer.feature.id)
    });
    window.hucLayer.on('click', function(e){
        var coordinates = getCenter(e.layer.feature, e);
        var name = e.layer.feature.properties.SUBBASIN;
        var num = e.layer.feature.properties.HUC_8;
        var popHTML = "<strong>HUC8: " + num + "</strong><p>Name: " + name + "</p>"
        var pop = L.popup().setLatLng(coordinates).setContent(popHTML).addTo(window.map);
    });
    window.hucLayer.on("mouseover", function(e){
        window.hucLayer.setFeatureStyle(e.layer.feature.id, {
            color: "#0000ff",
            weight: 3,
            fillOpacity: 0
        })
    });
    return window.hucList;
}

// Function to enable drawable rectangle on map
function enableBBSelect() {
    window.hucLayer.setStyle({
        color: '#4286f4',
        fillOpacity: 0,
        weight: 1,
        opacity: 0.8, 
    });
    window.hucLayer.off('mouseover');
    window.rect1 = window.map.editTools.startRectangle();
}

function getBBCoords() {
    window.hucLayer.on("mouseover", function(e){
        window.hucLayer.setFeatureStyle(e.layer.feature.id, {
            color: "#0000ff",
            weight: 3,
            fillOpacity: 0
        })
    });
    var coords = window.rect1.getBounds();
    var nw = coords.getNorthWest();
    var se = coords.getSouthEast();
    var nwlat = nw.lat;
    var nwlong = nw.lng;
    var selat = se.lat;
    var selong = se.lng;
    
    window.rect1.remove();
    window.map.editTools.stopDrawing();

    return `COORDS:${nwlat}|${nwlong}|${selat}|${selong}`
}

function setActiveLayers(layers) {
    
    layers = layers.split(",");
    console.log(layers);
    window.layerControl._layers.forEach(function (obj) {
        if (obj.overlay == true) {
            window.map.removeLayer(obj.layer);
        }
    });
    layers.forEach(function(lay){
        window.layerControl._layers.forEach(function (obj) {
            if (lay == obj.name) {
                window.map.addLayer(obj.layer);
            }
        });
    })
};
    



function getActiveLayers() {
    var active = [];
    window.layerControl._layers.forEach(function (obj) {
        if (window.map.hasLayer(obj.layer)) {
            active.push(obj.name);
        }
    })
    return `ACTIVELAYERS:${active}`;
}

function updateApplication() {
    
    if (window.loaded == true) {
        var loc_ = getLocation();
        var layers_ = getActiveLayers();
        window.foo.getJavascriptVariable([loc_, layers_]);
        return;
    } else {
        return;
    }
}

function getLocation() {
    latlong = window.map.getCenter();
    lt = latlong.lat;
    lg = latlong.lng;
    zoom = window.map.getZoom();
    return `POSITION:${lt}|${lg}|${zoom}`
}

function zoomToLoc(lat, long, zoomLevel) {
    window.map.setView([lat, long], zoomLevel);
}

// Function to find center of polygon
function getCenter(feat, ev) {
    var lats = 0;
    var longs = 0;
    var count = 0;
    for (i = 0; i < feat.geometry.coordinates[0].length; i++) {
        var lt = feat.geometry.coordinates[0][i][1];
        var ln = feat.geometry.coordinates[0][i][0];
        if (isNaN(lt) == false && isNaN(ln) == false) {
            
            lats += lt;
            longs += ln;
            count += 1;
        }
        
    };
    var meanLat = lats / count;
    var meanLong = longs / count;
    var coords = [meanLat, meanLong];
    if (isNaN(meanLat) || isNaN(meanLong) ) {
        return window.map.mouseEventToLatLng(ev.originalEvent);
    }
    
    return coords;
};

