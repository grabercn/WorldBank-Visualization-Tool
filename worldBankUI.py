# List of required modules
required_modules = [
    'wbgapi', 'matplotlib', 'pandas', 'PyQt5', 'scikit-learn', 'statsmodels', 'numpy', 'pyinstaller'
]

# needed imports for the auto installer
import importlib
import subprocess
import sys

# checks if any modules need installing
def install_missing_modules():
    for module in required_modules:
        try:
            importlib.import_module(module)
        except ImportError:
            print(f"Module '{module}' not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])

install_missing_modules()

# rest of the program continues here
import wbgapi as wb
from matplotlib.pyplot import bar, plot, scatter, title, xlabel, ylabel, figure, xticks, legend, grid, show, xlim
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QLabel, QListWidget, 
                             QApplication, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QPushButton, QComboBox, QSizePolicy, 
                             QCheckBox, QLineEdit)
from PyQt5.QtGui import QPalette

class WorldBankUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("World-BankUI (Unofficial Graphing Tool)")
        self.setGeometry(200, 800, 1400, 1000)
        self.data = None
        self.current_dfs = []
        self.countries = wb.economy.list()
        self.create_ui()
        self.fetch_worldbank_data()
    
    def create_ui(self):
        self.layout = QVBoxLayout()

        self.instruction_label_countries = QLabel("Select Countries (Click to select multiple):")
        self.layout.addWidget(self.instruction_label_countries)

        self.country_selector = QListWidget()
        self.country_selector.setSelectionMode(QListWidget.MultiSelection)
        self.country_selector.addItems([country['id'] + ': ' + country['value'] for country in self.countries])
        self.layout.addWidget(self.country_selector)
        
        self.instruction_label_series = QLabel("Select a Data Series:")
        self.layout.addWidget(self.instruction_label_series)

        self.data_search_bar = QLineEdit()
        self.data_search_bar.setPlaceholderText("Search datasets...")
        self.data_search_bar.textChanged.connect(self.filter_data_series)
        self.layout.addWidget(self.data_search_bar)
        
        self.data_list = QListWidget()
        self.data_list.itemClicked.connect(self.on_data_series_selected)
        self.layout.addWidget(self.data_list)

        self.table_widget = QTableWidget()
        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.table_widget)

        self.graph_type_selector = QComboBox()
        self.graph_type_selector.addItems(["Line", "Bar", "Scatter"])
        self.layout.addWidget(QLabel("Select Graph Type:"))
        self.layout.addWidget(self.graph_type_selector)

        self.marker_style_selector = QComboBox()
        self.marker_style_selector.addItems(["o", "s", "D", "x", "^", "v"])
        self.layout.addWidget(QLabel("Marker Style:"))
        self.layout.addWidget(self.marker_style_selector)

        self.source_checkbox = QCheckBox("Include source link")
        self.layout.addWidget(self.source_checkbox)

        self.prediction_checkbox = QCheckBox("Show Predictions")
        self.layout.addWidget(self.prediction_checkbox)

        self.plot_button = QPushButton("Plot Data")
        self.plot_button.clicked.connect(self.plot_selected_data)
        self.layout.addWidget(self.plot_button)

        self.loading_label = QLabel("")
        self.layout.addWidget(self.loading_label)

        self.github_label = QLabel('<a href="https://github.com/grabercn">Made with ❤️ by Chrismslist</a>')
        self.github_label.setOpenExternalLinks(True)
        self.layout.addWidget(self.github_label)
        
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.apply_theme()  # Apply theme based on system setting

    def apply_theme(self):
        """Applies a light or dark theme based on system settings."""
        palette = QApplication.palette()
        if palette.color(QPalette.Window).value() < 128:  # Dark mode
            self.setStyleSheet("""
                QWidget {
                    background-color: #1e1e2f;
                    color: #e6e6e6;
                    font-family: Arial;
                }
                QListWidget, QTableWidget {
                    background-color: #28293d;
                    border: 1px solid #3e3e50;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #008CBA;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #005f75;
                }
                QLabel, QCheckBox, QComboBox {
                    margin: 5px;
                }
                QLabel#instruction_label_countries, QLabel#instruction_label_series {
                    font-size: 14px;
                    font-weight: bold;
                }
                QLabel#github_label {
                    margin-top: 10px;
                    font-size: 12px;
                }
            """)
        else:  # Light mode
            self.setStyleSheet("""
                QWidget {
                    background-color: #f7f9fc;
                    color: #1e1e2f;
                    font-family: Arial;
                }
                QListWidget, QTableWidget {
                    background-color: #ffffff;
                    border: 1px solid #c0c0c0;
                    color: #1e1e2f;
                }
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
                QLabel, QCheckBox, QComboBox {
                    margin: 5px;
                }
                QLabel#instruction_label_countries, QLabel#instruction_label_series {
                    font-size: 14px;
                    font-weight: bold;
                }
                QLabel#github_label {
                    margin-top: 10px;
                    font-size: 12px;
                }
            """)

    def fetch_worldbank_data(self):
        self.loading_label.setText("Loading data, please wait...")
        QApplication.processEvents()
        try:
            self.data = list(wb.series.list())
            self.data_list.clear()
            for item in self.data:
                self.data_list.addItem(f"{item['id']}: {item['value']}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch data: {str(e)}")
        finally:
            self.loading_label.setText("")

    def filter_data_series(self, text):
        filtered_data = [f"{item['id']}: {item['value']}" for item in self.data if text.lower() in item['value'].lower()]
        self.data_list.clear()
        self.data_list.addItems(filtered_data)

    def on_data_series_selected(self, item):
        try:
            series_id = item.text().split(":")[0].strip()
            self.selected_series_title = item.text().split(": ")[1].strip()

            selected_countries = [country.text().split(":")[0].strip() for country in self.country_selector.selectedItems()]
            self.current_dfs.clear()

            self.loading_label.setText("Fetching data, please wait...")
            QApplication.processEvents()

            for country in selected_countries:
                df = wb.data.DataFrame(series_id, economy=country)
                df.reset_index(inplace=True)
                self.current_dfs.append(df)

            if self.current_dfs:
                self.current_df = pd.concat(self.current_dfs, ignore_index=True)
                self.populate_table(self.current_df)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch data for series: {str(e)}")
        finally:
            self.loading_label.setText("")

    def populate_table(self, df):
        self.table_widget.setRowCount(df.shape[0])
        self.table_widget.setColumnCount(df.shape[1])
        self.table_widget.setHorizontalHeaderLabels(df.columns.astype(str))
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iat[i, j]))
                self.table_widget.setItem(i, j, item)

    def calculate_arima_predictions(self, years, values):
        """Calculates future predictions using ARIMA while handling NaN values."""
        
        # Drop NaNs and prepare the data
        values = values.dropna()
        if len(values) < 2:  # Not enough data to train
            raise ValueError("Not enough data to fit ARIMA model.")
        
        years = np.array([int(year) for year in years[:len(values)]]).reshape(-1, 1)
        
        # Ensure values are a 1D array for ARIMA
        values = values.values.flatten()

        # Fit the ARIMA model
        model = ARIMA(values, order=(5, 1, 0))  # You can adjust the order as needed
        model_fit = model.fit()

        # Forecast future values
        forecast_years = 10  # Forecast for the next 10 years
        forecast = model_fit.forecast(steps=forecast_years)
        
        # Create future years based on the last year in the data
        last_year = int(years[-1][0])
        future_years = np.array(range(last_year + 1, last_year + forecast_years + 1))
        
        return future_years.tolist(), forecast.tolist()

    def plot_selected_data(self):
        try:
            if hasattr(self, 'current_df') and self.current_df is not None:
                country_column = self.current_df.columns[0]
                years = self.current_df.columns[1:]
                years = [int(year.replace("YR", "")) for year in years]  # Convert to integer years
                values = self.current_df.iloc[:, 1:]

                figure(figsize=(12, 8))
                marker_style = self.marker_style_selector.currentText()
                graph_type = self.graph_type_selector.currentText()

                for i, country in enumerate(self.current_df[country_column]):
                    country_values = values.iloc[i].dropna()
                    plot_years = years[:len(country_values)]

                    # Plot original data with a solid line
                    if graph_type == "Line":
                        plot(plot_years, country_values, marker=marker_style, linestyle='-', label=country)
                    elif graph_type == "Bar":
                        bar(plot_years, country_values, label=country, alpha=0.6)
                    elif graph_type == "Scatter":
                        scatter(plot_years, country_values, marker=marker_style, label=country)

                    # Plot predictions for future years only if checkbox is checked
                    if self.prediction_checkbox.isChecked():
                        self.loading_label.setText("Calculating data predictions, please wait...")
                        future_years, future_values = self.calculate_arima_predictions(plot_years, country_values)
                        # Plot predictions as a dotted line for future years only
                        plot(future_years, future_values, linestyle='--', marker='o', label=f"{country} (predicted)")
                        self.loading_label.setText("")


                title(self.selected_series_title, fontsize=14)
                xlabel('Year', fontsize=12)
                ylabel('Value', fontsize=12)

                # Adjust x-axis for better readability
                xticks(rotation=45)
                x_min = min(plot_years) if plot_years else 0
                x_max = max(future_years) if self.prediction_checkbox.isChecked() else max(plot_years)
                xlim(x_min - 1, x_max + 1)  # Set x-axis range

                legend(fontsize=10)
                grid(True)

                if self.source_checkbox.isChecked():
                    title(self.selected_series_title + "\nSource: World Bank Data - https://data.worldbank.org", fontsize=14)

                show()
            else:
                QMessageBox.critical(self, "Error", "No data available to plot.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to plot data: {str(e)}")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WorldBankUI()
    window.show()
    sys.exit(app.exec_())
