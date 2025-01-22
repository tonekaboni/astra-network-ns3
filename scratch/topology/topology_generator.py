

n_npu = int(input("Enter total number of NPUs: "))
n_layers = int(input("Enter number of layers of switches(npus notincl): "))
print("now enter the number of switches in each layer")
print("start from top down (ex: 1-2-4)")
l_sizes = []
n_switch = 0
for i in range(n_layers):
    inpt = int(input("number of switches in layer "+str(i)+": "))
    l_sizes.append(inpt)
    n_switch += inpt

filename = str(n_npu)+"_nodes_"+str(n_switch)+"_switch_"+str(n_layers)+"_layers_topology.txt"

f = open(filename, "w")

##lets find total number of connectiones
#lets start with every npu
n_connections = n_npu

#lets go up the layers
for i in range(n_layers-1,0,-1):
    n_connections += l_sizes[i]

#top layer is interconnected:
n_connections += (l_sizes[0] * (l_sizes[0]-1)) / 2

f.write(str(n_npu+n_switch)+" "+str(n_switch)+" "+str(int(n_connections))+"\n")

line = ""
for i in range(n_switch):
    line = line + str(n_npu+i) + " "

f.write(line+"\n")

n_parent = l_sizes[len(l_sizes)-1]
body = ""
for i in range (n_npu):
    parent = int((i / (n_npu/n_parent))+ n_npu)
    body = body + (str(i)+" "+str(parent)+" 200Gbps 0.005ms 0\n")
iter = n_npu
if (n_layers>1):
    
    for j in range(n_layers-1,0,-1):
        iter += l_sizes[j]
        n_parent = l_sizes[j-1]
        
        for i in range (l_sizes[j]):
            
            parent = int((i / (l_sizes[j]/n_parent))+ iter)
            body = body + (str(i+iter-l_sizes[j])+" "+str(parent)+" 200Gbps 0.005ms 0\n")

if (l_sizes[0]>1):
    for i in range (l_sizes[0]):
        for j in range(i,l_sizes[0]):
            if (i!=j):
                body = body + (str(i+iter)+" "+str(j+ iter)+" 200Gbps 0.005ms 0\n")


f.write(body)

