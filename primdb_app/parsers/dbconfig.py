import psycopg2
conn = psycopg2.connect(host="localhost",user="primuser",password="web",database="primdb")
#conn = psycopg2.connect(host="ec2-107-21-106-181.compute-1.amazonaws.com",
#						user="lmvpqjgbjuzgpy",password="xwIwc5j8kHEAKWVJJmgi5MAcGM",
#						port="5432", database="d1kf7ea8upulok")
cursor = conn.cursor()
