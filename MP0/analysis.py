time_A = []
time_B = []
time_C = []
size_A = []
size_B = []
size_C = []


with open("A.txt", 'r') as f:
    content = f.readlines()
    for line in content:
        if "GN" in line:
            begin_time = float(line.split(' ')[1])
        if "[RECV TIME]" in line:
            end_time = float(line.split(' ')[2].strip('\n'))
            time_A.append(end_time-begin_time)
        if "[SIZE]" in line:
            size_A.append(int(line.split(' ')[1].strip('\n')))

with open("B.txt", 'r') as f:
    content = f.readlines()
    for line in content:
        if "GN" in line:
            begin_time = float(line.split(' ')[1])
        if "[RECV TIME]" in line:
            end_time = float(line.split(' ')[2].strip('\n'))
            time_B.append(end_time-begin_time)
        if "[SIZE]" in line:
            size_B.append(int(line.split(' ')[1].strip('\n')))

with open("C.txt", 'r') as f:
    content = f.readlines()
    for line in content:
        if "GN" in line:
            begin_time = float(line.split(' ')[1])
        if "[RECV TIME]" in line:
            end_time = float(line.split(' ')[2].strip('\n'))
            time_C.append(end_time-begin_time)
        if "[SIZE]" in line:
            size_C.append(int(line.split(' ')[1].strip('\n')))

print("A")
print(sum(time_A)/len(time_A))
print(max(time_A))
print(min(time_A))
print(sum(size_A)/sum(time_A))
print("B")
print(sum(time_B)/len(time_B))
print(max(time_B))
print(min(time_B))
print(sum(size_B)/sum(time_B))
print("C")
print(sum(time_C)/len(time_C))
print(max(time_C))
print(min(time_C))
print(sum(size_C)/sum(time_C))






