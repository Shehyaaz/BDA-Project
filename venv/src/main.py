from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import subprocess
import re
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
# user-defined module imports
from main_window import Ui_MainWindow
from insert_document import Insert_Document_Dialog
from delete_document import Delete_Document_Dialog
from update_document import Update_Document_Dialog
from adv_search import Adv_Search_Dialog
from recommended_apps import Recommended_Apps_Dialog
from mongo_db import Mongo_db
from data_model import DataModel
from graph import *


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.mongo_obj = Mongo_db()
        self.setupMainWindow()

    def setupMainWindow(self):
        # create UI
        self.setupUi(self)

        # a figure instance to plot on
        self.figure = plt.figure()
        # this is the Canvas Widget that displays the 'figure'it takes the 'figure' instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        # this is the Navigation widget it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)
        # creating a Vertical Box layout
        self.plot_layout = QVBoxLayout()
        # adding tool bar to the layout
        self.plot_layout.addWidget(self.toolbar)
        # adding canvas to the layout
        self.plot_layout.addWidget(self.canvas)
        self.plot.setLayout(self.plot_layout)

        # connect controllers to menu items
        # File menu items
        self.actionImport_dataset.triggered.connect(self.importDataset)
        self.actionExport_dataset.triggered.connect(self.exportDataset)
        self.actionQuit.triggered.connect(self.close)
        # Edit menu items
        self.actionInsert_Document.triggered.connect(self.insertDocument)
        self.actionUpdate_Document.triggered.connect(self.updateDocument)
        self.actionDelete_Document.triggered.connect(self.deleteDocument)
        self.actionDelete_Collection.triggered.connect(self.deleteCollection)

        # connect controllers to buttons
        # Tab1
        self.load_data.pressed.connect(self.loadData)
        self.search.pressed.connect(self.searchData)
        self.adv_search.pressed.connect(self.advSearchData)
        # Tab2
        self.recommended.pressed.connect(self.getRecommendations)
        self.graphs.currentIndexChanged.connect(self.displayGraph)

    def importDataset(self):
        # open file dialog to import dataset
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Import Dataset", "", "Comma Separated Values (*.csv)"
        )
        if fileName == '':
            return 0
        else:
            cmd = ["mongoimport", "--db", "bda-project", "--collection",
                   "googleplaystore", "--type", "csv", "--headerline", "--file", fileName]
            output = subprocess.run(cmd)
            if output.returncode == 0:
                self.alert("success", "Import Successful",
                           "The data was successfully imported")
            else:
                self.alert("error", "Import Unsuccessful",
                           "The data could not be imported :(")

    def exportDataset(self):
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Export Dataset", "", "Comma Separated Values (*.csv)"
        )
        if fileName == '':
            return 0
        else:
            cmd = ["mongoexport", "--db", "bda-project", "--collection", "googleplaystore", "--csv",
                   "--fieldFile", "/home/shehyaaz/Documents/BDA-project/Dataset/headers.txt", "--out", fileName]
            output = subprocess.run(cmd)
            if output.returncode == 0:
                self.alert("success", "Export Successful",
                           "The data was successfully exported")
            else:
                self.alert("error", "Export Unsuccessful",
                           "The data could not be exported :(")

    def insertDocument(self):
        # open form dialog
        dlg = Insert_Document_Dialog(self)
        if dlg.exec_():
            try:
                temp = {}
                temp["App"] = dlg.app.text()
                temp["Category"] = dlg.category.text()
                temp["Rating"] = float(dlg.rating.text())
                temp["Reviews"] = dlg.reviews.text()
                temp["Size"] = dlg.size.text()
                temp["Installs"] = dlg.installs.text()
                temp["Type"] = dlg.type.currentText()
                temp["Price"] = dlg.price.text()
                temp["Content Rating"] = dlg.content_rating.currentText()
                temp["Genres"] = dlg.genres.text()
                temp["Last Updated"] = dlg.last_updated.text()
                temp["Current Ver"] = dlg.current_version.text()
                temp["Android Ver"] = dlg.android_version.text()
                # checking the inserted values
                if not temp["App"]:
                    self.alert("error", "App Name missing",
                               "Please enter the app name")
                    return 0

                temp["Category"] = temp["Category"].replace(
                    " ", "_").upper()
                temp["Reviews"] = 0 if not temp["Reviews"] else int(
                    temp["Reviews"])
                if temp["Size"]:
                    temp["Size"] = re.findall(r'\d+\.?', temp["Size"])[0] + "M"
                if temp["Installs"]:
                    temp["Installs"] = temp["Installs"].replace(
                        ",", "").replace("+", "")
                    temp["Installs"] = f'{int(temp["Installs"]):,}' + "+"
                temp["Price"] = 0.0 if temp["Type"] == "Free" else float(
                    temp["Price"])
                if temp["Last Updated"]:
                    date_obj = datetime.strptime(
                        temp["Last Updated"], "%d/%m/%y")
                    temp["Last Updated"] = date_obj.strftime("%d %B, %Y")

                insert_val = {k: v for k, v in temp.items() if v != ""}
                # print(insert_val)

                if self.mongo_obj.insertDocument(insert_val) is None:
                    self.alert("error", "Document Not Inserted",
                               "The document could not be inserted :(")
                else:
                    self.alert("sucess", "Document Inserted",
                               "The document was successfully inserted :)")
            except ValueError as e:
                self.alert("error", "Wrong Value", str(e))

    def updateDocument(self):
        # open form dialog
        dlg = Update_Document_Dialog(self)
        if dlg.exec_():
            try:
                app = dlg.app_search.text()
                category = dlg.category_search.text()
                # query = {k: v for k, v in temp.items() if v != ""}
                if not app and not category:  # if query is empty
                    self.alert("error", "Update failed",
                               "Please enter search criteria")
                    return 0
                query = {}
                if app:
                    query["App"] = {"$regex": app, "$options": "i"}
                if category:
                    category = category.replace(" ", "_").upper()
                    query["Category"] = {"$regex": category, "$options": "i"}

                temp = {}
                temp["App"] = dlg.app.text()
                temp["Category"] = dlg.category.text()
                temp["Rating"] = float(dlg.rating.text())
                temp["Reviews"] = dlg.reviews.text()
                temp["Size"] = dlg.size.text()
                temp["Installs"] = dlg.installs.text()
                temp["Type"] = dlg.type.currentText()
                temp["Price"] = dlg.price.text()
                temp["Content Rating"] = dlg.content_rating.currentText()
                temp["Genres"] = dlg.genres.text()
                temp["Last Updated"] = dlg.last_updated.text()
                temp["Current Ver"] = dlg.current_version.text()
                temp["Android Ver"] = dlg.android_version.text()
                update_options = dlg.update_options.currentText()
                # checking the values
                temp["Category"] = temp["Category"].replace(
                    " ", "_").upper()
                temp["Reviews"] = "" if not temp["Reviews"] else int(
                    temp["Reviews"])
                temp["Rating"] = "" if not temp["Rating"] else float(
                    temp["Reviews"])
                if temp["Size"]:
                    temp["Size"] = re.findall(r'\d+\.?', temp["Size"])[0] + "M"
                if temp["Installs"]:
                    temp["Installs"] = temp["Installs"].replace(
                        ",", "").replace("+", "")
                    temp["Installs"] = f'{int(temp["Installs"]):,}' + "+"
                temp["Price"] = 0.0 if temp["Type"] == "Free" else float(
                    temp["Price"])
                if temp["Last Updated"]:
                    date_obj = datetime.strptime(
                        temp["Last Updated"], "%d/%m/%y")
                    temp["Last Updated"] = date_obj.strftime("%d %B, %Y")

                update_val = {k: v for k, v in temp.items() if v != ""}
                # print(query)
                # print(update_val)
                multiple = False
                if update_options == "Update All":
                    multiple = True
                res = self.mongo_obj.updateDocument(
                    query, update_val, multiple)
                if res is None or res <= 0:
                    self.alert("error", "Update Failed",
                               "Update was not successful :(")
                else:
                    self.alert("success", "Update Successful",
                               str(res)+" document(s) was updated :)")
            except ValueError as e:
                self.alert("error", "Wrong Value", str(e))

    def deleteDocument(self):
        # open form dialog
        dlg = Delete_Document_Dialog(self)
        if dlg.exec_():
            app = dlg.app.text()
            category = dlg.category.text()
            delete_options = dlg.delete_options.currentText()

            if not app and not category:
                self.alert("error", "Delete failed",
                           "Please enter search criteria")
                return 0
            query = {}
            if app:
                query["App"] = {"$regex": app, "$options": "i"}
            if category:
                category = category.replace(" ", "_").upper()
                query["Category"] = {"$regex": category, "$options": "i"}
            # print(query)
            multiple = False
            if delete_options == "Delete All":
                multiple = True
            res = self.mongo_obj.deleteDocument(query, multiple)
            if res is None or res <= 0:
                self.alert("error", "Delete Failed",
                           "Delete was not successful :(")
            else:
                self.alert("success", "Delete Successful",
                           str(res)+" document(s) was deleted :)")

    def deleteCollection(self):
        if self.mongo_obj.deleteCollection():
            self.alert("success", "Delete Successful",
                       "Collection dropped successfully")
        else:
            self.alert("error", "Delete Unsuccessful",
                       "Collection could not be deleted :(")

    def loadData(self):
        # loads the data from mongodb in the table view
        self.search_text.clear()
        try:
            self.model = DataModel(self.mongo_obj.searchData({}, {"_id": 0}))
            self.proxyModel = QSortFilterProxyModel(self)
            self.proxyModel.setSourceModel(self.model)
            self.tableView.setModel(self.proxyModel)
        except Exception as e:
            self.alert("error", "Load failed", str(e))

    def searchData(self):
        # shows data which matches the text pattern
        text = self.search_text.text()
        if not text:
            self.search_text.clear()
            return 0
        if not hasattr(self, 'proxyModel'):
            self.search_text.clear()
            self.alert("error", "Error", "Please load the data first !")
            return 0
        self.proxyModel.setFilterRegExp("^"+str(text))
        self.proxyModel.setFilterKeyColumn(0)  # search across all columns

    def advSearchData(self):
        # open form dialog
        dlg = Adv_Search_Dialog(self)
        self.search_text.clear()
        if dlg.exec_():
            app = dlg.app.text()
            category = dlg.category.text()
            rating_low = float(dlg.rating_low.text())
            rating_high = float(dlg.rating_high.text())
            reviews_low = dlg.reviews_low.text()
            reviews_high = dlg.reviews_high.text()
            size_low = dlg.size_low.text()
            size_high = dlg.size_high.text()
            installs_low = dlg.installs_low.text()
            installs_high = dlg.installs_high.text()
            price_low = dlg.price_low.text()
            price_high = dlg.price_high.text()
            type = dlg.type.currentText()
            content_rating = dlg.content_rating.currentText()
            genre = dlg.genre.text()
            android_ver = dlg.android_ver.text()
            sort_field = dlg.sort_field.currentText()
            sort_order = dlg.sort_order.currentText()

            # creating the query
            try:
                query = {}
                if not any((app, category, rating_low, rating_high, reviews_low, reviews_high, size_low, size_high, installs_low, installs_high, price_low, price_high, genre, android_ver)) and type == "None" and content_rating == "None" and sort_field == "None":
                    self.alert("error", "Search Failed",
                               "Please enter some values !")
                    return 0
                if app:
                    query["App"] = {"$regex": app, "$options": "i"}
                if category:
                    category = category.replace(" ", "_").upper()
                    query["Category"] = {"$regex": category, "$options": "i"}
                if rating_low != 0.0 or rating_high != 0.0:
                    query["Rating"] = {"$gte": rating_low}
                    if rating_high != 0.0:
                        query["Rating"]["$lte"] = rating_high
                if reviews_low or reviews_high:
                    query["Reviews"] = {"$gte": int(reviews_low)}
                    if reviews_high:
                        query["Rating"]["$lte"] = int(reviews_high)
                if size_low or size_high:
                    size_low = "" if not size_low else re.findall(
                        r'\d+\.?', size_low)[0] + "M"
                    query["Size"] = {"$gte": size_low}
                    if size_high:
                        size_high = re.findall(r'\d+\.?', size_high)[0] + "M"
                        query["Size"]["$lte"] = size_high
                if installs_low or installs_high:
                    if installs_low:
                        installs_low = installs_low.replace(
                            ",", "").replace("+", "")
                        installs_low = f'{int(installs_low):,}' + "+"
                    query["Installs"] = {"$gte": installs_low}
                    if installs_high:
                        installs_high = installs_high.replace(
                            ",", "").replace("+", "")
                        installs_high = f'{int(installs_high)}' + "+"
                        query["Installs"]["$lte"] = installs_high

                if price_low or price_high:
                    query["Price"] = {"$gte": float(price_low)}
                    if price_high:
                        query["Price"]["$lte"] = float(price_high)
                if type != "None":
                    query["Type"] = type
                if content_rating != "None":
                    query["Content Rating"] = content_rating
                if genre:
                    query["Genre"] = {"$regex": genre, "$options": "i"}
                if android_ver:
                    query["Android Ver"] = {
                        "$regex": "^"+android_ver, "$options": "i"}

                # print(query)
                res = None
                if sort_field == "None":
                    res = self.mongo_obj.searchData(query, {"_id": 0})
                else:
                    sort_order = 1 if sort_order == "Asc" else -1
                    res = self.mongo_obj.searchData(
                        query, {"_id": 0}, sort_field, sort_order)

                # load data in the table widget
                self.model = DataModel(res)
                self.proxyModel = QSortFilterProxyModel(self)
                self.proxyModel.setSourceModel(self.model)
                self.tableView.setModel(self.proxyModel)
            except Exception as e:
                self.alert("error", "Search Failed", str(e))

    def displayGraph(self):
        ''' to display graphs '''
        try:
            collection = self.mongo_obj.getCollection()
            text = self.graphs.currentText()
            if text == "None":
                plt.clf()
            elif text == "Distribution of apps - bar graph":  # 1
                barGraphNumApps(collection)
            elif text == "Distribution of free and paid apps":  # 2
                pieChartFreePaidApps(collection)
            elif text == "Distribution of content rating":  # 3
                pieChartContentRating(collection)
            elif text == "Distribution of Android versions":  # 4
                barGraphAndroidVer(collection)
            elif text == "Histogram of App Ratings":
                ratingHistogram(collection, self.figure)
            elif text == "Boxplot of Installs":
                boxPlotInstall(collection, self.figure)
            elif text == "Rating vs Size":
                scatterPlotRatingSize(collection)

            self.canvas.draw()
        except Exception as e:
            self.alert("error", "Error", str(e))

    def getRecommendations(self):
        ''' Use demographic filtering to get recommended apps '''
        try:
            # mongodb query
            x = list(self.mongo_obj.getCollection().aggregate(
                [{"$match": {"Rating": {"$gt": 0}}}, {"$group": {"_id": "_id", "AverageRating": {"$avg": "$Rating"}}}]))
            data = self.mongo_obj.searchData(
                {}, {"_id": 0, "App": 1, "Category": 1, "Rating": 1, "Reviews": 1})
            data.dropna(inplace=True)

            # determine the score of all apps
            C = x[0]["AverageRating"]  # C - average rating for all apps
            # minimum number of reviews required
            m = data["Reviews"].quantile(0.9)
            filter_data = data.copy().loc[data["Reviews"] >= m]
            filter_data['Score'] = self.weighted_rating(filter_data, m, C)
            filter_data = filter_data.sort_values('Score', ascending=False)

            # display results
            dlg = Recommended_Apps_Dialog(self)
            dlg.tableView.setModel(DataModel(filter_data.head(n=20)))
            dlg.show()
        except Exception as e:
            self.alert("error", "Error", str(e))

    def weighted_rating(self, df, m, C):
        v = df['Reviews']
        R = df['Rating']
        # Calculation based on the IMDB formula
        return (v/(v+m) * R) + (m/(m+v) * C)

    def alert(self, type, title, text=None):
        msg = QMessageBox(self)
        if type == "info" or type == "success":
            msg.setIcon(QMessageBox.Information)
        elif type == "error":
            msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        if text != None:
            msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    try:
        sys.exit(app.exec_())
    except Exception as e:
        mainWindow.alert("error", "Error", str(e))
