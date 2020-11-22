import mongoConnect
from pymongo import MongoClient
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

from PyQt5 import QtCore, QtWidgets
# histogram of number of apps in each Genre
def histogram():
    yval=[]
    xval = []
    db = mongoConnect.mongoconnect()
    x = list(db.google_playstore_apps.aggregate([{"$group": {"_id": "$Category", "number": {"$sum": 1}}}]))
    for doc in x:
        xval.append(doc['_id'])
        yval.append(doc['number'])
    n_bins = 200
    # x = np.random.randn(10000, 3)

    # colors = ['green']*xval

    plt.hist(xval, n_bins, density=True,histtype='bar',color='r',label=yval)
    plt.legend(prop={'size': 10})
    plt.title('Category',fontweight="bold")
    # plt.show()
    # plt.show()



# Bar graph of number of apps in each Genre
def barGraph1():
    #mongodb query
    db = mongoConnect.mongoconnect()
    x = list(db.google_playstore_apps.aggregate([{"$group": {"_id": "$Category", "number": {"$sum": 1}}}]))
    yval=[]
    xval = []
    for doc in x:
        xval.append(doc['_id'])
        yval.append(doc['number'])

    # matplot bargraph
    plt.barh(xval,yval, color=('deepskyblue', 'palegreen', 'orangered','gold'))
    plt.xlabel('No. of Apps')
    plt.ylabel("Category")
    for i, v in enumerate(yval):
        plt.text(v + 3, i-0.25, str(v), color='black', fontsize=5)
    plt.yticks(rotation=0, fontsize=5, fontname='roboto')
    plt.title('Categories of number of Apps')
    # plt.show()
# Bar graph of number of apps in each Genre
def barGraph2():
    #mongodb query
    db = mongoConnect.mongoconnect()
    x = list(db.google_playstore_apps.aggregate([{"$group": {"_id": "$Android Ver", "number": {"$sum": 1}}}]))
    yval=[]
    xval = []
    for doc in x:
        xval.append(str(doc['_id']))
        yval.append(doc['number'])

    # matplot bargraph
    plt.barh(xval,yval, color=('slategrey','dodgerblue', 'orangered','gold'))
    plt.xlabel('Type of Apps')
    plt.ylabel("No.of Apps")
    for i, v in enumerate(yval):
        plt.text(v + 3, i-0.25,str(v), color='black', fontsize=4)
    plt.yticks(rotation=0, fontsize=5, fontname='roboto')
    plt.title('Categories of number of Apps')
    # plt.show()


# Pie chart of Content Rating of apps as per Age

def pieChart1():
    db = mongoConnect.mongoconnect()
    x = list(db.google_playstore_apps.aggregate([{"$group": {"_id": "$Content Rating", "number": {"$sum": 1}}}]))
    yval = []
    xval = []
    for doc in x:
        xval.append(doc['_id'])
        yval.append(doc['number'])
    fig = plt.figure()

    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('equal')
    ax.text(-0.4, 0.7, 'Content Rating as per Age', color='black', fontsize=15)
    colors = ['gold','palegreen','tomato','darkblue','deepskyblue']



    plt.pie(yval, labels=xval,explode=[0.03]*len(yval), colors=colors, radius=0.6, startangle=290, shadow=False,
             autopct='%1.2f%%',rotatelabels=0)
    # print(xval)
    # print(yval)

    # plt.show()


# Pie chart of number of apps in each Category
def pieChart2():
    db = mongoConnect.mongoconnect()
    x = list(db.google_playstore_apps.aggregate([{"$group": {"_id": "$Type", "number": {"$sum": 1}}}]))
    yval = []
    xval = []
    t = mongoConnect.mongoconnect()
    for doc in x:
        xval.append(doc['_id'])
        yval.append(doc['number'])
    fig = plt.figure()

    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('equal')
    ax.text(-0.4, 0.7, 'Types of App in Playstore', color='black', fontsize=15)
    colors = ['lightgrey','lightcoral','gold','darkblue','deepskyblue']

     # sizes = [1500, 600, 500, 300]


    plt.pie(yval, labels=xval,explode=[0.03]*len(yval), colors=colors, radius=0.6, startangle=20, shadow=False,
             autopct='%1.2f%%',rotatelabels=0)
    # print(xval)
    # print(yval)

    # plt.show()

#scatter plot of install vs size
def scatterplot():
    db = mongoConnect.mongoconnect()
    collection = db.google_playstore_apps
    data = pd.DataFrame(list(collection.find()))
    # x = list(db.google_playstore_apps.find())
    arr = data['Installs']
    for i in range(len(arr)):
        if arr[i] == 'Free':
            arr[i] = 1000
        else:
            arr[i] = arr[i].replace('+', '').replace(',', '')
            arr[i] = float(arr[i])
    data['Installs'] = arr
    # The size column has M which denotes Mb so we need to make it in numeric values too
    arr = data['Size'].values
    vr = []
    for i in range(len(arr)):
        if arr[i] == 'Varies with device':
            vr.append(21.51)
        elif 'M' in arr[i]:
            arr[i] = arr[i].replace('M', '')
            arr[i] = float(arr[i])
            vr.append(arr[i])
        elif 'k' in arr[i]:
            arr[i] = arr[i].replace('k', '')
            arr[i] = float(arr[i]) / 1000
            vr.append(arr[i])
        elif 'G' in arr[i]:
            arr[i] = arr[i].replace('G', '')
            arr[i] = float(arr[i]) * 1000
            vr.append(arr[i])
        else:
            vr.append(1000)
    data['Size'] = vr
    mydata = data[["Installs", "Size"]].dropna(how="any")
    # Now plot with matplotlib
    vals = mydata.values
    plt.title("No. of Installs per size of the app")
    plt.xlabel("No. of Installs")
    plt.ylabel("Size of the app")
    # fig, ax = plt.subplots()
    plt.scatter(vals[:, 0], vals[:, 1],s=2,c=vals[:, 1],marker='.',cmap='plasma')


# Box plot of installs, grouped according to type
def boxplot():
    db = mongoConnect.mongoconnect()
    collection = db.google_playstore_apps
    data = pd.DataFrame(list(collection.find()))
    # x = list(db.google_playstore_apps.find())
    arr = data['Installs']
    x = list(db.google_playstore_apps.aggregate([{"$group": {"_id": "$Type", "number": {"$sum": 1}}}]))
    yval = []
    xval = []
    arr = data['Installs']
    for i in range(len(arr)):
        if arr[i] == 'Free':
            arr[i] = 1000
        else:
            arr[i] = arr[i].replace('+', '').replace(',', '')
            # arr[i] = float(arr[i])
    data['Installs'] = arr
    for doc in x:
        xval.append(doc['_id'])
    print(data)
    data.boxplot(by=['Type'],coloumn=['Installs'])
    plt.show()