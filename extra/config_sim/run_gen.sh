#!/bin/bash

#for (( j=0; j <= 1000; j++ ))
#do
#python3 scenario_gen.py -gen $j 10
#done

#for (( j=0; j <= 100; j++ ))
#do
#python3 scenario_gen.py -gen $j 50
#done

for (( i=10; i <= 300; i++))
do
let a=$i*100-900
for (( j=0; j <= 9; j++ ))
do
python3 scenario_gen.py -gen $j $a
done
done
