import numpy as np

a = np.array([[1, 2], [4, 3], [5, 6], [8, 7]], int)
print a
print a[0, 0]

b = np.eye(5,5)
print b

c = np.ones((5, 3))
c[1,1] = 0
print c

d = c.copy()
d[4,2] = 2
d = np.c_[d, [1,2,3,4,5]]
d = np.r_[d, np.array([[9,8,7,6]])]
print d

lignes = 10
colonnes = 5
mymap = []
for x in range(0, lignes):
	vecteur = []
	for y in range(0, colonnes):
		vecteur.append(1)
	mymap.append(vecteur)


print mymap

print len(mymap)
print len(mymap[0])

print mymap[0][1]