# PyForecast
PyForecast is a statistical modeling tool useful in predicting monthly and seasonal inflows and streamflows. The tool collects meterological and hydrologic datasets, analyzes hundreds to thousands of predictor subsets, and returns statistical regressions between predictors and streamflows. Check out the [Wiki](https://github.com/usbr/PyForecast/wiki) for background information and a brief walkthrough for how to use the software. Beta testing is underway, you may download an installer at [this link](https://github.com/usbr/PyForecast/releases) to install PyForecast on your machine.

## Requirements
* Python 3.X with the following libraries installed
    * [numpy](http://www.numpy.org/)
    * [scipy](https://www.scipy.org/)
    * [pandas](https://pandas.pydata.org/)
    * [requests](http://python-requests.org)
    * [zeep](https://python-zeep.readthedocs.io/en/master/)
    * [sklearn](https://scikit-learn.org/stable/)
    * [matplotlib](https://matplotlib.org/)
    * [PyQt5 (MUST BE version 5.9)](https://pypi.org/project/PyQt5/)
    * [pyqtchart (MUST BE version 5.9)](https://pypi.org/project/PyQtChart/)
    * [datetime](https://docs.python.org/3/library/datetime.html)
    * [openpyxl](https://pypi.org/project/openpyxl/)
    * [xlrd](https://pypi.org/project/xlrd/)
    * [configparser](https://pypi.org/project/configparser/)
    * [statsmodels](https://www.statsmodels.org/stable/index.html)
    * [scikit-learn](https://scikit-learn.org/stable/)
    * [staty](https://pypi.org/project/staty/)
    * [pyqtgraph](https://www.pyqtgraph.org/)
    * [geojson](https://pypi.org/project/geojson/)
    * [fuzzywuzzy](https://pypi.org/project/fuzzywuzzy/)
    * [bitarray](https://pypi.org/project/bitarray/)

These packages can be installed automatically to your default python distribution by running the 'install_dependencies.bat' script. 

## Use
Run the software by downloading the source code and running the program via a Python IDE with main.py, via Visual Studio with NextFlow.pyproj, or by installing the program using the latest release at [this link](https://github.com/usbr/PyForecast/releases).

## Disclaimer
The software as originally published constitutes a work of the United States Government and is not subject to domestic copyright protection under 17 USC ยค 105. Subsequent contributions by members of the public, however, retain their original copyright.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
