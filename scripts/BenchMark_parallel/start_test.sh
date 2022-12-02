#!/bin/bash

export curr=$(pwd)
export dfolder=$(pwd)/opennms

monitorDocker () {
    export DOCKERSTATOUTPUTFILE="logs/docker_stat_$1.txt"
    echo "DATETIME Name CPUPerc MemUsage MemPerc NetIO BlockIO" >> "$DOCKERSTATOUTPUTFILE"
    echo " " >>  "$DOCKERSTATOUTPUTFILE"
    while [ ! -f logs/stopLogging.txt ];
    do 
      date | tee -a  "$DOCKERSTATOUTPUTFILE";
      docker stats --no-stream --format "{{.Name}}: {{.CPUPerc}} {{.MemUsage}} {{.MemPerc}} {{.NetIO}} {{.BlockIO}}" database horizon | tee -a "$DOCKERSTATOUTPUTFILE";
      
    done
    touch logs/stopLogging.txt
}

test () {
    export docker_opennms_maxCpu=$2
    export docker_opennms_maxMemory=$4
    export docker_postgress_maxCpu=$3
    export docker_postgress_maxMemory=$5

    export OUTPUTFILE="logs/output_$1.txt"
    export DOCKERSTATOUTPUTFILE="logs/docker_stat_$1.txt"

    echo "Container Resource INFO:" >> "$DOCKERSTATOUTPUTFILE" 2>&1
    echo "OpenNMS CPU: $docker_opennms_maxCpu " >> "$DOCKERSTATOUTPUTFILE" 2>&1
    echo "OpenNMS Memory: $docker_opennms_maxMemory " >> "$DOCKERSTATOUTPUTFILE" 2>&1
    echo "Postgress CPU: $docker_postgress_maxCpu " >> "$DOCKERSTATOUTPUTFILE" 2>&1
    echo "Postgress Memory: $docker_postgress_maxMemory " >> "$DOCKERSTATOUTPUTFILE" 2>&1
    if [ -f logs/stopLogging.txt ]; then
     rm logs/stopLogging.txt
    fi
    echo "Running tests with $1 nodes at $(date)" >> "$OUTPUTFILE" 2>&1
    echo "Running tests with $1 nodes at $(date)" >> "$DOCKERSTATOUTPUTFILE" 2>&1
    monitorDocker $1 &
    cd $dfolder
    docker compose up -d
    cd $curr
    echo "Waiting for OpenNMS to come up $(date)" >> "$OUTPUTFILE" 2>&1
    curl -s --retry 50 -f --retry-all-errors --retry-delay 5 -o /dev/null "http://localhost:8980/opennms/login.jsp"
    echo "OpenNMS is up and ready $(date)" >> "$OUTPUTFILE" 2>&1
    echo "Executing test $(date)" >> "$OUTPUTFILE" 2>&1
    python3 main.py $1 >> "$OUTPUTFILE" 2>&1
    echo "Done executing test $(date)" >> "$OUTPUTFILE" 2>&1
    echo "Sleeping for 15 minutes to observe the behaviour of system usage $(date)" >> "$OUTPUTFILE" 2>&1
    echo "Monitoring Behaviour for 15 minutes " >> "$DOCKERSTATOUTPUTFILE" 2>&1
    sleep 900
    echo "Sleept for 15 minutes in order to observe the behaviour of system usage $(date)" >> "$OUTPUTFILE" 2>&1
    echo "DONE" >> logs/stopLogging.txt 2>&1
    cd $dfolder
    docker compose down -v
    cd $curr
    echo "---" >> "$OUTPUTFILE" 2>&1
    echo "---" >> "$DOCKERSTATOUTPUTFILE" 2>&1
    echo "DONE" >> logs/stopLogging.txt 2>&1
    sleep 10
}

export OpenNMS_MaxCPU=2
export Postgress_MaxCPU=2
export OpenNMS_MaxMemory="8G"
export Postgress_MaxMemory="2G"

START=1
INCREMENT=10
END=500
## save $START, just in case if we need it later ##
i=$START
while [[ $i -le $END ]]
do
    ((n = (i - 1) + INCREMENT))
    echo "$n/$END"
    test $n $OpenNMS_MaxCPU $Postgress_MaxCPU $OpenNMS_MaxMemory $Postgress_MaxMemory
    ((i = i +INCREMENT))
done

python3 graphit.py