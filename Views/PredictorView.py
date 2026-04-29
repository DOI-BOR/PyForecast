import sys

from PySide6.QtCore import Qt, QDate, QStringListModel, QModelIndex, QSortFilterProxyModel
from PySide6.QtWidgets import (QApplication, QDialog, QAbstractItemView, QMessageBox,
                               QPushButton, QSizePolicy, QTableView, QCheckBox, QFrame,
                               QFormLayout, QLabel, QHBoxLayout, QGridLayout)
from pandas import DateOffset

from Models.ModelConfigurations import ResampledDataset
from Utilities.HydrologyDateTimes import water_year_start_date
from Utilities.ZzQWidgets import ZzQDateEdit, ZzQComboBox

app = QApplication.instance()


class MethodFilterModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filterString = None

    def setFilterString(self, dataset):

        self.dataset = dataset
        text = dataset.display_unit.type
        self.filterString = text.lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, sourceRow, sourceParent=QModelIndex()):
        idx = self.sourceModel().index(sourceRow, 0)
        source_method = self.sourceModel().data(idx, Qt.ItemDataRole.DisplayRole)
        if self.filterString == 'flow':
            if self.dataset.display_unit.id == 'cfs':
                if 'MCM' in source_method:
                    return False
            elif self.dataset.display_unit.id == 'cms':
                if 'KAF' in source_method:
                    return False
            return True
        else:
            if 'MCM' in source_method or 'KAF' in source_method:
                return False
            else:
                return True


class UnitFilterModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filterString = 'length'
        self.dataset = None
        self.method = ''

    def setFilterString(self, dataset, method):
        self.method = method
        self.dataset = dataset
        text = dataset.display_unit.type
        self.filterString = text.lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, sourceRow, sourceParent=QModelIndex()):
        idx = self.sourceModel().index(sourceRow, 5)
        source_unit_type = self.sourceModel().data(idx, Qt.ItemDataRole.DisplayRole)
        idx2 = self.sourceModel().index(sourceRow, 0)
        source_unit_id = self.sourceModel().data(idx2, Qt.ItemDataRole.DisplayRole)

        if 'MCM' in self.method:
            if source_unit_id == 'mcm':
                return True
            else:
                return False
        elif 'KAF' in self.method:
            if source_unit_id == 'kaf':
                return True
            else:
                return False
        else:
            if source_unit_type == self.filterString:
                return True
            else:
                return False

