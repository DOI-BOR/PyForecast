//
// Script Name:     WebMap2.js
// Script Author:   Kevin Foley, 
//
// Description:     'WebMap2.js' is the javascript portion of a web map application used
//                  to select stations and datasets in the PyForecast application. This
//                  script uses the MapboxGL javascript API to map GeoJSON files located
//                  in the GIS folder



// Startup Variables
var rect1 = null;
var hucList = null;
var loaded = false;


// Define Basemaps
var grayMap = L.tileLayer('http://{s}.tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'});
var terrainMap =  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri'});
var streetMap =  L.tileLayer('https://{s}.tile.openstreetmap.de/tiles/osmde/{z}/{x}/{y}.png', {
	maxZoom: 18,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'});
var imageryMap = L.tileLayer('https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 18,    
    attribution: 'U.S. Geologic Survey'});


// Create an initial map using the terrain basemap
var map = L.map('map',
    {zoomControl: true,
    editable: true,
    layers: [terrainMap]}).setView([ 43, -113], 7); // Set up a map centered on the U.S. at zoom level 4


// Store the basemaps in a dict
var baseMaps = {'Terrain': terrainMap,
                'Grayscale': grayMap, 
                'Streets': streetMap,
                'Satellite': imageryMap};

// Create map panes
map.createPane("HUCPane")
map.createPane('ClimDivPane')
map.createPane("PointsPane")

// Create a layer group
var layer_group = L.layerGroup()

// Create objects for watersheds and climate divisions
var HUC8 = new Object();
var CLIM_DIV = new Object();

// Load the data into the objects
loadJSON('../../GIS/MapData/HUC8_WGS84.json', function(response) {
    // Parse data into object
    window.HUC8 = JSON.parse(response);
});
loadJSON('../../GIS/MapData/CLIMATE_DIVISION_GEOJSON.json', function(response){
    // Parse data into object
    window.CLIM_DIV = JSON.parse(response);
});

// Create the LeafLet Layers for the Climate Divisions and the Watersheds
window.hucLayer = L.geoJSON( window.HUC8, {
    style: {
        pane: "HUCPane",
        fillColor: "#4286f4",
        weight: 1,
        opacity: .8, 
        color: "#4286f4", 
        fillOpacity: 0.0
        },
        
}).addTo(window.map);

window.hucLayer.eachLayer(function(layer) {
    layer.on("mouseover", function(e) {
        e.target.setStyle({
            color:"#4872ff",
            weight:3,
            opacity: .8,
        });
    });
    layer.on("mouseout", function(e){
        window.hucLayer.resetStyle(e.target);
    });

})


window.climLayer = L.geoJSON( window.CLIM_DIV, {
    style: {
        pane: "HUCPane",
        fillColor: "#f5bb3d",
        weight: 1,
        opacity: 0.8,
        color: "#f5bb3d",
        fillOpacity: 0,
    },
    
});

window.climLayer.eachLayer(function(layer) {
    layer.on("mouseover", function(e) {
        e.target.setStyle({
            color:"#e4ba0e",
            weight:3,
            opacity: .8,
        });
    });
    layer.on("mouseout", function(e){
        window.climLayer.resetStyle(e.target);
    });

})



// FUNCTIONS
//

// Function to load raw geojson from the PyForecast application into the map. 
//      Reads the 'geojson_string' (which is actually an object)
//      into the web map as a set of layers.
function loadDatasetCatalog(geojson_string) {

    // load json
    point_data = geojson_string;

    // Load USGS StreamGages
    window.USGSLayer = L.geoJSON(point_data, {

        // Filter for streamgages
        filter: function(feature) {
            if (feature.properties.DatasetType == 'STREAMGAGE') return true;
        },

        // Create Circle markers
        pointToLayer: function (feature, latlng) {
            return L.circleMarker(latlng, {
                pane: "PointsPane",
                fillColor: "#23ff27",
                color: "#000000",
                weight: 1,
                radius: 7,
                fillOpacity: 1
            })
        }
    }).addTo(map);
    window.layer_group.addLayer(window.USGSLayer);

    // Load NRCS SNOTEL sites
    window.SNOTELLayer = L.geoJSON(point_data, {
        
        // Filter for SNOTEL sites
        filter: function(feature) {
            if (feature.properties.DatasetType == 'SNOTEL') return true;
        },

        // Create circle markers
        pointToLayer: function (feature, latlng) {
            return L.circleMarker(latlng, {
                pane: "PointsPane",
                fillColor: "#4cffed",
                color: "#000000",
                weight: 1,
                radius: 7,
                fillOpacity: 1
            })
        }
    }).addTo(map);
    window.layer_group.addLayer(window.SNOTELLayer);

    // Load NRCS Snow Course Sites
    window.SNOWCOURSELayer = L.geoJSON(point_data, {
        
        // Filter for Snow Course Sites
        filter: function(feature) {
            if (feature.properties.DatasetType == 'SNOWCOURSE') return true;
        },

        // Create circle markers
        pointToLayer: function (feature, latlng) {
            return L.circleMarker(latlng, {
                pane: "PointsPane",
                fillColor: "#00beff",
                color: "#000000",
                weight: 1,
                radius: 7,
                fillOpacity: 1
            })
        }
    }).addTo(map);
    window.layer_group.addLayer(window.SNOWCOURSELayer);

    // Load SCAN sites
    window.SCANLayer = L.geoJSON(point_data, {
        
        // Filter for SCAN Sites
        filter: function(feature) {
            if (feature.properties.DatasetType == 'SCAN') return true;
        },

        // Create circle markers
        pointToLayer: function (feature, latlng) {
            return L.circleMarker(latlng, {
                pane: "PointsPane",
                fillColor: "#ffcc6f",
                color: "#000000",
                weight: 1,
                radius: 7,
                fillOpacity: 1
            })
        }
    }).addTo(map);
    window.layer_group.addLayer(window.SCANLayer);

    // Load USBR Reservoirs
    window.USBRLayer = L.geoJSON(point_data, {
        
        // Filter for USBR reservoirs
        filter: function(feature) {
            if (feature.properties.DatasetType == 'RESERVOIR') return true;
        },

        // Create circle markers
        pointToLayer: function (feature, latlng) {
            return L.circleMarker(latlng, {
                pane: "PointsPane",
                fillColor: "#5263fe",
                color: "#000000",
                weight: 1,
                radius: 7,
                fillOpacity: 1
            })
        }
    }).addTo(map);
    window.layer_group.addLayer(window.USBRLayer);

    // Load USBR Agrimet Sites
    window.USBRAGRIMETLayer = L.geoJSON(point_data, {
        
        // Filter for USBR AGRIMET
        filter: function(feature) {
            if (feature.properties.DatasetType == 'AGRIMET') return true;
        },

        // Create Circle Markers
        pointToLayer: function (feature, latlng) {
            return L.circleMarker(latlng, {
                pane: "PointsPane",
                fillColor: "#f47251",
                color: "#000000",
                weight: 1,
                radius: 7,
                fillOpacity: 1
            })
        }
    });
    window.layer_group.addLayer(window.USBRAGRIMETLayer);

    // Load NOAA NCDC Sites
    window.NCDCLayer = L.geoJSON(point_data, {
        
        // Filter for NCDC
        filter: function(feature) {
            if (feature.properties.DatasetType == 'NCDC') return true;
        },

        // Create Circle Markers
        pointToLayer: function (feature, latlng) {
            return L.circleMarker(latlng, {
                pane: "PointsPane",
                fillColor: "#c0c0c0",
                color: "#000000",
                weight: 1,
                radius: 7,
                fillOpacity: 1
            })
        }
    });
    window.layer_group.addLayer(window.NCDCLayer);

    // Create Popups for point and area datasets
    createPopups();

    // Create the layer control
    createLayerControlOverlay();
}

// Creates Popup windows when users click on circle markers and
// area polygons. Creates the 'add dataset' buttons
function createPopups() {
    
    // Iterate over the layers in the 'layer_group'
    window.layer_group.eachLayer(function (layer) {

        // For each layer, create a popup on click
        layer.on("click", function(e) {

            var hiddenID = String(e.layer.feature.properties.DatasetInternalID);
            var id = e.layer.feature.properties.DatasetExternalID;
            var agency = e.layer.feature.properties.DatasetAgency;
            var typ = e.layer.feature.properties.DatasetType;
            var name = e.layer.feature.properties.DatasetName;
            var param = e.layer.feature.properties.DatasetParameter;
            var elev = e.layer.feature.properties.DatasetElevation;

            var popHTML = `<strong>${agency} ${typ}</strong>` + 
                            `<p><strong>Name:</strong> ${name}` + 
                            `</br><strong>ID:</strong> ${id}`
            popHTML = popHTML + `</br><strong>Elevation:</strong> ${elev}`
            
            // Handle sites with multiple parameters
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
                popHTML = popHTML + `</br><span data-pors="${sdates}||${edates}" id='por' style='margin:0; padding:0;'><strong>POR:</strong> ${dates}</span>`
            
            // Handle sites with single parameters
            } else {
                popHTML = popHTML + `</br><strong>Parameter:</strong> ${param}`
                var sdate = new Date(e.layer.feature.properties.DatasetPORStart);
                var edate = new Date(e.layer.feature.properties.DatasetPOREnd);
                var por = sdate.getFullYear() + ' - ' + edate.getFullYear();
                popHTML = popHTML + `</br><strong>POR:</strong> ${por}`
            };

            // Create links to websites if applicable
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

            // Add a button to add the dataset
            popHTML = popHTML + '<button type="button" onclick="buttonPress()">Add Dataset</button>' + `<p hidden id="ids" style="margin:0">${hiddenID}</p>` ;
            
            var pop = L.popup().setLatLng(e.latlng).setContent(popHTML).addTo(window.map);
            
        });
    });

    // Create popups for watershed layers
    window.hucLayer.on('click', function(e) {

        var coordinates = getCenter(e.layer.feature, e);
        var name = e.layer.feature.properties.NAME;
        var num = e.layer.feature.properties.HUC8;
        var popHTML = "<strong>HUC8: " + num + "</strong><p><strong>Name: <strong>" + name;
        popHTML = popHTML + `</br><select id='param'>`;
        popHTML = popHTML + `<option value='PRISM'>PRISM Temperature & Precipitation</option><option value='NRCC'>NRCC Temperature & Precipitation</option></select></p>`;
        popHTML = popHTML + '<button type="button" onclick="HUCPress()">Add Temp/Precip</button>' + `<p hidden id="hucNum" style="margin:0">${num}</p>` ;
        var pop = L.popup().setLatLng(coordinates).setContent(popHTML).addTo(window.map);

    });

    // Create popups for climate division layer
    window.climLayer.on('click', function(e) {

        var coordinates = getCenter(e.layer.feature, e);
        var name = e.layer.feature.properties.NAME;
        var num = e.layer.feature.properties.CLIMDIV;
        var popHTML = "<strong>NAME: " + name + "</strong><p><strong>Number: <strong>" + num;
        popHTML = popHTML + `</br><select id='param'><option value='PDSI'>Palmer Drought Severity Index</option><option value='SPEI'>Standardized Precipitation Evapotranspiration Index</option></select></p>`;
        popHTML = popHTML + '<button type="button" onclick="PDSIPress()">Add Drought Index</button>' + `<p hidden id="pdsiNum" style="margin:0">${num}</p>` ;
        var pop = L.popup().setLatLng(coordinates).setContent(popHTML).addTo(window.map);

    });
}

