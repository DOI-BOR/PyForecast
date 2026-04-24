import pyqtgraph as pg


class ErrorPlot(pg.PlotItem):

    def __init__(self, parent=None, enableMenu=False, **kwargs):

        super().__init__(parent, enableMenu=enableMenu, **kwargs)
        return

    def plot(self, x, y):

        self.clear()
        self.bg = pg.BarGraphItem()
        self.bg.setData(x, y)
        self.addItem(self.bg)

    def tooltip(self, x, y, data):
        if self.bg.opts['hoverable']:
            return f'{data}: ({x:.2f}, {y:.2f})'
        else:
            return ''
