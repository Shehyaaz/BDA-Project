import pymongo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PyQt5 import QtCore, QtWidgets


def ratingHistogram(col, fig):
    ''' Histogram of App Ratings '''
    plt.clf()
    # mongodb query
    data = pd.DataFrame(
        list(col.find({}, {"_id": 0, "Rating": 1})))
    ax = fig.add_subplot(111)
    data.hist(bins=50, ax=ax)  # histogram of ratings


def barGraphNumApps(col):
    ''' Bar graph of number of apps in each Category '''
    plt.clf()  # clear the current figure
    # mongodb query
    x = list(col.aggregate(
        [{"$group": {"_id": "$Category", "number": {"$sum": 1}}}]))
    yval = []
    xval = []
    for doc in x:
        xval.append(doc['_id'])
        yval.append(doc['number'])

    # horizontal bar graph
    plt.barh(xval, yval, color=('deepskyblue',
                                'palegreen', 'orangered', 'gold'))
    plt.xlabel('No. of Apps')
    plt.ylabel("Categories")
    for i, v in enumerate(yval):
        plt.text(v + 3, i-0.25, str(v), color='black', fontsize=5)
    plt.yticks(rotation=0, fontsize=5)
    plt.title('Distribution of Apps across Categories')


def barGraphAndroidVer(col):
    ''' Bar graph of Android Version '''
    plt.clf()  # clear the current figure
    # mongodb query
    x = list(col.aggregate(
        [{"$group": {"_id": "$Android Ver", "number": {"$sum": 1}}}]))
    yval = []
    xval = []
    for doc in x:
        if str(doc['_id']) != "nan":
            xval.append(str(doc['_id']))
            yval.append(doc['number'])

    # bargraph
    plt.barh(xval, yval, color=('slategrey', 'lightcoral', 'orangered', 'gold'))
    plt.xlabel('Android Version')
    plt.ylabel("No.of Apps")
    for i, v in enumerate(yval):
        plt.text(v + 3, i-0.25, str(v), color='black', fontsize=5)
    plt.yticks(rotation=0, fontsize=5)
    plt.title('Distribution of Android Versions')


def pieChartContentRating(col):
    ''' Pie chart of Content Rating of apps as per Age '''
    plt.clf()  # clear the current figure
    x = list(col.aggregate(
        [{"$group": {"_id": "$Content Rating", "number": {"$sum": 1}}}]))
    yval = []
    xval = []
    for doc in x:
        xval.append(doc['_id'])
        yval.append(doc['number'])

    colors = ['gold', 'palegreen', 'tomato', 'lightcoral', 'deepskyblue']

    plt.pie(yval, labels=xval, explode=[0.03]*len(yval), colors=colors, radius=0.6, startangle=290, shadow=False,
            autopct='%1.2f%%', rotatelabels=0)
    plt.title('Content Rating on Playstore')
    plt.axis('equal')


def pieChartFreePaidApps(col):
    ''' Pie chart of free and paid apps '''
    plt.clf()  # clear the current figure
    x = list(col.aggregate(
        [{"$group": {"_id": "$Type", "number": {"$sum": 1}}}]))
    yval = []
    xval = []
    for doc in x:
        xval.append(doc['_id'])
        yval.append(doc['number'])

    colors = ['lightgrey', 'lightcoral']

    plt.pie(yval, labels=xval, explode=[0.03]*len(yval), colors=colors, radius=0.6, startangle=20, shadow=False,
            autopct='%1.2f%%', rotatelabels=0)
    plt.title('Distribution of Free and Paid apps')
    plt.axis('equal')


def scatterPlotRatingSize(col):
    ''' scatter plot of install vs size '''
    plt.clf()  # clear the current figure
    data = pd.DataFrame(
        list(col.find({}, {"_id": 0, "Rating": 1, "Size": 1})))
    # data.head()
    data["Rating"].dropna(inplace=True)

    # The size column has M which denotes Mb so we need to make it in numeric values too
    data["Size"].dropna(how='any', inplace=True)
    arr = data['Size'].values
    temp = []
    for i in range(len(arr)):
        if arr[i] == 'Varies with device':
            temp.append(21.51)  # approximate value
        elif 'k' in arr[i]:
            arr[i] = arr[i].replace('k', '')
            arr[i] = float(arr[i])/1000
            temp.append(arr[i])
        elif 'G' in arr[i]:
            arr[i] = arr[i].replace('G', '')
            arr[i] = float(arr[i])*1000
            temp.append(arr[i])
        elif 'M' in arr[i]:
            arr[i] = arr[i].replace('M', '')
            arr[i] = float(arr[i])
            temp.append(arr[i])
    data['Size'] = temp
    # Now plot with matplotlib
    plt.title("Rating Vs. App Size")
    plt.xlabel("App Size")
    plt.ylabel("Rating")
    plt.scatter(data.Size, data.Rating, s=10,
                c=data.Rating, marker='*', cmap='plasma')


def boxPlotInstall(col, fig):
    ''' Box plot of installs, grouped according to type '''
    plt.clf()  # clear the current figure
    data = pd.DataFrame(
        list(col.find({}, {"_id": 0, "Installs": 1, "Type": 1})))
    data.dropna(inplace=True)
    data["Installs"] = data["Installs"].str.replace(",", "")
    data["Installs"] = data["Installs"].str.replace("+", "")
    data["Installs"] = pd.to_numeric(data["Installs"])
    data = data[data!=0].dropna()
    data["Installs"] = np.log10(data["Installs"])  # converting to log 10 scale

    ax = fig.add_subplot(111)
    data.boxplot(by="Type", column=[
        "Installs"], ax=ax)
    plt.title("Boxplot of Installs(log-scale) grouped by Type")
    plt.suptitle("")
