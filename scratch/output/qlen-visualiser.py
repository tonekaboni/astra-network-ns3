import matplotlib
#import scipy.io
import struct
import pandas as pd
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

# code is hard coded for 8 node, 4 switch fat tree topology with 2 cores and 2 edges
num_cores = 2
num_edges = 2
num_nodes_per_edge = 4
min_id_of_core = 10
num_npus = 8
num_switch_ports = 2


f = open("qlen.txt", "r")

swich_id = {}
rev_swich_id = {}
times = []
lengths = []


def get_q_lengths(col):
    if int(col[2]) >= min_id_of_core:
        num_qs = int((len(col) - 3) / 3)
        total = [0] * num_edges 
        
        for i in range (num_qs):
            ind = int(col[4+(3*i)])-1
            total[ind] = int(col[5+(3*i)])
        return total
    else: 
        num_qs = int((len(col) - 3) / 3)
        total = [0] * num_cores 
        
        for i in range (num_qs):
            
            ind = int(col[4+(3*i)])-1
            if (ind>= num_nodes_per_edge):
                total[ind-num_nodes_per_edge] = int(col[5+(3*i)])
        return total


u = open("linkUtil.txt", "r")

util_times = [[[0 for _ in range(0)] for _ in range(num_switch_ports)] for _ in range(num_npus)]
util = [[[0 for _ in range(0)] for _ in range(num_switch_ports)] for _ in range(num_npus)]

for line in u:
    col = line.split(' ')
    sw_id = int (col[3]) - num_npus 
    port_id = int (col[5]) - 1
    is_core = False
    #print (str(sw_id) + "  ")
    if int (col[3]) >= min_id_of_core:
        is_core = True

    if not is_core and port_id < num_nodes_per_edge:
        continue    
    if not is_core:
        port_id = port_id - num_nodes_per_edge
    #print("port id: " +str(port_id) + " switch id :" + str(sw_id))
    util_times[sw_id][port_id].append(int(col[1]))
    util[sw_id][port_id].append(int(col[7]))
    #np.append (util_times[sw_id][port_id], col[1])
    #np.append (util[sw_id][port_id], col[7])

    


for line in f:
    col = line.split(' ')
    id = int (col[2])
    if (swich_id.get(id)==None):
        index = len(swich_id)
        swich_id.update({id:index})
        rev_swich_id.update({index:id})
        new_time_list = [int(col[1])]
        length_list = get_q_lengths(col)
        
        new_length_list =[[0 for _ in range(1)] for _ in range(num_cores)]
        times.append(new_time_list)
        for i in range (num_cores):
            
            new_length_list[i][0]= length_list[i]
        lengths.append(new_length_list)
        #print(str(lengths) + " lengths\n")
    else:
        index = swich_id.get(id)
        times[index].append(int(col[1]))
        #print("times\n")
        new_length_list = get_q_lengths(col)
        for i in range (num_cores):
            (lengths[index][i]).append(new_length_list[i])
            #print(str(new_length_list[i]) + " lengths\n")
            #if (count<20):
            #    print(str(lengths) + " lengths\n")
            #    count = count+1
    

figure, axis = plt.subplots(num_cores+ num_edges, num_cores * 2, figsize=(8*num_cores, 4*num_edges))

#print (util[3][0]) 


for i in range (num_cores+ num_edges):
    if (i<len(swich_id)):
        for j in range (num_cores):
            axis[i, j].set_title(str(num_npus+i)+ "_th_node" + str(j+1) + "'th port Q length")
            #print(str(len(times[i]))+ " " + str(len(lengths[i][j])) + "\n")
            axis[i, j].scatter(times[i], lengths[i][j], s=1)
            axis[i, j].set_xlabel('time (Nano Seconds)')
            axis[i, j].set_ylabel('Queue size (bytes)')
            #axis[i, j].xaxis.set_major_locator(MaxNLocator(nbins=5))
    for j in range (num_cores):
        axis[i, j+num_cores].set_title(str(num_npus+i)+ "_th_node" + str(j+1) + "'th link util")
        axis[i, j+num_cores].plot(util_times[i][j], util[i][j])
        axis[i, j+num_cores].set_xlabel('time (Nano Seconds)')
        axis[i, j+num_cores].set_ylabel('util size (bytes)')
        
plt.tight_layout()
filename = "sw_Q_size_graph.png"
plt.savefig(filename)    
    #plt.xlabel('time (Nano Seconds)')
    #plt.ylabel('Queue size (bytes)')
    #plt.scatter(times[i],lengths[i])
    
    #print(lengths[i])
    
plt.clf()






