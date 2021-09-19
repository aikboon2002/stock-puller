import sqlite3 as sl
import pandas as pd
import matplotlib.pyplot as plt
import datetime

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

print("""This program queries relevant information according to your input. 
Enter the name of the company below to view their respective information.""")
while True:
    y = 0
    num = 1
    for x in counters:
        print(str(num) + ". " + x)
        numbers.append(y)
        num += 1
        y += 1
    entry = int(input("Enter the number of the company you wish to query: ")) - 1
    if isinstance(entry, int) and entry in numbers:
        query = counters[entry]
        dateprompt = input("Any specified dates (Y / N)? ").upper()
        if dateprompt == 'N':
            fetch = "SELECT * FROM Stocks WHERE company = ?"
            catch = []
            for row in cur.execute(fetch, (query,)):
                catch.append(row)
            df = pd.DataFrame(catch, columns = ['Company', 'Stock Code', 'Institution', 'Retail', 'Date Added', 'ID'])
            df.plot(x = 'Date Added', y = ['Institution', 'Retail'], kind="bar")
            plt.show()
            retry = input("Would you like to search for another company (Y / N)? ").upper()
            if retry.isalpha() and retry == "N":
                print("Program closed.")
                break          
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
                    df.plot(x = 'Date Added', y = ['Institution', 'Retail'], kind="bar")
                    plt.show()
                    break
            retry = input("Would you like to search for another company (Y / N)? ").upper()
            if retry.isalpha() and retry == "N":
                print("Program closed.")
                break   
        else:
            print("Please enter either Y or N! Try again!")
    else:
        print("Company is not found within the database. Please try again.")