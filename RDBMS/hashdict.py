letters=list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
totallist=[]
for i in letters:
	totallist.append(i)

no=[0,1,2,3,4,5,6,7,8,9]
nos=[]
for i in no:
	nos.append(str(i))
for i in nos:
	totallist.append(i)
punctuation=list('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')
for i in punctuation:
	totallist.append(i)
spaces=list(' \t\n\r\x0b\x0c')
for i in spaces:
	totallist.append(i)
print(totallist)
hashdict={}
c=0
for i in totallist:
	c+=1
	kie=i
	value=c
	hashdict[kie]=value

def hash(string):
	hashed=''
	for i in string:
		hashkey=hashdict[i]
		hashkey=str(hashkey)
		hashed+=hashkey
		hashed+='#'
		print(i,hashkey)
	return str(hashed)

def unhash(hashno):
	hashlst=list(hashno.split('#'))
	print(hashlst)

	unhash=''
	for i in hashlst:
		try:
			i=int(i)
			unhash+=((list(hashdict.keys())[list(hashdict.values()).index(i)]))
		except:
			continue
	return str(unhash)