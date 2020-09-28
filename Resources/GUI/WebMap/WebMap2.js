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

//window.legend = false;



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
                fillColor: "#f5edd0",
                color: "#000000",
                weight: 1,
                radius: 7,
                fillOpacity: 1
            })
        }
    });
    window.layer_group.addLayer(window.NCDCLayer);
    var arr = ["NCDC", "SNOTEL", "SCAN", "AGRIMET", "RESERVOIR", "STREAMGAGE", "SNOWCOURSE"]
    window.otherLayer = L.geoJSON(point_data, {
        
        filter: function(feature) {
            if (arr.includes(feature.properties.DatasetType)) {return false} else {return true};
        },
        pointToLayer: function (feature, latlng) {
            return L.circleMarker(latlng, {
                pane: "PointsPane",
                fillColor: "#aaaaaa",
                color: "#000000",
                weight: 1,
                radius: 7,
                fillOpacity: 1
            })
        }

    });
    window.layer_group.addLayer(window.otherLayer);

    // Create Popups for point and area datasets
    createPopups();

    // Create the layer control
    createLayerControlOverlay();
}

// Creates Popup windows when users click on circle markers and
// area polygons. Creates the 'add dataset' buttons
function createPopups() {
    var colorDict = {"STREAMGAGE":"#23ff27",
                    "SNOTEL":"#4cffed",
                    "SNOWCOURSE":"#00beff",
                    "SCAN":"#ffcc6f",
                    "RESERVOIR":"#5263fe",
                    "AGRIMET":"#f47251",
                    "NCDC":"#f5edd0"}
    window.hucDict = {};

    window.hucLayer.eachLayer( function(sublayer) {
        var huc = sublayer.feature.properties.HUC8;
        if (window.hucDict[huc] == undefined) {
            window.hucDict[huc] = new Object;
            window.hucDict[huc].ids = Array();
            window.hucDict[huc].colors = Array();
            window.hucDict[huc].names = Array();
            window.hucDict[huc].ids.push('PRISM');
            window.hucDict[huc].names.push('PRISM Temperature & Precipitation');
            window.hucDict[huc].colors.push("#a83273");
        }   
    })
    
    // Iterate over the layers in the 'layer_group'
    window.layer_group.eachLayer(function (layer) {

        layer.eachLayer( function(sublayer){
            var huc = sublayer.feature.properties.DatasetHUC8;
            var type = sublayer.feature.properties.DatasetType;
            var hiddenID = String(sublayer.feature.properties.DatasetInternalID);
            var name = sublayer.feature.properties.DatasetName;
            var param = sublayer.feature.properties.DatasetParameter;

            if (window.hucDict[huc] == undefined) {
                window.hucDict[huc] = new Object;
                window.hucDict[huc].ids = Array();
                window.hucDict[huc].names = Array();
                window.hucDict[huc].colors = Array();
                window.hucDict[huc].ids.push('PRISM');
                window.hucDict[huc].names.push('PRISM Temperature & Precipitation');
                window.hucDict[huc].colors.push("#a83273");
            }   

            if (hiddenID.includes("|")){
                var hiddenIDs = hiddenID.split('|');
                var params = param.split('|');
                hiddenIDs.forEach(function(id, idx){
                    window.hucDict[huc].ids.push(id);
                    if (colorDict.hasOwnProperty(type)){
                        window.hucDict[huc].colors.push(colorDict[type]);
                    } else {
                        window.hucDict[huc].colors.push("#AAAAAA");
                    }
                    
                    if (name.length > 15) {var name2 = name.substr(0,15)+'...'} else {var name2 = name};
                    if (params[idx].length > 10) {var param2 = params[idx].substr(0,10) + '...'} else {var param2 = params[idx]};
    
                    window.hucDict[huc].names.push('[' +name2 + ']' + param2)
                })
            } else {
                window.hucDict[huc].ids.push(hiddenID);
                if (colorDict.hasOwnProperty(type)){
                    window.hucDict[huc].colors.push(colorDict[type]);
                } else {
                    window.hucDict[huc].colors.push("#AAAAAA");
                }
                if (name.length > 15) {var name2 = name.substr(0,15)+'...'} else {var name2 = name};
                if (param.length > 10) {var param2 = param.substr(0,10) + '...'} else {var param2 = param};
    
                window.hucDict[huc].names.push('[' +name2 + ']' + param2)
            }
           

        })
        // For each layer, create a tooltip
        layer.on("mouseover", function(e) {
            //console.log(e.layer.feature.properties.DatasetName);
            e.layer.unbindTooltip();
            e.layer.bindTooltip(e.layer.feature.properties.DatasetName).openTooltip();
        })
        
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
            
            window.pop = L.popup().setLatLng(e.latlng).setContent(popHTML).addTo(window.map);
            
        });
    });

    // Create popups for watershed layers
    window.hucLayer.on('click', function(e) {

        //Try to do drop down checkboxes
        var coordinates = getCenter(e.layer.feature, e);
        var name = e.layer.feature.properties.NAME;
        var num = e.layer.feature.properties.HUC8;
        window.num = num;

        // get a list of all the datasets in this huc

        var popHTML = "<strong>HUC8: " + num + "</strong><p><strong>Name: <strong>" + name;

        
        popHTML = popHTML + `</p><div id="list1_HUC" class="dropdown-check-list" tabindex="100">
            <span class="anchor_HUC" style="background:#eaeaea; color: black">Select Datasets</span>
            <ul id="items_HUC" class="items_HUC visible" style="background: #cacaca">
            `
        popHTML = popHTML + `<li><label style="color: black; font-family: 'Open Sans'; font-weight: bold"><input class="HUC_SELECT" type="checkbox" id="SELECT_ALL" onchange="hucSelectAll()"/>Select All</label></li>`
        window.hucDict[num].ids.forEach(function(id, idx){
            color = window.hucDict[num].colors[idx];
            popHTML = popHTML + `<li><label style="color: black; font-family: monospace"><input class="HUC_SELECT" type="checkbox" id="` + id + `" /><span style="display:inline-block;height:10px;width:10px;border: 1px solid black;border-radius:50%;background:` + color + `"></span>` + window.hucDict[num].names[idx] +`</label></li>`
        });
        popHTML = popHTML + `</ul></div></br>`;

        //popHTML = popHTML + `</br><select id='param'>`;
        //popHTML = popHTML + `<option value='PRISM'>PRISM Temperature & Precipitation</option><option value='NRCC'>NRCC Temperature & Precipitation</option></select></p>`;
        popHTML = popHTML + '<button type="button" onclick="HUCPress()">Add Datasets</button>' ;
        window.pop = L.popup().setLatLng(coordinates).setContent(popHTML).addTo(window.map);

        var checkList = document.getElementById('list1_HUC');
        var items = document.getElementById('items_HUC');
                checkList.getElementsByClassName('anchor_HUC')[0].onclick = function (evt) {
                    if (items.classList.contains('visible')){
                        items.classList.remove('visible');
                        items.style.display = "none";
                    }
                    
                    else{
                        items.classList.add('visible');
                        items.style.display = "block";
                    }
                    
                    
                }

                items.onblur = function(evt) {
                    items.classList.remove('visible');
                }

        
    });

    // Create popups for climate division layer
    window.climLayer.on('click', function(e) {

        var coordinates = getCenter(e.layer.feature, e);
        var name = e.layer.feature.properties.NAME;
        var num = e.layer.feature.properties.CLIMDIV;
        var popHTML = "<strong>NAME: " + name + "</strong><p><strong>Number: <strong>" + num;
        popHTML = popHTML + `</br><select id='param'><option value='PDSI'>Palmer Drought Severity Index</option><option value='SPEI'>Standardized Precipitation Evapotranspiration Index</option></select></p>`;
        popHTML = popHTML + '<button type="button" onclick="PDSIPress()">Add Drought Index</button>' + `<p hidden id="pdsiNum" style="margin:0">${num}</p>` ;
        window.pop = L.popup().setLatLng(coordinates).setContent(popHTML).addTo(window.map);
        
    });
}