function createLayerControlOverlay() {
    // Creates a layer control using the grouped overlay add-on to Leaflet
    
    // Create Grouped Overlays
    var groupedOverlays = {
        "Stations":{
            '<span style="display:inline-block;height:10px;width:10px;border: 1px solid black;border-radius:50%;background:#23ff27"></span>&nbsp;USGS Streamgages':     window.USGSLayer,
            '<span style="display:inline-block;height:10px;width:10px;border: 1px solid black;border-radius:50%;background:#4cffed"></span>&nbsp;NRCS SNOTEL Sites':    window.SNOTELLayer,
            '<span style="display:inline-block;height:10px;width:10px;border: 1px solid black;border-radius:50%;background:#00beff"></span>&nbsp;NRCS Snow Courses':    window.SNOWCOURSELayer,
            '<span style="display:inline-block;height:10px;width:10px;border: 1px solid black;border-radius:50%;background:#ffcc6f"></span>&nbsp;NRCS SCAN Sites':      window.SCANLayer,
            '<span style="display:inline-block;height:10px;width:10px;border: 1px solid black;border-radius:50%;background:#5263fe"></span>&nbsp;USBR Natural Flow':    window.USBRLayer,
            '<span style="display:inline-block;height:10px;width:10px;border: 1px solid black;border-radius:50%;background:#f47251"></span>&nbsp;USBR AgriMet':         window.USBRAGRIMETLayer,
            '<span style="display:inline-block;height:10px;width:10px;border: 1px solid black;border-radius:50%;background:#c0c0c0"></span>&nbsp;NOAA Sites':           window.NCDCLayer,
        },
        "Areas":{
            "Watersheds":           window.hucLayer,
            "Climate Divisions":    window.climLayer
        }
    };

    // Create a layer control overlay with options
    var layer_control_options = {
        exclusiveGroups: ["Areas"],
        groupCheckboxes: false
    };

    L.control.groupedLayers(baseMaps, groupedOverlays, layer_control_options).addTo(window.map);
};

