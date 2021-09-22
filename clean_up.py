import os
import glob

files = glob.glob('*.csv')
files.extend(glob.glob('*.xlsx'))
#print (files)
for f in files:
    try:
        os.remove(f)
        print ("Removed", f)
    except OSError as e:
        print("Error: %s : %s" % (f, e.strerror))

