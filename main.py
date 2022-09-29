import PySimpleGUI as sg
import datareader as datareader
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tinydb import TinyDB, Query
import tkinter as tk
import datetime as dt


# set variable
db = TinyDB('data.json')
stock = 'TSM'
data = yf.download(tickers=stock, period='1d', interval='1m')
balance_set = 0
stock_list = []
stock_dict = {}
date_dict = {}
# button funtion
def Robot_start(new_stock):
    global date_dict
    date = dt.date.today()
    result = db.search(User.name == "robotstock")
    date_dict.update({new_stock: str(date)})
    db.update({"buytime": date_dict}, User.name == "robotstock")

def Robot_run(new_stock):
    global date_dict, stock_dict, balance_set
    todaydate = dt.date.today()
    startdate = date_dict.get(new_stock)
    tsm = yf.download(new_stock, start=startdate, end=todaydate)
    a = tsm.Close
    #startprice = stock_dict.get(new_stock)
    balance_set += a[len(a)-1]
    add_balance()

def Robot_end(new_stock):
    global date_dict
    Robot_run(new_stock)
    result = db.search(User.name == "robotstock")
    del date_dict[new_stock]
    db.update({"buytime": date_dict}, User.name == "robotstock")

# stock purchase day
def update_date():
    global date_dict
    result = db.search(User.name == "robotstock")
    date_dict = result[0]['buytime']

# add to database
def insert_data():
    db.insert({'balance': 5000})
    db.insert({'stock':stock_list})
    insert_data()

User = Query()
# update balance
def update_balance():
    global balance_set
    result = db.search(User.name == "user1")
    balance_set = result[0]['balance']
def add_balance():
    global balance_set
    result = db.search(User.name == "user1")
    db.update({"balance": balance_set}, User.name == "user1")
# add stock ticket to list box
def update_stock_list():
    global  stock_list
    result = db.search(User.name == "userstock")
    stock_list = result[0]['stock']

def upload_stock_list(new_stock):
    global stock_list
    result = db.search(User.name == "userstock")
    stock_list.append(new_stock)
    db.update({"stock":stock_list}, User.name == "userstock")

def change_balance(new_stock):
    global balance_set
    result = db.search(User.name == "user1")
    ticker = yf.Ticker(new_stock)
    todays_data = ticker.history(period='1d')
    price = todays_data['Close'][0]
    balance_set = balance_set - price
    db.update({"balance": balance_set}, User.name == "user1")

def upload_stock_dict(new_stock):
    global stock_dict
    result = db.search(User.name == "userstock")
    ticker = yf.Ticker(new_stock)
    todays_data = ticker.history(period='1d')
    price = todays_data['Close'][0]
    stock_dict.update({new_stock:price})
    change_balance(new_stock)
    update_balance()
    db.update({"stockprice": stock_dict}, User.name == "userstock")

def update_stock_dict():
    global stock_dict
    result = db.search(User.name == "userstock")
    stock_dict = result[0]['stockprice']

def delete_stock_list(new_stock):
    global stock_list
    result = db.search(User.name == "userstock")
    stock_list.remove(new_stock)
    db.update({"stock": stock_list}, User.name == "userstock")

def delete_stock_dict(new_stock):
    global stock_dict
    result = db.search(User.name == "userstock")
    del stock_dict[new_stock]
    db.update({"stockprice": stock_dict}, User.name == "userstock")
#update data
def update():
    update_balance()
    update_stock_list()
    update_stock_dict()
    update_date()

update()


def create_plot():
    data.Close.plot()
    plt.title(stock, fontsize=14)
    plt.xlabel('Date Time', fontsize=14)
    plt.ylabel('Stock Price (USD per Shares)', fontsize=14)
    plt.grid(True)
    return plt.gcf()

sg.theme('Material2')