function hucSelectAll(){
    var selectAllBox = document.getElementById("SELECT_ALL");
    if (selectAllBox.checked) {
        var items = document.getElementsByClassName("HUC_SELECT");
        for(i=0; i<items.length; i++){
            if (items[i].id != 'SELECT_ALL'){
                items[i].checked = true;
            }
        }
    } else {
        var items = document.getElementsByClassName("HUC_SELECT");
        for(i=0; i<items.length; i++){
            if (items[i].id != 'SELECT_ALL'){
                items[i].checked = false;
            }
        }
    }
}

function createLayerControlOverlay() {
    // Creates a layer control using the grouped overlay add-on to Leaflet
    window.NEXRADLayer =  new L.tileLayer.wms("http://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi", {
            layers: 'nexrad-n0r',
            format: 'image/png',
            opacity: 0.8,
            transparent: true,
            attribution: "Weather data &copy; 2015 IEM Nexrad"
            });
    SWE_URL = "https://climate.arizona.edu/Maps/SNODAS_SWE_a/{yr}_{mo}_{dy}_SNODAS_SWE_a/{z}/{x}/{y}.png";
    dt = new Date();
    dt = new Date(dt - 7*60*60*1000);
    var yr = dt.getFullYear().toString();
    var mo = (dt.getMonth()+1).toString();
    var dy = dt.getDate().toString();
    if (mo.length < 2) {mo = "0" + mo;}
    if (dy.length < 2) {dy = "0" + dy;}
    SWE_URL = SWE_URL.replace('{yr}',yr).replace('{mo}',mo).replace('{dy}',dy)
    window.SWELayer = L.tileLayer.wms(SWE_URL, {
        format: 'image/png',
        transparent: true,
        opacity: 0.8,
        attribution: 'Map data from the <a target="_blank" rel="noreferrer" href="https://www.nohrsc.noaa.gov/">National Operational Hydrologic Remote Sensing Center</a>.  Tiles created by <a target="_blank" rel="noreferrer" href="mailto:broxtopd@email.arizona.edu>Patrick Broxton"</a>.'
    });
    window.QPFLayer7Day = L.esri.featureLayer({
        url:"https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Forecasts_Guidance_Warnings/wpc_qpf/MapServer/11",
    });
    window.QPFLayer6Hour = L.esri.featureLayer({
        url:"https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Forecasts_Guidance_Warnings/wpc_qpf/MapServer/7",
        opacity: 1
    });
    window.QPFLayer3Day = L.esri.featureLayer({
        url:"https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Forecasts_Guidance_Warnings/wpc_qpf/MapServer/9",
    });

   

    window.emptyLayer = L.tileLayer("").addTo(window.map);
    window.hucNone = L.tileLayer("");
    

    window.QPFLayer7Day.setStyle(QPFStyle);
    window.QPFLayer6Hour.setStyle(QPFStyle);
    window.QPFLayer3Day.setStyle(QPFStyle);
    

    // Events
    window.NEXRADLayer.on('load', function(){
        addLegend(window.NEXRADLayer);
    })
    window.SWELayer.on('load', function(){
        addLegend(window.SWELayer);
    })
    window.QPFLayer3Day.on("load", function() {
        addLegend(window.QPFLayer3Day);
        reorderLayer(window.QPFLayer3Day);
        window.QPFLayer3Day.eachFeature(function(sublayer){
            sublayer.on("mouseover", function(e){
                var val = sublayer.feature.properties.qpf;
                var infoIcon = document.getElementById("legend_"+val);
                infoIcon.style.boxShadow = "inset 0 0 0px 5px rgb(0,0,0)"
            });
            sublayer.on("mouseout", function(e){
                var val = sublayer.feature.properties.qpf;
                var infoIcon = document.getElementById("legend_"+val);
                infoIcon.style.boxShadow = "inset 0 0 0px 1px rgb(37,37,37)"
            });
          
        })
    });
    window.QPFLayer7Day.on("load", function() {
        addLegend(window.QPFLayer7Day);
        reorderLayer(window.QPFLayer7Day);
        window.QPFLayer7Day.eachFeature(function(sublayer){
            sublayer.on("mouseover", function(e){
                var val = sublayer.feature.properties.qpf;
                var infoIcon = document.getElementById("legend_"+val);
                infoIcon.style.boxShadow = "inset 0 0 0px 5px rgb(0,0,0)"
            });
            sublayer.on("mouseout", function(e){
                var val = sublayer.feature.properties.qpf;
                var infoIcon = document.getElementById("legend_"+val);
                infoIcon.style.boxShadow = "inset 0 0 0px 1px rgb(37,37,37)"
            });
          
        })
        
    });
    window.QPFLayer6Hour.on("load", function() {
        addLegend(window.QPFLayer6Hour);
        reorderLayer(window.QPFLayer6Hour);
        window.QPFLayer6Hour.eachFeature(function(sublayer){
            sublayer.on("mouseover", function(e){
                var val = sublayer.feature.properties.qpf;
                var infoIcon = document.getElementById("legend_"+val);
                infoIcon.style.boxShadow = "inset 0 0 0px 5px rgb(0,0,0)"
            });
            sublayer.on("mouseout", function(e){
                var val = sublayer.feature.properties.qpf;
                var infoIcon = document.getElementById("legend_"+val);
                infoIcon.style.boxShadow = "inset 0 0 0px 1px rgb(37,37,37)"
            });
          
        })
        
    });
    window.emptyLayer.on("load", function() {
        addLegend(window.emptyLayer);
        
    })


    



    // Create Grouped Overlays
    var groupedOverlays = {
        "Stations":{
            '<span style="display:inline-block;height:10px;width:10px;border: 1px solid black;border-radius:50%;background:#23ff27"></span>&nbsp;USGS Streamgages':     window.USGSLayer,
            '<span style="display:inline-block;height:10px;width:10px;border: 1px solid black;border-radius:50%;background:#4cffed"></span>&nbsp;NRCS SNOTEL Sites':    window.SNOTELLayer,
            '<span style="display:inline-block;height:10px;width:10px;border: 1px solid black;border-radius:50%;background:#00beff"></span>&nbsp;NRCS Snow Courses':    window.SNOWCOURSELayer,
            '<span style="display:inline-block;height:10px;width:10px;border: 1px solid black;border-radius:50%;background:#ffcc6f"></span>&nbsp;NRCS SCAN Sites':      window.SCANLayer,
            '<span style="display:inline-block;height:10px;width:10px;border: 1px solid black;border-radius:50%;background:#5263fe"></span>&nbsp;USBR Natural Flow':    window.USBRLayer,
            '<span style="display:inline-block;height:10px;width:10px;border: 1px solid black;border-radius:50%;background:#f47251"></span>&nbsp;USBR AgriMet':         window.USBRAGRIMETLayer,
            '<span style="display:inline-block;height:10px;width:10px;border: 1px solid black;border-radius:50%;background:#f5edd0"></span>&nbsp;NOAA Sites':           window.NCDCLayer,
            '<span style="display:inline-block;height:10px;width:10px;border: 1px solid black;border-radius:50%;background:#AAAAAA"></span>&nbsp;OTHER':                window.otherLayer,
        },
        "Areas":{
            "Watersheds":           window.hucLayer,
            "Climate Divisions":    window.climLayer,
            "None":                 window.hucNone
        },
        "Current Weather":{
            "None": window.emptyLayer,
            "NEXRAD Radar": window.NEXRADLayer,
            "SNODAS SWE": window.SWELayer,
            "QPF (6-hour)": window.QPFLayer6Hour,
            "QPF (3-Day)": window.QPFLayer3Day,
            "QPF (7-Day)": window.QPFLayer7Day,
        }
    };

    // Create a layer control overlay with options
    var layer_control_options = {
        exclusiveGroups: ["Areas", 'Current Weather'],
        groupCheckboxes: true
    };

    L.control.groupedLayers(baseMaps, groupedOverlays, layer_control_options).addTo(window.map);
};


