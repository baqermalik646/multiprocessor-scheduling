

# Interactive Real-Time CPU Scheduling Dashboard

### Project Overview

This project implements an Interactive Real-Time CPU Scheduling Dashboard using Python and Dash. It provides a dynamic simulation and visualization of CPU scheduling, displaying performance metrics and a Gantt chart for job execution.

The dashboard allows users to:

    Dynamically configure the number of CPUs and the maximum jobs.
    Monitor performance metrics, including CPU utilization, average turnaround time, waiting time, response time, and throughput.
    Visualize job execution using a real-time Gantt Chart.

### Features

   1. Dynamic Job Generation:
        Jobs are generated with random durations and CPU affinity constraints.
        Maximum jobs and CPU count are user-configurable.

   2. Job Scheduling:
        Jobs are scheduled to available CPUs based on their affinity.
        Retries are handled with a configurable retry limit.

   3. Performance Metrics:
        CPU Utilization,
        Average Turnaround Time,
        Average Waiting Time,
        Average Response Time,
        Throughput (jobs/second)

   4. Real-Time Gantt Chart:
        Displays job execution timeline per CPU.
        Updates dynamically as jobs are completed.

   5. Monitoring and Logging:
        Real-time logs are printed to the terminal.
        Job completion status and scheduling issues are monitored.


### Tech Stack

    Programming Language: Python 3
    Frameworks & Libraries:
        Dash: For building the interactive web application.
        Plotly: For generating the dynamic Gantt chart.
        Multiprocessing: For simulating parallel job execution.


### Installation

   1. Prerequisites:

            Python 3.x installed.

        Required Python libraries:

            pip install dash plotly

   2. Clone the Repository:

            git clone https://github.com/baqermalik646/multiprocessor-scheduling.git

            cd multiprocessor-scheduling

   3. Run the Program:

            python3 multi.py

   4. Access the Dashboard:

            Open your browser and go to http://127.0.0.1:8050/


### Usage
#### Dashboard Overview:

    1. Set Configurations:
        Use the Set Maximum Jobs and Set Number of CPUs inputs to configure the system.
        Click Apply Settings to update.

    2. Performance Metrics:
        Displays real-time statistics such as:
            CPU Utilization
            Average Turnaround, Waiting, and Response Times
            Throughput

    3. Dynamic Gantt Chart:
            Visualizes job execution over time across multiple CPUs.

    4. Real-Time Logs:
            Monitor job scheduling events in the terminal.

        
#### Dashboard Preview - Screenshots are available in screenshots folder.

### How It Works

    1. Job Generation:
            Jobs are dynamically created with random durations (1-8 seconds) and CPU affinity constraints.

    2. Job Scheduling:
            Jobs are scheduled to CPUs that match their affinity.
            Jobs exceeding the retry limit are discarded.

    3. Performance Monitoring:
            Metrics are dynamically calculated and displayed in real-time.

    4. Visualization:
            A Gantt Chart dynamically visualizes completed jobs across CPUs.

