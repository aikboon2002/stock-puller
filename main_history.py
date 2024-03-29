import pandas as pd
import requests
import sqlite3 as sl
import csv
import datetime
import os
import glob
from datetime import date
from dateutil.relativedelta import relativedelta, MO

# Note: This script will delete all existing data in your existing database
#       This script should run once if you are populating a new db

# Number of weeks of historical data to pull from SGX
history_loop_count = 26

con = sl.connect('fund-flow.db')
cur = con.cursor()
con.execute('DROP TABLE Stocks')
con.execute('''CREATE TABLE IF NOT EXISTS Stocks (
            Company TEXT,
            Stock_Code VARCHAR(255),
            Institution REAL,
            Retail REAL,
            Date_Added VARCHAR(255),
            ID INTEGER PRIMARY KEY AUTOINCREMENT
        ); ''')

today = date.today()
last_monday = today + relativedelta(weekday=MO(-1))
last_monday = last_monday + relativedelta(weekday=MO(-history_loop_count))

for i in range(history_loop_count):
    day = last_monday.strftime("%d")
    month = last_monday.strftime("%m")
    if (last_monday.month==6 or last_monday.month==7) and last_monday.year==2022:
        month_short = last_monday.strftime("%B")
    else:
        month_short = last_monday.strftime("%b")
    year = last_monday.strftime("%G")

    # 7 days ago
    past = last_monday + relativedelta(days=-7)
    pday = past.strftime("%#d")
    paddedpday = past.strftime("%d")
    pmonth = past.strftime("%m")
    if past.month>=6 and past.year>=2022:
        if past.month==8 or past.month==9 or past.month==10:
            pmonth_short = past.strftime("%b")
        else:
            pmonth_short = past.strftime("%B")
    else:
        pmonth_short = past.strftime("%b")
    pyear = past.strftime("%G")
    pdate = str(pyear + "-" + pmonth + "-" + paddedpday)

    url = ("https://api2.sgx.com/sites/default/files/" + year + "-" + month + "/SGX Fund Flow Weekly Tracker %28Week of " + pday + " " + pmonth_short + " " + pyear + "%29.xlsx")
    excel = "SGX Fund Flow Weekly Tracker (Week of " + pday + " " + pmonth_short + " " + pyear + ").xlsx"
    txt = "SGX Fund Flow Weekly Tracker (Week of " + pday + " " + pmonth_short + " " + pyear + ").csv"

    # Offset last monday by -1 week
    last_monday = last_monday + relativedelta(days=7)

    try:
        dl = requests.get(url)
        dl.raise_for_status()
    except requests.exceptions.HTTPError as error:
        raise SystemExit(error)
    else:
        with open(excel, 'wb') as output:
            output.write(dl.content)

    # Parse Weekly STI constituents tab for STI index stocks        
    read = pd.read_excel(excel, sheet_name='STI Constituents', header=1, skipfooter=8)
    read.to_csv(txt, index=None, header=True)
    with open(txt, newline='') as csvfile:
        stats = csv.reader(csvfile, delimiter=',')
        rows = list(stats)
        for x in range(len(rows)):
            if rows[x][0] == 'Overall Net Buy (+) / Net Sell (-) (S$M)':
                break
            rows[x].append(pdate)
            con.execute("INSERT INTO Stocks (Company, Stock_Code, Institution, Retail, Date_Added) VALUES (?, ?, ?, ?, ?)", (rows[x][0], rows[x][1], rows[x][2], rows[x][3], rows[x][4]))
        
    # Parse Weekly Top 10 tab for non-STI index stocks
    top_10_list = []
    for i in range(20):
        top_10_list.append([])

    # Process Institution Top 10 net buy and net sell
    read = pd.read_excel(excel, sheet_name='Weekly Top 10', header=5, skiprows = range(15, 28), skipfooter=12)
    read.to_csv(txt, index=None, header=True)
    with open(txt, newline='') as csvfile:
        stats = csv.reader(csvfile, delimiter=',')
        rows_top10 = list(stats)
        for x in range(len(rows_top10)):
            # Net buy
            if not any(rows_top10[x][0] in y for y in rows):
                for z in range(3):
                    top_10_list[x].append(rows_top10[x][z])
                top_10_list[x].append('0')
                top_10_list[x].append(pdate)
            # Net sell
            if not any(rows_top10[x][3] in y for y in rows):            
                for z in range(3, 6):
                    top_10_list[10+x].append(rows_top10[x][z])
                top_10_list[10+x].append('0')
                top_10_list[10+x].append(pdate)
        for top_10 in top_10_list:
            if top_10 != []:
                con.execute("INSERT INTO Stocks (Company, Stock_Code, Institution, Retail, Date_Added) VALUES (?, ?, ?, ?, ?)", (top_10[0], top_10[1], top_10[2], top_10[3], top_10[4]))

    print("Done updating database with", url)

con.commit()
con.close()

# Clean up intermediate files
files = glob.glob('*.csv')
files.extend(glob.glob('*.xlsx'))
#print (files)
for f in files:
    try:
        os.remove(f)
        #print ("Removed", f)
    except OSError as e:
        print("Error: %s : %s" % (f, e.strerror))