function reorderLayer(layer) {
    // Reorders the QPF layer so the the 
    // higher precip values are always on top
    var sublayers = Array();
    layer.eachFeature(function(sublayer){
        sublayers.push(sublayer);
    });
    sublayers.sort(function(a,b){
        return a.feature.properties.qpf - b.feature.properties.qpf;
    });
    sublayers.forEach(function(sublayer){
        sublayer.bringToFront();
        //layer.resetStyle(feature.id)
        //layer.setFeatureStyle(feature.id, QPFStyle);
    });
    //layer.resetStyle();
    //;


}

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
    };
    // close the popup
    window.pop._close();
};

// Function to print a formatted message to the console 
// when users click the 'Add Dataset' button on watersheds
function HUCPress() {

    //iterate over the checked boxes
    var datasetList = Array();
    var parameterList = document.getElementsByClassName("HUC_SELECT");
    for (i=0; i<parameterList.length; i++) {
        item = parameterList[i];
        if (item.checked){
            if (item.id != "SELECT_ALL"){
            datasetList.push(item.id);
            }
        }
    }
    datasetList.forEach(function(dataset){
        if (dataset == 'PRISM') {
            console.log("HUC:" + window.num + ":PARAM:" + dataset);
        } else {
            console.log("ID:" + dataset)
        }
    })

    // close the popup
    window.pop._close();
}

