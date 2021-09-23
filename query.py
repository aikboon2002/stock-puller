import sqlite3 as sl
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from dateutil.relativedelta import relativedelta, MO
from os import system, name

# define our clear function
def clear(): 
    # for windows
    if name == 'nt':
        _ = system('cls')
  
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

con = sl.connect('fund-flow.db')
cur = con.cursor()
fetch = cur.execute("SELECT * FROM Stocks")

stash = cur.fetchall()

def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD") from None

all_names = []
counters = []
numbers = []

for row in stash:
    all_names.append(row[0])
    [counters.append(x) for x in all_names if x not in counters]

while True:
    clear()
    print("""This program queries relevant information according to your input. 
    Enter the name of the company below to view their respective information.""")
    y = 0
    num = 1
    for x in counters:
        print(str(num) + ". " + x)
        numbers.append(y)
        num += 1
        y += 1
    user_input = int(input("Enter the number of the company you wish to query. '0' to exit. "))
    entry = user_input - 1
    if isinstance(entry, int) and entry in numbers:
        query = counters[entry]
        dateprompt = input("Any specified dates (Y / N)? ").upper()
        if dateprompt == 'N':
            fetch = "SELECT * FROM Stocks WHERE company = ?"
            catch = []
            for row in cur.execute(fetch, (query,)):
                catch.append(row)
            df = pd.DataFrame(catch, columns = ['Company', 'Stock Code', 'Institution', 'Retail', 'Date Added', 'ID'])
            ax = df.plot(stacked=True, color=['C2','C3'], x = 'Date Added', y = ['Institution', 'Retail'], kind="bar", title=query, xlabel="Date", ylabel="Vol (millions)")
            for container in ax.containers:
                ax.bar_label(container,fmt='%.1f')
            plt.show()        
        elif dateprompt == 'Y':
            query = counters[entry]
            while True: 
                startdate = input("Please enter starting date (YYYY-MM-DD): ")
                validate(startdate)
                enddate = input("Please enter end date (YYYY-MM-DD): ")
                validate(enddate)
                if startdate > enddate:
                    print("The starting date is larger than the end date! Please try again!")
                else:
                    duration = pd.date_range(start=startdate, end=enddate)
                    recall = cur.execute("SELECT Date_Added FROM Stocks")
                    dates = []
                    for row in recall:
                        if row[0] in duration:
                            dates.append(row[0])
                    fetchdate = cur.execute("SELECT * FROM Stocks WHERE Date_Added IN (%s)"% ("?," * len(dates))[:-1], dates)
                    catchdate = []
                    for row in fetchdate:
                        catchdate.append(row)
                    fetchname = "SELECT * FROM Stocks WHERE company = ?"
                    catchname = []
                    for row in cur.execute(fetchname, (query,)):
                        catchname.append(row)
                    result = set(catchname).intersection(catchdate)
                    df = pd.DataFrame(result, columns = ['Company', 'Stock Code', 'Institution', 'Retail', 'Date Added', 'ID'])
                    ax = df.plot(stacked=True, color=['C2','C3'], x = 'Date Added', y = ['Institution', 'Retail'], kind="bar", title=query, xlabel="Date", ylabel="Vol (millions)")
                    for container in ax.containers:
                        ax.bar_label(container,fmt='%.1f')
                    plt.show()
                    break
        else:
            print("Please enter either Y or N! Try again!")
    elif user_input == 999:
        last_monday = datetime.datetime.now() + relativedelta(weekday=MO(-2))
        last_monday_date = str(last_monday.strftime("%G") + "-" + last_monday.strftime("%m") + "-" + last_monday.strftime("%d"))       
        fetchdate = cur.execute("SELECT * FROM Stocks WHERE Date_Added = ?", (last_monday_date,))
        last_monday_date = "SGX Fund Flow " + last_monday_date
        df = pd.DataFrame(fetchdate, columns = ['Company', 'Stock Code', 'Institution', 'Retail', 'Date Added', 'ID'])
        ax = df.plot(stacked=True, color=['C2','C3'], x = 'Company', y = ['Institution', 'Retail'], kind="bar", title=last_monday_date, xlabel="Company", ylabel="Vol (millions)")
        for container in ax.containers:
            ax.bar_label(container,fmt='%.1f')
        plt.show()
    elif user_input == 0:
            break
    else:
        print("Company is not found within the database. Please try again.")