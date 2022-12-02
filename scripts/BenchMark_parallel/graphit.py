import os
import re
import datetime
import pandas as pd 
import matplotlib.pyplot as plt


def graphit(TMP_FILE):
    tmp_content=""
    numNodes=TMP_FILE.split("_")[-1].replace(".txt","")
    with open(TMP_FILE,"r") as f:
        tmp_content=f.readlines()

    data_table={}
    data_table["database"]={}
    data_table["horizon"]={}

    data_table_cpumemUsage=[]
    database_table_cpumemUsage=[]

    datePattern=re.compile("(\w)+ (\w)+ (\d)+ (\d)+:(\d)+:(\d)+ (\w)+ (\d)+")
    tmp_datetime=""
    for l in tmp_content:
        if re.match(datePattern,l.strip()):
            tmp_datetime=l.strip()

        if "database:" in l.strip() or "horizon" in l.strip():
            tmp=l.strip().split(":")[1]
            tmp_cpuPercentage=(tmp.split(" ")[1])
            tmp_memUsage=(tmp.split(" ")[2])
            tmp_memMax=(tmp.split(" ")[4])
            tmp_memPercentage=(tmp.split(" ")[5])
            tmp_networkInput=(tmp.split(" ")[6])
            tmp_networkOutput=(tmp.split(" ")[8])
            tmp_blockInput=(tmp.split(" ")[9])
            tmp_blockOutput=(tmp.split(" ")[11])


            if "database:" in l.strip():
                database_table_cpumemUsage.append([datetime.datetime.strptime(tmp_datetime.split(" ")[3],"%H:%M:%S"),float(tmp_cpuPercentage.split("%")[0]),float(tmp_memPercentage.split("%")[0])])
            elif "horizon" in l.strip():
                data_table_cpumemUsage.append([datetime.datetime.strptime(tmp_datetime.split(" ")[3],"%H:%M:%S"),float(tmp_cpuPercentage.split("%")[0]),float(tmp_memPercentage.split("%")[0])])


    df=pd.DataFrame(data_table_cpumemUsage,columns=['datetime', 'cpuusage', 'memusage'])
    df.to_csv(TMP_FILE.replace(".txt","_horizon.csv"))
    df2=pd.DataFrame(database_table_cpumemUsage,columns=['datetime', 'cpuusage', 'memusage'])
    df2.to_csv(TMP_FILE.replace(".txt","_database.csv"))

    x=df['datetime'].to_list()
    y=df['cpuusage'].to_list()
    z=df['memusage'].to_list()
    x1=df2['datetime'].to_list()
    y1=df2['cpuusage'].to_list()
    z1=df2['memusage'].to_list()

    plt.subplot(1,2,1)
    plt.suptitle("OpenNMS Running with "+numNodes+" Nodes")
    plt.plot(x,y,'b',label="Cpu")
    plt.plot(x,z,'r',label="Mem")
    plt.title('Cpu/Mem Usage (Horizon)')
    plt.legend()
    plt.tick_params(labelrotation = 90)
    plt.xlabel('Time')
    plt.ylabel('%')

    plt.subplot(1,2,2)
    plt.plot(x1,y1,'b',label="Cpu",)
    plt.plot(x1,z1,'r',label="Mem")
    plt.title('Cpu/Mem Usage (Database)')
    plt.legend()
    plt.tick_params(labelrotation = 90)
    plt.xlabel('Time')
    plt.ylabel('%')


    plt.tight_layout()
    plt.savefig(TMP_FILE.replace(".txt",".png"))
    plt.close()



LOG_DIRECTORY="logs"
for f in os.listdir(LOG_DIRECTORY):
    if "stopLogging.txt" in f:
        continue
    if "docker_stat_" in f and ".png" not in f and ".csv" not in f:
        print(f)
        graphit(LOG_DIRECTORY+"/"+f)