// Function to print a formatted message to the console 
// when users click the 'Add Dataset' button on climate divisions
function PDSIPress() {
    var id = document.getElementById('pdsiNum').innerHTML;
    var option  = document.getElementById('param').value;
    console.log('PDSI:'+id+':PARAM:'+option);
    // close the popup
    window.pop._close();
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

var NEXRADMap = {
    levels: [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75],
    colors: ["#646464", "#04e9e7",  "#019ff4", "#0300f4", "#02fd02", "#01c501", "#008e00", "#fdf802", "#e5bc00", "#fd9500", "#fd0000", "#d40000", "#bc0000", "#f800fd", "#9854c6", "#fdfdfd" ]
};

var QPFMap = {
    levels: [0, 0.01, .1, .25, .5, .75, 1, 1.25, 1.5, 1.75, 2, 2.5, 3, 4, 5, 7, 10, 15, 20],
    colors: ["#FFFFFF", '#7fff00', "#00ff00", "#088b00", "#104e8b", "#1e90ff", "#00b2ee", "#00eeee", "#8968cd", "#912cee", "#8b008b", "#8b0000", "#ff0000", "#ee4000", "#ff7f00", "#ce8500", "#ffd700", "#ffff00", "#ffc0b7"]
};

var SNODASMap = {
    levels: [0.0, 0.01, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 7.5, 10.0, 20.0, 40.0],
    colors: ['#ffffff', '#f7fdfd', '#dbfffb', '#bfd0f6', '#6167bc', '#5b40b7', '#731cc1', '#af2dd4', '#e24fdb', '#ef70c2', '#e99eba', '#fae3dd']
};

function highlightLegend(){
    return
}

function addLegend(layer) {
    // Adds a legend for the overlay raster layer

    // Check if empty layer
    if (layer == window.emptyLayer) {
        L.DomUtil.remove(window.divElem);
        window.map.removeControl(window.legend);
        return
    }

    
    // Delete any old legends
    if (typeof window.legend != "undefined") {
        L.DomUtil.remove(window.divElem);
        window.map.removeControl(window.legend);
    }
    window.legend = L.control({position: 'bottomright'});
    window.divElem = L.DomUtil.create('div', 'info legend');
    

    window.legend.onAdd = function(map) {
        // Get the color map
        if ([window.QPFLayer3Day, window.QPFLayer6Hour, window.QPFLayer7Day].includes(layer)) {
            cmap = window.QPFMap;
            title = 'Accumulated Precip (inches)';
        } else if (layer == window.SWELayer) {
            cmap = window.SNODASMap;
            title = 'Snow Water Equiv. (inches)';
        } else {
            cmap = window.NEXRADMap;
            title = 'Base Reflectivity (dBz)';
        };
        // Create the legend
        
        
        labels = ['<strong style="font-family: Open Sans, Arial">'+title+"</strong><br>"];
        categories = cmap.levels;
        colors = cmap.colors;

        for (var i=0; i < categories.length; i++) {
            labels.push(
                '<h5>'+padCenter(categories[i].toString(), 5, '&nbsp;')+'</h5>'
            );
            }
        labels.push('<br>');
        for (var i=0; i < categories.length; i++) {
            labels.push(
                '<i id="legend_' + categories[i] + '" style="background:' + colors[i] + '"></i>'
            );
        }

        window.divElem.innerHTML = labels.join("");
        return window.divElem;
    }

    
    window.legend.addTo(window.map);
}

function padCenter(string, length, char) {
    var padCharsLeft = Array(1 + string.length + Math.floor((length - string.length) / 2)).join('@');
    var padCharsRight =  Array(length+1).join('@');
    string = pad(padCharsLeft, string, true);
    string = pad(padCharsRight, string, false);
    //string =  string.padStart(string.length + Math.floor((length - string.length) / 2), '@').padEnd(length, '@');
    return string.replace(/@/g, char);
}

function pad(pad, str, padLeft) {
    if (typeof str === 'undefined') 
      return pad;
    if (padLeft) {
      return (pad + str).slice(-pad.length);
    } else {
      return (str + pad).substring(0, pad.length);
    }
  }

function QPFStyle(feature){
    switch(feature.properties.qpf) {
        case 20:
          color1 = "#ffc0b7";
          width1 = 0;
          break;
        case 15:
          color1 = "#ffff00";
          width1 = 0;
          break;
        case 10:
          color1 = "#ffd700";
          width1 = 0;
          break;
        case 7:
          color1 = "#ce8500";
          width1 = 0;
          break;
        case 5:
          color1 = "#ff7f00";
          width1 = 0;
          break;
        case 4:
            color1 = "#ee4000";
            width1 = 0;
            break;
        case 3:
          color1 = "#ff0000";
          width1 = 0;
          break;
        case 2.5:
          color1 = "#8b0000";
          width1 = 0;
          break;
          case 2:
          color1 = "#8b008b";
          width1 = 0;
          break;
          case 1.75:
          color1 = "#912cee";
          width1 = 0;
          break;
          case 1.5:
          color1 = "#8968cd";
          width1 = 0;
          break;
          case 1.25:
          color1 = "#00eeee";
          width1 = 0;
          break;
          case 1:
          color1 = "#00b2ee";
          width1 = 0;
          break;
          case 0.75:
          color1 = "#1e90ff";
          width1 = 0;
          break;
          case 0.5:
          color1 = "#104e8b";
          width1 = 0;
          break;
          case 0.25:
          color1 = "#088b00";
          width1 = 0;
          break;
          case 0.1:
          color1 = "#00ff00";
          width1 = 0;
          break;
          case 0.01:
          color1 = "#7fff00";
          width1 = 0;
          break;


        default:
            color1 = "#00FF00";
            width1 = 0;
            break;
      }
    return {
      fillColor: color1,
      width: 1,
      fillOpacity: 0.63,
      stroke: false,
    };};