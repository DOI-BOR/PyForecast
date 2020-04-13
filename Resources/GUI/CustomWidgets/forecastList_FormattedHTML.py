from PyQt5 import QtWidgets, QtCore, QtGui
FF = """<style>
div {
border: 1px solid red;
color: #003E51;
margin: 0px;
padding: 0px;
font-family: 'Open Sans', Arial, sans-serif, monospace;
font-size: 17px;
}
td img{
    display: block;
    margin-left: auto;
    margin-right: auto;
    border: 1px solid blue;

}
</style>

<div>


<table border="0">
	<tr >
	<td>
    <img style=" border:0px solid blue" src="resources/GraphicalResources/icons/high.png" width="24" height="24"/>
    </td>
	<td><p style="color: #007396; font-size: 20px"><strong style="color: #007396; font-size: 20px">800 KAF </strong>(100 KAF - 1200 KAF)</p></td>
	</tr>
	<tr>
	<td>
    <img src="resources/GraphicalResources/icons/flag_checkered-24px.svg" width="24" height="24"/>
	</td>
	<td><p style="vertical-align: middle"><strong>R<sup>2</sup>:</strong> 0.54</p></td>
	</tr>
    <tr>
	<td>
    <img src="resources/GraphicalResources/icons/target-24px.svg" width="24" height="24"/>
	</td>
	<td><p style="vertical-align: middle">Buffalo Bill April 01 - July 31 Inflow</p></td>
	</tr>
    <tr >
	<td >
    <img src="resources/GraphicalResources/icons/bullseye-24px.svg" width="24" height="24"/>
	</td>
	<td ><p style="vertical-align: middle">PDSI, Antecedent Flow, SNOTEL, SST</p></td>
	</tr>

</table>


</div>"""
HTML_FORMAT = """
<style>
p {{
color: #003E51;
vertical-align: center;
line-height: 18px;
margin: 0px;
padding: 0px;
margin-left: 1em;
font-family: 'Open Sans', Arial, sans-serif, monospace;
font-size: 17px;
}}
.high {{
    display: inline-block;
    background-color: #00e690;
    border: 2px solid blue;
    padding: 10px;
    width: 100px;
    border-radius: 50%
}}
.mid {{
    background-color: #e6d9a9;
    border: 2px solid blue;
    padding: 10px;
}}
.low {{
    background-color: #ff7070;
    border: 2px solid blue;
}}
</style>

<p style="color: #007396;font-size: 18px"><div class="{range}"></div><span style="font-weight:bold">&nbsp;&nbsp;{fcst} {units}</span> ({fcstLow} {units} - {fcstHigh} {units})</p>

<p style=" margin:0; margin-left: 1.0em;padding:0;font-family:'Open Sans', Arial; font-size:17px;line-height: 18px;">
<img style="vertical-align:bottom" src="resources/GraphicalResources/icons/flag_checkered-24px.svg" width="20" height="20"/>
<!--
<svg style="width:20px;height:20px; vertical-align:bottom" viewBox="0 0 24 24">
    <path fill="black" d="M14.4,6H20V16H13L12.6,14H7V21H5V4H14L14.4,6M14,14H16V12H18V10H16V8H14V10L13,8V6H11V8H9V6H7V8H9V10H7V12H9V10H11V12H13V10L14,12V14M11,10V8H13V10H11M14,10H16V12H14V10Z" />
</svg>-->
<span style="font-weight:bold">{skill}</p>

<p style="vertical-align:center; line-height: 18px; margin:0; margin-left: 1.0em;padding:0;font-family:'Open Sans', Arial; font-size:17px;">
<img style="vertical-align:bottom" src="resources/GraphicalResources/icons/target-24px.svg" width="20" height="20"/>
<!--<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="vertical-align:bottom" version="1.1" width="20" height="20" viewBox="0 0 24 24"><path d="M11,2V4.07C7.38,4.53 4.53,7.38 4.07,11H2V13H4.07C4.53,16.62 7.38,19.47 11,19.93V22H13V19.93C16.62,19.47 19.47,16.62 19.93,13H22V11H19.93C19.47,7.38 16.62,4.53 13,4.07V2M11,6.08V8H13V6.09C15.5,6.5 17.5,8.5 17.92,11H16V13H17.91C17.5,15.5 15.5,17.5 13,17.92V16H11V17.91C8.5,17.5 6.5,15.5 6.08,13H8V11H6.09C6.5,8.5 8.5,6.5 11,6.08M12,11A1,1 0 0,0 11,12A1,1 0 0,0 12,13A1,1 0 0,0 13,12A1,1 0 0,0 12,11Z" /></svg>-->&nbsp;{target}</p>

<p style="vertical-align:center; margin:0; margin-left: 1.0em;padding:0;font-family:'Open Sans', Arial; font-size:17px;line-height: 18px;">
<img style="vertical-align:bottom" src="resources/GraphicalResources/icons/bullseye-24px.svg" width="20" height="20"/>
<!--<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" style="vertical-align:bottom" width="20" height="20" viewBox="0 0 24 24"><path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12C22,10.84 21.79,9.69 21.39,8.61L19.79,10.21C19.93,10.8 20,11.4 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4C12.6,4 13.2,4.07 13.79,4.21L15.4,2.6C14.31,2.21 13.16,2 12,2M19,2L15,6V7.5L12.45,10.05C12.3,10 12.15,10 12,10A2,2 0 0,0 10,12A2,2 0 0,0 12,14A2,2 0 0,0 14,12C14,11.85 14,11.7 13.95,11.55L16.5,9H18L22,5H19V2M12,6A6,6 0 0,0 6,12A6,6 0 0,0 12,18A6,6 0 0,0 18,12H16A4,4 0 0,1 12,16A4,4 0 0,1 8,12A4,4 0 0,1 12,8V6Z" /></svg>-->&nbsp;{predictors}</p>
<p style="vertical-align:center; margin:0; margin-left: 1.5em;padding:0;font-family:'Open Sans', Arial;line-height: 18px; font-size:17px; text-align:right; color: darkgray">{id}</p>
"""