"""

def get_total_q(col):
    num_qs = int((len(col) - 3) / 3)
    total = 0
    for i in range (num_qs):
        total = total + int(col[5+(3*i)])
    return total

swich_id = {}
rev_swich_id = {}
times = []
lengths = []

## parsing and making lists
print("im runnin\n")
for line in f:
    col = line.split(' ')
    id = int (col[2])
    if (swich_id.get(id)==None):
        index = len(swich_id)
        swich_id.update({id:index})
        rev_swich_id.update({index:id})
        new_time_list = [int(col[1])]
        new_length_list = [get_total_q(col)]
        times.append(new_time_list)
        lengths.append(new_length_list)
    else:
        index = swich_id.get(id)
        times[index].append(int(col[1]))
        lengths[index].append(get_total_q(col))

##plotting:

for i in range (len(swich_id)):
    plt.title(str(rev_swich_id.get(i))+ "_th_node")
    plt.xlabel('time (Nano Seconds)')
    plt.ylabel('Queue size (bytes)')
    plt.scatter(times[i],lengths[i])
    filename = str(rev_swich_id.get(i))+ "_th_switch.png"
    
    plt.savefig(filename)
    plt.clf()
    #plt.show()

# Load the .mat file
#mat_data = scipy.io.loadmat('mix.tr')
#print(mat_data.keys())
# Assuming the variable you want to export is a matrix
#matrix_data = mat_data['your_matrix_variable']  # Replace with the variable name

# Save to CSV
#with open('output_file.csv', 'w', newline='') as csvfile:
 ##   csvwriter = csv.writer(csvfile)
 #   csvwriter.writerows(matrix_data)



# Define the TraceFormat structure
# '<' indicates little-endian
# Q: uint64_t, H: uint16_t, B: uint8_t, I: uint32_t
# The main structure has fixed-size fields followed by a union




TRACE_FORMAT_STRUCT = '<Q H B B I I I H B B B B'

# Define the sizes of the union members
DATA_STRUCT = '<H H I Q H H'
CNP_STRUCT = '<H B B H H'
ACK_STRUCT = '<H H H H I Q'
PFC_STRUCT = '<I I B'
QP_STRUCT = '<H H'

# Define event types for mapping
EVENT_TYPES = {
    0: 'Recv',
    1: 'Enqu',
    2: 'Dequ',
    3: 'Drop'
}

def parse_trace_file(file_path):
    records = []
    with open(file_path, 'rb') as f:
        while True:
            # Read the fixed part of TraceFormat
            fixed_size = struct.calcsize(TRACE_FORMAT_STRUCT)
            fixed_data = f.read(fixed_size)
            if not fixed_data or len(fixed_data) < fixed_size:
                break  # End of file

            fixed_fields = struct.unpack(TRACE_FORMAT_STRUCT, fixed_data)
            trace_record = {
                'time': fixed_fields[0],
                'node': fixed_fields[1],
                'intf': fixed_fields[2],
                'qidx': fixed_fields[3],
                'qlen': fixed_fields[4],
                'sip': fixed_fields[5],
                'dip': fixed_fields[6],
                'size': fixed_fields[7],
                'l3Prot': fixed_fields[8],
                'event': EVENT_TYPES.get(fixed_fields[9], 'Unknown'),
                'ecn': fixed_fields[10],
                'nodeType': fixed_fields[11]
            }

            # Depending on the event, read the appropriate union member
            event = fixed_fields[9]
            if event == 0:  # Recv
                union_size = struct.calcsize(DATA_STRUCT)
                union_data = f.read(union_size)
                if len(union_data) < union_size:
                    break  # Unexpected EOF
                data_fields = struct.unpack(DATA_STRUCT, union_data)
                trace_record.update({
                    'sport': data_fields[0],
                    'dport': data_fields[1],
                    'seq': data_fields[2],
                    'ts': data_fields[3],
                    'pg': data_fields[4],
                    'payload': data_fields[5]
                })
            elif event == 1:  # Enqu
                union_size = struct.calcsize(CNP_STRUCT)
                union_data = f.read(union_size)
                if len(union_data) < union_size:
                    break
                cnp_fields = struct.unpack(CNP_STRUCT, union_data)
                trace_record.update({
                    'fid': cnp_fields[0],
                    'qIndex': cnp_fields[1],
                    'ecnBits': cnp_fields[2],
                    'qfb': cnp_fields[3],
                    'total': cnp_fields[4]
                })
            elif event == 2:  # Dequ
                union_size = struct.calcsize(ACK_STRUCT)
                union_data = f.read(union_size)
                if len(union_data) < union_size:
                    break
                ack_fields = struct.unpack(ACK_STRUCT, union_data)
                trace_record.update({
                    'sport': ack_fields[0],
                    'dport': ack_fields[1],
                    'flags': ack_fields[2],
                    'pg': ack_fields[3],
                    'seq': ack_fields[4],
                    'ts': ack_fields[5]
                })
            elif event == 3:  # Drop
                union_size = struct.calcsize(PFC_STRUCT)
                union_data = f.read(union_size)
                if len(union_data) < union_size:
                    break
                pfc_fields = struct.unpack(PFC_STRUCT, union_data)
                trace_record.update({
                    'drop_time': pfc_fields[0],
                    'drop_qlen': pfc_fields[1],
                    'drop_qIndex': pfc_fields[2]
                })
            #else:
                # Unknown event, handle accordingly or skip
                #union_size = struct.calcsize(QP_STRUCT)
                #union_data = f.read(union_size)
                #if len(union_data) < union_size:
               #     break
               # pfc_fields = struct.unpack(QP_STRUCT, union_data)
               # trace_record.update({
               #     'sport': pfc_fields[0],
               #     'dport': pfc_fields[1]
               # })

            records.append(trace_record)

    # Convert records to DataFrame and save as CSV
    df = pd.DataFrame(records)
    df.to_csv('trace_output.csv', index=False)
    print("Trace data has been written to trace_output.csv")


trace_file_path = 'mix.tr'  # Replace with your .tr file path
parse_trace_file(trace_file_path)



###############################
"""