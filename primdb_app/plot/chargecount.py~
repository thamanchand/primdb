'''
Counting the charge statistics from the database data.
'''

import psycopg2
import numpy.numarray as na
import matplotlib.pyplot as plt

#establish connection with the postgres server with the given configuration
conn = psycopg2.connect(host="localhost",user="primuser",password="web",database="primdb")
charges = [0,1,2,3,4]

chargecount = []
cur = conn.cursor()
for c in charges:
    #fetch all the number of charge record from the table where where charge is 2 and 3 and 4
	#and append to it the charges list for plotting
    cur.execute("SELECT chargestate FROM primdb_app_selectedion where chargestate ='%d'" %(c))
    chargecount.append(cur.rowcount)

#fetch the number of charge record from the table where where charge is greater than 4
#and append to it the charges list for plotting
cur.execute("SELECT chargestate FROM primdb_app_selectedion where chargestate >'4'")
chargecount.append(cur.rowcount)

labels = ["0", "1","2", "3","4",">5"]
maxitem = max(chargecount) +1000
colors = ['r','g', 'm','c','k','w']
xlocations = na.array(range(len(chargecount)))+0.5
width = 0.7
plt.bar(xlocations, chargecount,  width=width, color=colors)
plt.xticks(xlocations+ width/2, labels)
plt.xlim(0, xlocations[-1]+width*2)
plt.xlabel("Charge")
plt.ylabel("Count per charge")
for x,y in zip(xlocations,chargecount):
    plt.text(x+0.4, y, '%.2d' % y, ha='center', va= 'bottom')
#change the directory according to your application path.
plt.savefig(r'D:/Dropbox/Dropbox/primdb/assets/img/statistics2.png', dpi=100, transparent=True)