class forecastList_HTML(QtWidgets.QTreeWidget):

    def __init__(self, parent = None):

        QtWidgets.QTreeWidget.__init__(self)
        self.setColumnCount(1)
        self.setHeaderLabels(["Forecasts"])
        for i in range(2):
            ii = QtWidgets.QTreeWidgetItem(self, ["Forecast Period April " + str(i)])
            for j in range(4):
                jj = QtWidgets.QTreeWidgetItem(ii, ["Issue Date " + str(j)])
                for k in range(3):
                    item = QtWidgets.QTreeWidgetItem(jj, 0)
                    label = QtWidgets.QLabel(HTML_FORMAT.format(target = "Buffalo Bill April 01 - July 31 Inflow", predictors = "PDSI, Antecedant Inflow, SNOTEL, SST",skill = "R2: 0.5", range="high", id="101101", fcst="800", fcstLow="405", fcstHigh="1211", units="KAF"))
                    
                    print(label.text())
                    label.setTextFormat(QtCore.Qt.RichText)
                    label.show()
                    self.setItemWidget(item,0, label)
        self.show()

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    widg = QtWidgets.QWidget()
    label = QtWidgets.QLabel(FF)
    #label = QtWidgets.QLabel(HTML_FORMAT.format(target = "Buffalo Bill April 01 - July 31 Inflow", predictors = "PDSI, Antecedant Inflow, SNOTEL, SST",skill = "R2: 0.5", range="high", id="101101", fcst="800", fcstLow="405", fcstHigh="1211", units="KAF"))
    label.setTextFormat(QtCore.Qt.RichText)
    #print(label.text())
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(label)
    widg.setLayout(layout)
    widg.show()
    #mw = forecastList_HTML()
    sys.exit(app.exec_())