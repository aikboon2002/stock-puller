import sqlite3 as sl
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from dateutil.relativedelta import relativedelta, MO
import PySimpleGUI as sg
import ctypes
import platform

sg.theme('Python')

def make_dpi_aware():
    if int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)

def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD") from None

def weeklydata(a, b):
    date = datetime.datetime.now() + relativedelta(weekday=MO(a))
    prevdate = str(date.strftime("%G") + "-" + date.strftime("%m") + "-" + date.strftime("%d"))
    for row in cur.execute("SELECT Institution, Company FROM Stocks WHERE Date_Added = ?", (prevdate,)):
        if row[0] > 0:
            b.append(row[1])
            b.append(row[0])
    print(prevdate)
    #print(b)
    return b

def compiledata(a, b):
    for row in cur.execute("SELECT Company FROM Stocks"):
            if row[0] in a:
                b.append(row[0])
    b = set(b)
    return b

con = sl.connect('fund-flow.db')
cur = con.cursor()
fetch = cur.execute("SELECT * FROM Stocks")
stash = cur.fetchall()

all_names = []
counters = []
numbers = []

for row in stash:
    all_names.append(row[0])
    [counters.append(x) for x in all_names if x not in counters]

layout = [[sg.Text('Flow Flow Query GUI')],
          [sg.Text('Select the counter to query')],
          [sg.Listbox(counters, size=(60, 30), key='-LIST_COUNTERS-', default_values = 'Singtel', enable_events=True)],
          [sg.Button('Query Single Stock', key='-QUERY-'), sg.Button('Latest Fund Flow', key='-LATEST-')],
          [sg.Button('Positive Fund Flow', key='-POSITIVE-'), sg.Text('# of weeks', size=(8, 1)), sg.Spin(key='-SPIN1-', values=[i for i in range(1, 20)], initial_value=3, size=(6, 1))],
          [sg.Exit()]]

make_dpi_aware()
window = sg.Window('Fund Flow GUI', layout)

while True:  # Event Loop
    event, values = window.read()
    print(event, values)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event == '-QUERY-':
        query = values['-LIST_COUNTERS-'][0]
        fetch = "SELECT * FROM Stocks WHERE company = ?"
        catch = []
        for row in cur.execute(fetch, (query,)):
            catch.append(row)
        df = pd.DataFrame(catch, columns = ['Company', 'Stock Code', 'Institution', 'Retail', 'Date Added', 'ID'])
        ax = df.plot(stacked=True, color=['C2','C3'], x = 'Date Added', y = ['Institution', 'Retail'], kind="bar", title=query, xlabel="Date", ylabel="Vol (millions)")
        for container in ax.containers:
            ax.bar_label(container,fmt='%.1f')
        plt.show()
    if event == '-LATEST-':
        last_monday = datetime.datetime.now() + relativedelta(weekday=MO(-2))
        last_monday_date = str(last_monday.strftime("%G") + "-" + last_monday.strftime("%m") + "-" + last_monday.strftime("%d"))       
        fetchdate = cur.execute("SELECT * FROM Stocks WHERE Date_Added = ?", (last_monday_date,))
        last_monday_date = "SGX Fund Flow " + last_monday_date
        df = pd.DataFrame(fetchdate, columns = ['Company', 'Stock Code', 'Institution', 'Retail', 'Date Added', 'ID'])
        ax = df.plot(stacked=True, color=['C2','C3'], x = 'Company', y = ['Institution', 'Retail'], kind="bar", title=last_monday_date, xlabel="Company", ylabel="Vol (millions)")
        for container in ax.containers:
            ax.bar_label(container,fmt='%.1f')
        plt.show()
    if event == '-POSITIVE-':
        d = {}
        sets = []
        num_of_weeks = int(values['-SPIN1-'])
        for x in range(2, num_of_weeks+2):
            d["data{0}".format(x)] = []
            d["results{0}".format(x)] = []
            d["product{0}".format(x)] = weeklydata(-x, d["data"+str(x)])
            d["var{0}".format(x)] = compiledata(d["product"+str(x)], d["results"+str(x)])
            sets.append(d["var{0}".format(x)])
        var = set.intersection(*sets)
        if len(var) == 0:
            sg.popup('No patterns found.', title='Filter results')
            print("No patterns found.")
        else:
            sg.popup('Counters with {} consecutive weeks of purchases by instituations: \n\n'.format(num_of_weeks), *list(var), '\n', title='Filter results')
            print(var)

con.close()
window.close()