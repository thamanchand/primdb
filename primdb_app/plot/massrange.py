'''
Counting the number of precursor ion masses in a define range from the database data.
'''
import numpy.numarray as na
import matplotlib.pyplot as plt
import psycopg2

#establish connection with the postgres server with the given configuration
conn = psycopg2.connect(host="localhost",user="primuser",password="web",database="primdb")
rangelow = [200,400,800,1200,1600] #
rangehigh = [400,800,1200,1600,2000]
masscount = []
cur = conn.cursor()
for mlow, mhigh in (zip(rangelow, rangehigh)):
    #fetch the number of precursor ion mass with the given range, for eg [200-400] and append it to masscount list
    cur.execute("SELECT monoiso FROM primdb_app_selectedion where monoiso BETWEEN '%d' AND '%d'" %(mlow,mhigh))
    masscount.append(cur.rowcount)

labels = ["200-400", "400-800","800-1200","1200-1600","1600-2000"]
maxitem = max(masscount) +1000
colors = ['r','g','y','b','b']
xlocations = na.array(range(len(masscount)))+0.5
width = 0.7
plt.bar(xlocations, masscount,  width=width, color=colors)
plt.xticks(xlocations+ width/2, labels)
plt.xlim(0, xlocations[-1]+width*2)
plt.ylabel("Count per mass range")
plt.xlabel("M/Z")
for x,y in zip(xlocations,masscount):
    plt.text(x+0.4, y, '%.2d' % y, ha='center', va= 'bottom')
#change the directory according to your application path.
plt.savefig(r'D:/Dropbox/Dropbox/primdb/assets/img/statistics1.png', dpi=100, transparent=True)
