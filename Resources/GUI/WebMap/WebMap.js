//
// Script Name:     mapbox.js
// Script Author:   Kevin Foley, Civil Engineer, Reclamation
// Last Modified:   Apr 4, 2018
//
// Description:     'mapbox.js' is the javascript portion of a web map application used
//                  to select stations and datasets in the PyForecast application. This
//                  script uses the MapboxGL javascript API to map GeoJSON files located
//                  in the GIS folder

///////////////// DEFINE STARTUP VARIABLES /////////////////////////////////
// This section defines all the variables that are called when the webpage
// initially loads. These variables are available to the javascript as
// global variables (with the 'window' handle) throughout the session

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
    layers: [grayMap]}).setView([ 43, -113], 6); // Set up a map centered on the U.S. at zoom level 4

// Store the basemaps in a dict
var baseMaps = {'Grayscale': grayMap,
                'Terrain': terrainMap, 
                'Streets': streetMap};

// Create map panes
map.createPane("HUCPane")
map.createPane("PointsPane")


// Load the local JSON files
var HUC8 = new Object();
var USGS = new Object();
var SNOTEL = new Object();
var SNOWCOURSE = new Object();
var USBR_POLY = new Object();
var USBR_POINTS = new Object();

loadJSON('../../Resources/GIS/WATERSHEDS/HUC8_WGS84.json', function(response) {
    // Parse data into object
    window.HUC8 = JSON.parse(response);
});
loadJSON('../../Resources/GIS/USGS_SITES/STREAMGAGES.json', function(response) {
    // Parse data into object
    window.USGS = JSON.parse(response);
});
loadJSON('../../Resources/GIS/NRCS_SITES/SNOTEL.json', function(response) {
    // Parse data into object
    window.SNOTEL = JSON.parse(response);
});
loadJSON('../../Resources/GIS/NRCS_SITES/SNOWCOURSE.json', function(response) {
    // Parse data into object
    window.SNOWCOURSE = JSON.parse(response);
});
loadJSON('../../Resources/GIS/RECLAMATION_SITES/RESERVOIRS2.json', function(response) {
    // Parse data into object
    window.USBR_POINTS = JSON.parse(response);
});



// Add the USGS Sites
var USGSLayer = L.geoJSON( window.USGS, {

    pointToLayer: function (feature, latlng) {
        return L.circleMarker(latlng, {
            pane: "PointsPane",
            fillColor: "#23ff27",
            color: "#000000",
            weight: 1,
            radius: 7,
            fillOpacity: 1
            })
        },
    }).addTo(map);

// Add the SNOTEL sites
var SNOTELLayer = L.geoJSON( window.SNOTEL, {
    pointToLayer: function (feature, latlng) {
        return L.circleMarker(latlng, {
            pane: "PointsPane",
            fillColor: "#4cffed",
            color: "#000000",
            radius: 7,
            weight: 1,
            fillOpacity: 1
            })
        }
    }).addTo(map);

// Add the SnowCourse Sites
var SNOWCOURSELayer = L.geoJSON( window.SNOWCOURSE, {
    
    pointToLayer: function (feature, latlng) {
        return L.circleMarker(latlng, {
            pane: "PointsPane",
            fillColor: "#00beff",
            color: "#000000",
            weight:1,
            radius: 7,
            fillOpacity: 1
            })
        }
    }).addTo(map);  

// Add the USBR sites
var USBR_POINTSLayer = L.geoJSON( window.USBR_POINTS, {
    
    pointToLayer: function (feature, latlng) {
        return L.circleMarker(latlng, {
            pane: "PointsPane",
            fillColor: "#2268ff",
            color: "#000000",
            radius: 7,
            weight:1,
            fillOpacity: 1
            })
        }
    }).addTo(map);  

// Add the popups for the USGS sites
USGSLayer.on("click",function(e) {
    var id = e.layer.feature.properties.site_no;
    var name = e.layer.feature.properties.station_nm;
    var huc = ("0" + e.layer.feature.properties.huc_cd).slice(-8);
    var elev = e.layer.feature.properties.alt_va;
    var por = e.layer.feature.properties.begin_date;
    var url = "https://waterdata.usgs.gov/nwis/inventory/?site_no="+id;
    var popHTML = "<strong>USGS Streamgage Site</strong>" + 
                  "<p>ID: " + id +
                  "</br>Name: " + name +
                  "</br>HUC8: " + huc + 
                  "</br>Elevation: " + elev + 
                  "</br>POR: " + por + 
                  "</br><a href = " + url + ">Website" + 
                  '</a></p><button type="button" onclick="buttonPress()">Add Site</button>' + 
                  '<p hidden id="info" style="margin:0">USGS|'+id+'|'+name+'|Streamflow</p>';
    var pop = L.popup().setLatLng(e.latlng).setContent(popHTML).addTo(map);

});

// Add the popups for the SNOTEL sites
SNOTELLayer.on("click",function(e) {
    var id = e.layer.feature.properties.ID;
    var name = e.layer.feature.properties.Name;
    var huc = ("0" + e.layer.feature.properties.HUC).slice(-8);
    var elev = e.layer.feature.properties.Elevation_ft;
    var por = e.layer.feature.properties.POR_START;
    if (window.soilSites.indexOf(parseInt(id)) > -1) {
        option3 = '<option value="SOIL">Soil Moisture</option>'
    } else {
        option3 = "";
    };
    var url = "https://wcc.sc.egov.usda.gov/nwcc/site?sitenum="+id;
    var popHTML = "<strong>NRCS SNOTEL Site</strong>" + 
                  "<p>ID: " + id +
                  "</br>Name: " + name +
                  "</br>HUC8: " + huc + 
                  "</br>Elevation: " + elev + 
                  "</br>POR: " + por + 
                  "</br><a href = " + url + ">Website" + 
                  '</a></p>' + 
                  '<select id="param"><option value="SWE">SWE (in)</option><option value="Precip">Precip (in)</option>' + option3 + '</select>' +
                  '<button type="button" onclick="buttonPress()">Add Site</button>' + 
                  '<p hidden id="info" style="margin:0">SNOTEL|'+id+'|'+name+'</p>';
    var pop = L.popup().setLatLng(e.latlng).setContent(popHTML).addTo(map);

});

