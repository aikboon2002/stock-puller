import pandas as pd
import requests
import sqlite3 as sl
import csv
import datetime

con = sl.connect('fund-flow.db')
cur = con.cursor()
#con.execute('DROP TABLE Stocks')
con.execute('''CREATE TABLE IF NOT EXISTS Stocks (
            Company TEXT,
            Stock_Code VARCHAR(255),
            Institution REAL,
            Retail REAL,
            Date_Added VARCHAR(255),
            ID INTEGER PRIMARY KEY AUTOINCREMENT
        ); ''')

counter = datetime.datetime.now()
day = counter.strftime("%d")
month = counter.strftime("%m")
month_short = counter.strftime("%b")
year = counter.strftime("%G")
today = str(day + " " + month_short + " " + year)

# 7 days ago
past = datetime.datetime.now() - datetime.timedelta(days=7)
pday = past.strftime("%#d")
paddedpday = past.strftime("%d")
pmonth = past.strftime("%m")
pmonth_short = past.strftime("%b")
pyear = past.strftime("%G")
pdate = str(pyear + "-" + pmonth + "-" + paddedpday)

url = ("https://api2.sgx.com/sites/default/files/" + year + "-" + month + "/SGX Fund Flow Weekly Tracker %28Week of " + pday + " " + pmonth_short + " " + pyear + "%29.xlsx")
excel = "SGX Fund Flow Weekly Tracker (Week of " + pday + " " + pmonth_short + " " + pyear + ").xlsx"
txt = "SGX Fund Flow Weekly Tracker (Week of " + pday + " " + pmonth_short + " " + pyear + ").csv"

try:
    dl = requests.get(url)
    dl.raise_for_status()
except requests.exceptions.HTTPError as error:
    raise SystemExit(error)
else:
    with open(excel, 'wb') as output:
        output.write(dl.content)
    
read = pd.read_excel(excel, sheet_name='STI Constituents', header=1, skipfooter=8)
read.to_csv(txt, index=None, header=True)
with open(txt, newline='') as csvfile:
    stats = csv.reader(csvfile, delimiter=',')
    rows = list(stats)
    for x in range(len(rows)):
        rows[x].append(pdate)
        con.execute("INSERT INTO Stocks (Company, Stock_Code, Institution, Retail, Date_Added) VALUES (?, ?, ?, ?, ?)", (rows[x][0], rows[x][1], rows[x][2], rows[x][3], rows[x][4]))
con.commit()
con.close()