// Function to update the POR in the popup 
// depending on the selected dataset
function updatePOR() {
    var idx = document.getElementById('param').selectedIndex;
    var pors = document.getElementById('por').getAttribute('data-pors');
    var sdates = pors.split('||')[0].split(',');
    var edates = pors.split('||')[1].split(',');
    var y1 = new Date(sdates[idx]);
    var y2 = new Date(edates[idx]);
    var por = y1.getFullYear() + ' - ' + y2.getFullYear();
    document.getElementById('por').innerHTML = `POR: ${por}`;
};

// Function to print a formatted message to the console 
// when users click the 'Add Dataset' button on sites
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

// Function to print a formatted message to the console 
// when users click the 'Add Dataset' button on watersheds
function HUCPress() {
    var id = document.getElementById('hucNum').innerHTML;
    var option  = document.getElementById('param').value;
   
    console.log('HUC:'+id+':PARAM:'+option);
   
}

// Function to print a formatted message to the console 
// when users click the 'Add Dataset' button on climate divisions
function PDSIPress() {
    var id = document.getElementById('pdsiNum').innerHTML;
    var option  = document.getElementById('param').value;
    console.log('PDSI:'+id+':PARAM:'+option);
}

// Function to move the map to the specified location
function moveToMarker(lat, lng) {
    window.map.setView([lat, lng], 12)
}

