import sys
import wbgapi as wb
from matplotlib.pyplot import bar, plot, scatter, title, xlabel, ylabel, figure, xticks, legend, grid, show
import pandas as pd
import subprocess
import importlib
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QLabel, QListWidget, 
                             QApplication, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QPushButton, QComboBox, QSizePolicy, 
                             QCheckBox, QLineEdit)

# this section checks needed modules and installs them if necessary
# List of required modules
required_modules = [
    'wbgapi', 'matplotlib', 'pandas', 'PyQt5'
]

def install_missing_modules():
    """Checks if required modules are installed and installs missing ones."""
    for module in required_modules:
        try:
            importlib.import_module(module)
        except ImportError:
            print(f"Module '{module}' not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])

# Install missing modules before running the application
install_missing_modules()

class WorldBankUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("World-BankUI (Unofficial Graphing Tool)")
        self.setGeometry(200, 800, 1400, 1000)  # Increased window size

        self.data = None  # Store the list of available data series
        self.current_dfs = []  # Store the fetched DataFrames for each selected country
        self.countries = wb.economy.list()  # Fetch the list of available countries
        self.create_ui()  # Create the initial UI
        self.fetch_worldbank_data()  # Fetch World Bank data
    
    def create_ui(self):
        """Sets up the UI elements."""
        self.layout = QVBoxLayout()

        # Instructional label for country selection
        self.instruction_label_countries = QLabel("Select Countries (Click to select multiple):")
        self.layout.addWidget(self.instruction_label_countries)

        # List widget for country selection
        self.country_selector = QListWidget()
        self.country_selector.setSelectionMode(QListWidget.MultiSelection)  # Allow multiple selections
        self.country_selector.addItems([country['id'] + ': ' + country['value'] for country in self.countries])
        self.layout.addWidget(self.country_selector)
        
        # Instructional label for data series selection
        self.instruction_label_series = QLabel("Select a Data Series:")
        self.layout.addWidget(self.instruction_label_series)

        # Search bar for data series list
        self.data_search_bar = QLineEdit()
        self.data_search_bar.setPlaceholderText("Search datasets...")
        self.data_search_bar.textChanged.connect(self.filter_data_series)
        self.layout.addWidget(self.data_search_bar)
        
        # List widget to display fetched data series
        self.data_list = QListWidget()
        self.data_list.itemClicked.connect(self.on_data_series_selected)
        self.layout.addWidget(self.data_list)

        # Table widget to display the DataFrame data
        self.table_widget = QTableWidget()  # This is the widget for table display
        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Set size policy
        self.layout.addWidget(self.table_widget)

        # ComboBox for selecting graph type
        self.graph_type_selector = QComboBox()
        self.graph_type_selector.addItems(["Line", "Bar", "Scatter"])  # Add graph types
        self.layout.addWidget(QLabel("Select Graph Type:"))
        self.layout.addWidget(self.graph_type_selector)

        # Marker style input
        self.marker_style_selector = QComboBox()
        self.marker_style_selector.addItems(["o", "s", "D", "x", "^", "v"])  # Various marker styles
        self.layout.addWidget(QLabel("Marker Style:"))
        self.layout.addWidget(self.marker_style_selector)
        
        # Checkbox to include source link
        self.source_checkbox = QCheckBox("Include source link")
        self.layout.addWidget(self.source_checkbox)

        # Button to plot the selected data
        self.plot_button = QPushButton("Plot Data")
        self.plot_button.clicked.connect(self.plot_selected_data)
        self.layout.addWidget(self.plot_button)

        # Loading label
        self.loading_label = QLabel("")  # This will show loading text
        self.layout.addWidget(self.loading_label)

        # GitHub footer label
        self.github_label = QLabel('<a href="https://github.com/grabercn">Made with ❤️ by Chrismslist</a>')
        self.github_label.setOpenExternalLinks(True)
        self.layout.addWidget(self.github_label)
        
        # Set layout for the main window
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Set stylesheet for color and appearance
        self.setStyleSheet("""
            QWidget {
                background-color: #f7f9fc;  /* Light background */
            }
            QListWidget, QTableWidget {
                background-color: #ffffff;  /* White background for input fields */
                border: 1px solid #c0c0c0;  /* Gray border */
            }
            QPushButton {
                background-color: #007bff;  /* Bootstrap primary blue */
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;  /* Darker blue on hover */
            }
            QLabel {
                margin: 5px;
                font-weight: bold;  /* Make instructional text bold */
            }
        """)

    def fetch_worldbank_data(self):
        """Fetches data from the World Bank API and populates the list widget."""
        self.loading_label.setText("Loading data, please wait...")  # Show loading message
        QApplication.processEvents()  # Update the GUI with loading message
        try:
            self.data = list(wb.series.list())  # Fetch the list of available data series
            self.data_list.clear()

            # Populate QListWidget with series IDs and names
            for item in self.data:
                self.data_list.addItem(f"{item['id']}: {item['value']}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch data: {str(e)}")
        finally:
            self.loading_label.setText("")  # Clear loading message

    def filter_data_series(self, text):
        """Filters the data series based on search bar input."""
        filtered_data = [f"{item['id']}: {item['value']}" for item in self.data if text.lower() in item['value'].lower()]
        self.data_list.clear()
        self.data_list.addItems(filtered_data)

    def on_data_series_selected(self, item):
        """Handles the selection of a data series from the list."""
        try:
            # Extract the series ID and title from the selected item
            series_id = item.text().split(":")[0].strip()
            self.selected_series_title = item.text().split(": ")[1].strip()  # Store the title

            # Get selected countries
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
        """Populates the QTableWidget with the DataFrame data."""
        self.table_widget.setRowCount(df.shape[0])  # Set the number of rows
        self.table_widget.setColumnCount(df.shape[1])  # Set the number of columns
        self.table_widget.setHorizontalHeaderLabels(df.columns.astype(str))  # Set the column headers

        # Loop through the DataFrame and add each cell's data to the table widget
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iat[i, j]))  # Convert each item to string
                self.table_widget.setItem(i, j, item)  # Add the item to the table

    def plot_selected_data(self):
        """Plots the data based on the available columns in the fetched DataFrame."""
        try:
            if hasattr(self, 'current_df') and self.current_df is not None:
                # The first column is the country code
                country_column = self.current_df.columns[0]  # Assuming this is the country code column
                years = self.current_df.columns[1:]  # The remaining columns are years
                # Remove the "YR" prefix from years
                years = [year.replace("YR", "") for year in years]
                values = self.current_df.iloc[:, 1:]  # Get the corresponding values

                figure(figsize=(12, 8))
                
                marker_style = self.marker_style_selector.currentText()
                graph_type = self.graph_type_selector.currentText()

                for i, country in enumerate(self.current_df[country_column]):
                    if graph_type == "Line":
                        plot(years, values.iloc[i], marker=marker_style, linestyle='-', label=country)
                    elif graph_type == "Bar":
                        bar(years, values.iloc[i], label=country, alpha=0.6)
                    elif graph_type == "Scatter":
                        scatter(years, values.iloc[i], marker=marker_style, label=country)

                title(self.selected_series_title, fontsize=14)
                xlabel('Year', fontsize=12)
                ylabel('Value', fontsize=12)
                xticks(rotation=45)  # Rotate x-axis labels for better readability
                legend(fontsize=10)
                grid(True)

                # Include the source link if the checkbox is checked
                if self.source_checkbox.isChecked():
                    title(self.selected_series_title+ "\nSource: World Bank Data - https://data.worldbank.org", fontsize=14) 

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