class PredictorView(QDialog):

    def __init__(self, parent=None, app=None, selected_configuration=None):

        super().__init__(parent)

        self.method_model = QStringListModel(app.agg_methods.keys())
        self.filter_method_model = MethodFilterModel()
        self.filter_method_model.setSourceModel(self.method_model)
        self.filter_units_model = UnitFilterModel()
        self.filter_units_model.setSourceModel(app.units)

        self.selected_configuration = selected_configuration
        self.configuration = (
            app.model_configurations.get_by_id(self.selected_configuration)
        )
        self.current_idx = -1
        self.setUI()

        self.predictor_field.currentIndexChanged.connect(
            lambda: self.updateMethodUnits('predictor')
        )
        self.predictor_method_field.currentIndexChanged.connect(
            lambda: self.updateMethodUnits('method')
        )

        self.predictor_grid.setModel(self.configuration.predictor_pool)
        self.new_button.pressed.connect(self.new_predictor)
        self.delete_all_button.pressed.connect(self.delete_all)
        self.auto_gen_button.pressed.connect(self.autogen)
        self.configuration.predictor_pool.dataChanged.connect(
            lambda: self.predictor_grid.resizeColumnsToContents()
        )
        self.predictor_grid.selectionModel().currentChanged.connect(
            lambda x: self.setPredictor(x.row())
        )
        self.save_predictor_button.pressed.connect(self.savePredictor)
        self.delete_button.pressed.connect(self.delPredictor)
        if len(self.configuration.predictor_pool) > 0:
            self.predictor_grid.selectRow(0)

    def updateMethodUnits(self, type_):
        dataset = app.datasets[self.predictor_field.currentIndex()]
        if type_ == 'predictor':
            self.filter_method_model.setFilterString(dataset)
            self.filter_units_model.setFilterString(
                dataset, self.predictor_method_field.currentText()
            )
            self.predictor_unit_field.setCurrentText(
                dataset.display_unit.__list_form__()
            )
        elif type_ == 'method':
            method = self.predictor_method_field.currentText()
            self.filter_units_model.setFilterString(dataset, method)
            if not ('MCM' in method) and not ('KAF' in method):
                self.predictor_unit_field.setCurrentText(
                    dataset.display_unit.__list_form__()
                )

    def autogen(self):

        wys = water_year_start_date(self.configuration.issue_date)
        non_generated_predictors = []

        def boundByWaterYear(d):
            return max(d, wys)

        # Iterate over the datasets in the file
        for dataset in app.datasets.datasets:
            print(f'on dataset: {dataset.name}')
            day_minus_one = self.configuration.issue_date - DateOffset(days=1)
            # Correct leap day bug
            if (day_minus_one.month == 2) and (day_minus_one.day == 29):
                day_minus_one = day_minus_one - DateOffset(days=1)
            if dataset.raw_unit.type.lower() == 'flow':
                predictor = ResampledDataset(
                    dataset_guid=dataset.guid,
                    forced=False,
                    mustBePositive=False,
                    agg_method='AVERAGE',
                    period_start=boundByWaterYear(
                        self.configuration.issue_date - DateOffset(months=3)),
                    period_end=day_minus_one,
                    preprocessing='NONE'
                )
                self.configuration.predictor_pool.add_predictor(predictor)
                continue
            elif dataset.raw_unit.type.lower() == 'temperature':
                predictor = ResampledDataset(
                    dataset_guid=dataset.guid,
                    forced=False,
                    mustBePositive=False,
                    agg_method='AVERAGE',
                    period_start=boundByWaterYear(
                        self.configuration.issue_date - DateOffset(months=3)),
                    period_end=day_minus_one,
                    preprocessing='NONE'
                )
                self.configuration.predictor_pool.add_predictor(predictor)
                continue
            elif 'NOAA-CPC' in dataset.dataloader.NAME:
                predictor = ResampledDataset(
                    dataset_guid=dataset.guid,
                    forced=False,
                    mustBePositive=False,
                    agg_method='AVERAGE',
                    period_start=boundByWaterYear(
                        self.configuration.issue_date - DateOffset(months=3)),
                    period_end=day_minus_one,
                    preprocessing='NONE'
                )
                self.configuration.predictor_pool.add_predictor(predictor)
                continue
            elif 'PRECIPITATION' in dataset.parameter.upper():
                predictor = ResampledDataset(
                    dataset_guid=dataset.guid,
                    forced=False,
                    mustBePositive=False,
                    agg_method='ACCUMULATION',
                    period_start=wys,
                    period_end=day_minus_one,
                    preprocessing='NONE'
                )
                self.configuration.predictor_pool.add_predictor(predictor)
                predictor = ResampledDataset(
                    dataset_guid=dataset.guid,
                    forced=False,
                    mustBePositive=False,
                    agg_method='ACCUMULATION',
                    period_start=boundByWaterYear(
                        self.configuration.issue_date - DateOffset(months=1)),
                    period_end=day_minus_one,
                    preprocessing='NONE'
                )
                self.configuration.predictor_pool.add_predictor(predictor)
                continue
            elif 'PDSI' in dataset.dataloader.NAME:
                predictor = ResampledDataset(
                    dataset_guid=dataset.guid,
                    forced=False,
                    mustBePositive=False,
                    agg_method='AVERAGE',
                    period_start=boundByWaterYear(
                        self.configuration.issue_date - DateOffset(months=3)),
                    period_end=day_minus_one,
                    preprocessing='NONE'
                )
                self.configuration.predictor_pool.add_predictor(predictor)
                continue
            elif 'SNOW' in dataset.parameter.upper():
                predictor = ResampledDataset(
                    dataset_guid=dataset.guid,
                    forced=False,
                    mustBePositive=True,
                    agg_method='LAST',
                    period_start=boundByWaterYear(
                        self.configuration.issue_date - DateOffset(days=15)),
                    period_end=day_minus_one,
                    preprocessing='NONE'
                )
                self.configuration.predictor_pool.add_predictor(predictor)
                continue
            else:
                non_generated_predictors.append(dataset)

        if len(non_generated_predictors) > 0:
            s = '\n\n'.join([d.__repr__() for d in non_generated_predictors])
            QMessageBox.information(
                self,
                'Unsupported Datasets',
                f"The following datasets had no predictors genereated:\n\n {s}")

        return

    def delete_all(self):
        for i in range(len(self.configuration.predictor_pool)):
            rc = self.configuration.predictor_pool.rowCount()
            self.configuration.predictor_pool.delete_predictor(rc - 1)

    def new_predictor(self):
        predictor = ResampledDataset(
            dataset_guid=app.datasets[0].guid,
            forced=False,
            mustBePositive=False,
            agg_method=list(app.agg_methods.keys())[0],
            preprocessing=list(app.preprocessing_methods.keys())[0],
            period_start=self.configuration.issue_date - DateOffset(days=1),
            period_end=self.configuration.issue_date - DateOffset(days=0),
        )
        self.configuration.predictor_pool.add_predictor(predictor)
        self.setPredictor(self.configuration.predictor_pool.rowCount() - 1)
        return

    def clear_widg(self):
        return

    def setUI(self):

        self.setWindowTitle('Predictors')
        self.setWindowIcon(app.icon)

        self.auto_gen_button = QPushButton("Auto Generate")
        self.auto_gen_button.setSizePolicy(QSizePolicy.Policy.Maximum,
                                           QSizePolicy.Policy.Maximum)
        self.delete_button = QPushButton('Delete Selected')
        self.delete_button.setSizePolicy(QSizePolicy.Policy.Maximum,
                                         QSizePolicy.Policy.Maximum)
        self.delete_all_button = QPushButton('Delete All')
        self.delete_all_button.setSizePolicy(QSizePolicy.Policy.Maximum,
                                             QSizePolicy.Policy.Maximum)
        self.predictor_grid = QTableView()
        self.predictor_grid.horizontalHeader().setVisible(True)
        self.predictor_grid.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.predictor_grid.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.new_button = QPushButton("Add new predictor")
        self.new_button.setSizePolicy(QSizePolicy.Policy.Maximum,
                                      QSizePolicy.Policy.Maximum)

        self.predictor_field = ZzQComboBox()
        self.predictor_field.setModel(app.datasets)
        self.predictor_method_field = ZzQComboBox()
        self.predictor_method_field.setModel(self.filter_method_model)
        self.predictor_period_start_field = ZzQDateEdit()
        self.predictor_period_start_field.setDisplayFormat('MMM dd')
        self.predictor_period_end_field = ZzQDateEdit()
        self.predictor_period_end_field.setDisplayFormat('MMM dd')
        self.predictor_preprocessing_field = ZzQComboBox()
        self.predictor_preprocessing_field.setModel(
            QStringListModel(
                [x for x in app.preprocessing_methods.keys() if not x.startswith('INV_')]
            )
        )
        self.predictor_unit_field = ZzQComboBox()
        self.predictor_unit_field.setModel(self.filter_units_model)
        self.predictor_unit_field.setModelColumn(6)
        self.predictor_positive_box = QCheckBox()
        self.save_predictor_button = QPushButton("Save")
        self.predictor_force_box = QCheckBox()

        self.predictor_widg = QFrame()
        self.predictor_widg.setFrameStyle(QFrame.Shape.Box)
        self.predictor_widg.setLineWidth(2)
        qlayout = QFormLayout()
        qlayout.addRow(QLabel("Edit Predictor"))
        qlayout.addRow("Predictor Dataset", self.predictor_field)
        qlayout.addRow("Predictor Aggregation Method", self.predictor_method_field)
        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel('Aggregation Period'))
        hlayout.addStretch(1)
        hlayout.addWidget(self.predictor_period_start_field)
        hlayout.addWidget(QLabel('to'))
        hlayout.addWidget(self.predictor_period_end_field)
        qlayout.addRow(hlayout)
        qlayout.addRow("Predictor Preprocessing", self.predictor_preprocessing_field)
        qlayout.addRow("Predictor Unit", self.predictor_unit_field)
        qlayout.addRow(
            "Enforce positive correlation between predictor and forecast target?",
            self.predictor_positive_box
        )
        hlayout = QHBoxLayout()
        hlayout.addStretch(1)
        qlayout.addRow("Force predictor to be in all models?", self.predictor_force_box)
        hlayout.addWidget(self.save_predictor_button)
        qlayout.addRow(hlayout)

        self.predictor_widg.setLayout(qlayout)
        self.predictor_widg.setEnabled(False)

        layout = QGridLayout()
        layout.addWidget(self.auto_gen_button, 0, 0, 1, 1)
        layout.addWidget(self.new_button, 0, 2, 1, 1)
        layout.addWidget(self.delete_button, 0, 3, 1, 1)
        layout.addWidget(self.delete_all_button, 0, 4, 1, 1)
        layout.addWidget(self.predictor_grid, 1, 0, 1, 5)
        layout.addWidget(self.predictor_widg, 2, 0, 1, 5)

        self.setLayout(layout)

    def delPredictor(self):
        idx = self.predictor_grid.selectionModel().currentIndex().row()
        self.configuration.predictor_pool.delete_predictor(idx)

    def savePredictor(self):

        self.predictor_widg.setEnabled(True)

        idx = self.predictor_unit_field.currentIndex()
        idx = self.filter_units_model.mapToSource(
            self.filter_units_model.index(idx, 0)
        )

        predictor = ResampledDataset(
            dataset_guid=app.datasets[self.predictor_field.currentIndex()].guid,
            period_start=self.predictor_period_start_field.date().toPython(),
            period_end=self.predictor_period_end_field.date().toPython(),
            preprocessing=self.predictor_preprocessing_field.currentText(),
            unit=app.units[idx.row()],
            agg_method=self.predictor_method_field.currentText(),
            forced=self.predictor_force_box.isChecked(),
            mustBePositive=self.predictor_positive_box.isChecked()
        )

        self.configuration.predictor_pool[self.current_idx] = predictor

    def setPredictor(self, idx):
        self.predictor_widg.setEnabled(True)
        self.current_idx = idx
        predictor = self.configuration.predictor_pool[idx]
        self.predictor_field.setCurrentText(predictor.dataset().__condensed_form__())
        self.predictor_method_field.setCurrentText(predictor.agg_method)
        self.predictor_period_start_field.setDate(QDate(predictor.period_start))
        self.predictor_period_end_field.setDate(QDate(predictor.period_end))
        self.predictor_preprocessing_field.setCurrentText(predictor.preprocessing)
        self.predictor_unit_field.setCurrentText(predictor.unit.__list_form__())
        self.predictor_positive_box.setChecked(predictor.mustBePositive)
        self.predictor_force_box.setChecked(predictor.forced)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = PredictorView()
    mw.exec_()
    sys.exit(app.exec())