// Add the popups for the SNOWCOURSE sites
SNOWCOURSELayer.on("click",function(e) {
    var id = e.layer.feature.properties.ID;
    var name = e.layer.feature.properties.Name;
    var huc = ("0" + e.layer.feature.properties.HUC).slice(-8);
    var elev = e.layer.feature.properties.Elevation_ft;
    var por = e.layer.feature.properties.POR_START;
    var popHTML = "<strong>NRCS Snow Course Site</strong>" + 
                  "<p>ID: " + id +
                  "</br>Name: " + name +
                  "</br>HUC8: " + huc + 
                  "</br>Elevation: " + elev + 
                  "</br>POR: " + por +  
                  '</p><button type="button" onclick="buttonPress()">Add Site</button>' + 
                  '<p hidden id="info" style="margin:0">SNOWCOURSE|'+id+'|'+name+'|SWE_SnowCourse</p>';
    var pop = L.popup().setLatLng(e.latlng).setContent(popHTML).addTo(map)

});

// Add the popups for the USBR sites
USBR_POINTSLayer.on("click",function(e) {
    var id = e.layer.feature.properties.USBR_ID;
    var name = e.layer.feature.properties.NAME;
    var elev = e.layer.feature.properties.MeanElevation;
    var huc = e.layer.feature.properties.HUC_CODE;
    var region = e.layer.feature.properties.REGION;
    var pcode = e.layer.feature.properties.PCODE;
    var popHTML = "<strong>USBR Reservoir Site</strong>" + 
                  "<p>ID: " + id +
                  "</br>Name: " + name +
                  "</br>Elevation: " + Math.round(elev) +
                  "</br>HUC: " + huc +
                  "</br>Region: " + region +
                  '</p><button type="button" onclick="buttonPress()">Add Site</button>' + 
                  '<p hidden id="info" style="margin:0">USBR|'+id+'|'+name+'|Inflow|' + region + '|' + pcode + '</p>';
    var pop = L.popup().setLatLng(e.latlng).setContent(popHTML).addTo(map)

});

// Load the map with all the HUCs, streamgages, SNOTEL sites, SNOW Courses, and USBR sites
var HUCLayer = L.geoJSON( window.HUC8, {
    style: {pane: "HUCPane",
            fillColor: "#4286f4",
            weight: 1,
            opacity: .8, 
            color: "#4286f4", 
            fillOpacity: 0.0},
    onEachFeature: window.onHUCFeatures}).addTo(map);


// Add interactivity to the HUC boundaries
function onHUCFeatures( feature, layer ) {
    layer.on({
        mouseover: highlightHUC,
        mouseout: resetHighlightHUC,
        click: clickHUC
    });
};

function highlightHUC(e) {
    var layer = e.target;
    layer.setStyle({
        color:"#0000ff",
        weight:3
    });
};

function resetHighlightHUC(e) {
    window.HUCLayer.resetStyle(e.target);
};

function clickHUC(e) {
    var coordinates = getCenter(e.target.feature);
    var name = e.target.feature.properties.NAME;
    var num = e.target.feature.properties.HUC8;
    var popHTML = "<strong>HUC8: " + num + "</strong><p>Name: " + name + "</p>"
    var pop = L.popup().setLatLng(coordinates).setContent(popHTML).addTo(map);
};

var dataLayers = {
    "Watersheds":HUCLayer,
    "Streamgages":USGSLayer,
    "SNOTEL Sites":SNOTELLayer,
    "Snow Course" :SNOWCOURSELayer,
    "Reservoirs":USBR_POINTSLayer
}

// Add a basemap and layer selector
L.control.layers(baseMaps, dataLayers).addTo(map);

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

// Function to send the site to the site list if the user selects it
function buttonPress() {
    var infoString = document.getElementById('info').innerHTML;
    var infoList = infoString.split('|');
    var type = infoList[0];
    if (type == 'SNOTEL') {
        var num = infoList[1];
        var name = infoList[2];
        var param = document.getElementById('param').value;
        console.log('StationSelect|'+name+'|'+num+'|'+type+'|'+param);
    } else if (type == 'USBR') {
        var num = infoList[1];
        var name = infoList[2];
        var param = infoList[3];
        var region = infoList[4];
        var pcode = infoList[5];
        console.log('StationSelect|'+name+'|'+num+'|'+type+'|'+param+'|'+region+'|'+pcode);
    } else {
        var num = infoList[1];
        var name = infoList[2];
        var param = infoList[3]
        console.log('StationSelect|'+name+'|'+num+'|'+type+'|'+param);
    };
    
};

// Function to find center of polygon
function getCenter(feat) {
    lats = 0;
    longs = 0;
    for (i = 0; i < feat.geometry.coordinates[0].length; i++) {
        lats += feat.geometry.coordinates[0][i][1];
        longs += feat.geometry.coordinates[0][i][0];
    };
    meanLat = lats / feat.geometry.coordinates[0].length;
    meanLong = longs / feat.geometry.coordinates[0].length;
    coords = [meanLat, meanLong];
    return coords;
};