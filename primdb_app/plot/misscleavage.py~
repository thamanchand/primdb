'''
Counting the number of misscleavage statistics from the database data.
'''
import psycopg2
import numpy.numarray as na
import matplotlib.pyplot as plt

#establish connection with the postgres server with the given configuration
conn = psycopg2.connect(host="localhost",user="primuser",password="web",database="primdb")
misscleavage = [0,1,2]
misscount = []
cur = conn.cursor()
for miss in misscleavage:
    #fetch all the number of missed cleavage record from the table where where cleavage is 0 and 1 and 2
	#and append to it misscount list for plotting
    cur.execute("SELECT num_missed_cleavage FROM primdb_app_search_hit where num_missed_cleavage ='%d'" %(miss))
    misscount.append(cur.rowcount)

labels = ["0", "1","2"]
maxitem = max(misscount) +1000
colors = ['red','grey','cyan']
xlocations = na.array(range(len(misscount)))+0.5
width = 0.7
plt.bar(xlocations, misscount,  width=width, color=colors)
plt.xticks(xlocations+ width/2, labels)
plt.xlim(0, xlocations[-1]+width*2)
plt.ylabel("Count per miss cleavage")
plt.xlabel("Miss cleavage")
for x,y in zip(xlocations,misscount):
    plt.text(x+0.4, y, '%.2d' % y, ha='center', va= 'bottom')
#change the directory according to your application path.
plt.savefig(r'D:/Dropbox/Dropbox/primdb/assets/img/statistics3.png', dpi=100, transparent=True)
