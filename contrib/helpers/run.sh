#!/usr/bin/env bash

# Create some dummy data
python dummy_writer.py
sleep 5

# Run some queries
python benchmark.py
