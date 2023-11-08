
doc : dict = {"_id" : "hi" , "key" : "1"}

dic : dict = {"_id" : "hola" , "key" : "2"}

lista = [dic , doc]

lis = []

doc = {**doc , **dic}

for i in lista:
    i.pop("_id")
    lis.append(tuple(i)+tuple(i.values()))
    
    print(lis)