// Function to let user select HUCS 
function enableHUCSelect() {

    // Make sure the huc layer is active and the PDSI layer is not
    window.map.removeLayer(window.climLayer);
    window.map.addLayer(window.hucLayer);


    // Create a list to store selected HUCS
    window.hucList = [];

    // Reset the HUC style
    window.hucLayer.setStyle({
        color: '#4286f4',
        fillOpacity: 0,
        weight: 1,
        opacity: 0.8, 
    });
    window.hucLayer.off("click");
    window.hucLayer.eachLayer(function(layer) {

        // turn off the default interaction
        layer.off("mouseout");
        layer.off("mouseover");
        layer.off("click");

        layer.on("click", function(e) {

            // get the selected HUC
            var HUC = layer.feature.properties.HUC8;

            // check if the HUC is already in the list
            if (window.hucList.includes(HUC)) {

                // Remove the HUC from the list
                var idx = window.hucList.indexOf(HUC);
                window.hucList.splice(idx,1);

                // Reset the layer style
                window.hucLayer.resetStyle(e.target)

            } else {

                // Add the HUC to the hucList
                window.hucList.push(HUC);

                // Shade in the HUC to show it's selected
                layer.setStyle({
                    fillColor: '#0080ff',
                    weight: 2,
                    fillOpacity: 0.4
                })
            }
        });
    });
};

// Function to return a list of HUCs to the application and 
function getSelectedHUCs() {

    // Reset the HUC Layers style and interaction elements
    window.hucLayer.setStyle( {
        color: '#4286f4',
            fillOpacity: 0,
            weight: 1,
            opacity: 0.8, 
    });

    window.hucLayer.eachLayer(function(layer) {
        layer.on("mouseover", function(e) {
            e.target.setStyle({
                color:"#4872ff",
                weight:3,
                opacity: .8,
            });
        });
        layer.on("mouseout", function(e){
            window.hucLayer.resetStyle(e.target);
        });
        layer.off("click");
        layer.on("click", function(e){
            var coordinates = getCenter(layer.feature, e);
            var name = layer.feature.properties.NAME;
            var num = layer.feature.properties.HUC8;
            var popHTML = "<strong>HUC8: " + num + "</strong><p><strong>Name: <strong>" + name;
            popHTML = popHTML + `</br><select id='param'>`;
            popHTML = popHTML + `<option value='PRISM'>PRISM Temperature & Precipitation</option><option value='NRCC'>NRCC Temperature & Precipitation</option></select></p>`;
            popHTML = popHTML + '<button type="button" onclick="HUCPress()">Add Temp/Precip</button>' + `<p hidden id="hucNum" style="margin:0">${num}</p>` ;
            var pop = L.popup().setLatLng(coordinates).setContent(popHTML).addTo(window.map);
        })
    
    });
    
    

    // Return the HUC List
    return window.hucList;

};

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
        window.hucLayer.setStyle(e.layer.feature.id, {
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

// Function to load local JSON file
function loadJSON(filename, callback) {   

    var xobj = new XMLHttpRequest();
    xobj.overrideMimeType("application/json");
    xobj.open('GET', filename, false); // Replace 'my_data' with the path to your file
    xobj.onreadystatechange = function () {
          if (xobj.status == "0") {
            // Required use of an anonymous callback as .open will NOT return a value but simply returns undefined in asynchronous mode
            callback(xobj.responseText);
          }
    };
    xobj.send(null);  
};