layout = [
            [sg.Text('Stock Trading System', font = ("Arial", 30), background_color=('white'), text_color=('Blue')),
             sg.Push(), sg.Push(), sg.Text('Balance', font = ("Arial", 30)), sg.Push()],
            [sg.Button('1D', visible=True, button_color=('white', 'blue'), font = ("Arial", 15)),
                sg.pin(sg.Button('5D', visible=True, button_color=('white', 'blue'), font = ("Arial", 15))),
                sg.pin(sg.Button('1M', visible=True, button_color=('white', 'blue'), font = ("Arial", 15))),
                sg.pin(sg.Button('6M', visible=True, button_color=('white', 'blue'), font = ("Arial", 15))),
                sg.pin(sg.Button('1Y', visible=True, button_color=('white', 'blue'), font = ("Arial", 15))),
                sg.pin(sg.Button('MAX', visible=True, button_color=('white', 'blue'), font = ("Arial", 15))),
                sg.Push(), sg.Push(), sg.Push(), sg.Push(), sg.Push(), sg.Text("USD "+str(balance_set), font = ("Arial", 30), key='-TEXT-'), sg.Push(), sg.Push()],
            [sg.Canvas(size=(400, 800), key="-CANVAS-")],
            [sg.Text('Ticker: ', key = '_text1_', font = ("Arial", 15)), sg.InputText(key='_IN_', size=(40, 15), do_not_clear=True),
             sg.Submit('send')],
            [sg.Button('ROBOT START', visible=True, button_color=('white', 'blue'), font = ("Arial", 15)),
                sg.pin(sg.Button('ROBOT END', visible=True, button_color=('white', 'blue'), font = ("Arial", 15))),  sg.Push(),
             sg.Listbox(values=stock_list, size=(30,10), enable_events=True, key="-LIST-", background_color=('white'), text_color="black", highlight_text_color="green", highlight_background_color="yellow"), sg.Push()],
        ]
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both')
    return figure_canvas_agg

def delete_figure_agg(figure_agg):
    figure_agg.get_tk_widget().forget()
    plt.close('all')

window = sg.Window('Stock', layout, size=(1366, 768), auto_size_text=True, finalize=True)

figure_agg = draw_figure(window['-CANVAS-'].TKCanvas, create_plot())
while True:
    event, values = window.read()
    if event == '1D':
        delete_figure_agg(figure_agg)
        data = yf.download(tickers=stock, period='1d', interval='1m')
        figure_agg = draw_figure(window['-CANVAS-'].TKCanvas, create_plot())

    if event == '5D':
        delete_figure_agg(figure_agg)
        data = yf.download(tickers=stock, period='5d', interval='5m')
        figure_agg = draw_figure(window['-CANVAS-'].TKCanvas, create_plot())
    if event == '1M':
        delete_figure_agg(figure_agg)
        data = yf.download(tickers=stock, period='1mo', interval='15m')
        figure_agg = draw_figure(window['-CANVAS-'].TKCanvas, create_plot())
    if event == '6M':
        delete_figure_agg(figure_agg)
        data = yf.download(tickers=stock, period='6mo', interval='1d')
        figure_agg = draw_figure(window['-CANVAS-'].TKCanvas, create_plot())
    if event == '1Y':
        delete_figure_agg(figure_agg)
        data = yf.download(tickers=stock, period='1y', interval='1d')
        figure_agg = draw_figure(window['-CANVAS-'].TKCanvas, create_plot())
    if event == 'MAX':
        delete_figure_agg(figure_agg)
        data = yf.download(tickers=stock, period='max', interval='1wk')
        figure_agg = draw_figure(window['-CANVAS-'].TKCanvas, create_plot())
    if event == 'send':
        stock = values['_IN_']
        delete_figure_agg(figure_agg)
        data = yf.download(tickers=stock, period='1d', interval='1m')
        figure_agg = draw_figure(window['-CANVAS-'].TKCanvas, create_plot())
    if event == 'ROBOT START':
        if stock_list.count(stock) == 0:
            upload_stock_list(stock)
            upload_stock_dict(stock)
            Robot_start(stock)
            window['-TEXT-'].update("USD "+str(balance_set))
            window['-LIST-'].update(stock_list)
        else:
            tk.messagebox.showinfo(title="ERROR", message="YOU HAVE ALREADY START IT")
    if event == 'ROBOT END':
        if stock_list.count(stock) == 0:
            tk.messagebox.showinfo(title="ERROR", message="IT HAVEN'T START IT")
        else:
            delete_stock_list(stock)
            delete_stock_dict(stock)
            Robot_end(stock)
            window['-TEXT-'].update("USD " + str(balance_set))
            window['-LIST-'].update(stock_list)

    if event == sg.WIN_CLOSED:
        break

window.close()