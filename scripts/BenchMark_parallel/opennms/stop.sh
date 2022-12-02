#!/bin/bash
export docker_opennms_maxCpu=2
export docker_opennms_maxMemory="1G"
export docker_postgress_maxCpu=2
export docker_postgress_maxMemory="1G"
docker compose down -v
