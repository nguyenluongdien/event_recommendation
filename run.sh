#!/bin/bash
    for i in `seq 1 10`;
    do
        python split_data.py
        python main.py
    done    
