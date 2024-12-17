import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import webbrowser
import multiprocessing
import random
import time
from datetime import datetime, timedelta
import plotly.figure_factory as ff

# Initialize Dash app
app = dash.Dash(__name__)

# Default values for jobs and CPUs
DEFAULT_MAX_JOBS = 50
DEFAULT_NUM_CPUS = 3

# log messages
def log(message):
   timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
   print(f"{timestamp} {message}")

# generate random jobs dynamically
def generate_jobs(job_queue, stop_signal, max_jobs, num_cpus):
   job_id = 0
   while not stop_signal.is_set():
      if job_id >= max_jobs.value:  # Dynamically check max_jobs
         log(f"Reached MAX_JOBS limit: {max_jobs.value}. Stopping job generation.")
         break

      duration = random.randint(1, 8)
      affinity = random.sample(range(num_cpus.value), random.randint(1, num_cpus.value))
      arrival_time = datetime.now()
      job = {
         "Job ID": job_id, 
         "Duration": duration, 
         "Affinity": affinity,
         "Arrival": arrival_time
      }
      job_queue.put(job)
      log(f"Generated Job {job_id} with Duration {duration} and Affinity {affinity}")
      job_id += 1
      time.sleep(0.1)

# schedule jobs on available CPUs
def schedule_jobs(cpu_id, job_queue, completed_jobs, stop_signal, lock, num_cpus):
   retry_limit = 3
   job_retry_count = {} 

   while not stop_signal.is_set() or not job_queue.empty():
      try:
         job = job_queue.get(timeout=1)
         job_id = job["Job ID"]

         if job_id not in job_retry_count:
            job_retry_count[job_id] = 0

         # Check CPU affinity and CPU limit
         if cpu_id >= num_cpus.value or cpu_id not in job["Affinity"]:
            job_retry_count[job_id] += 1
            if job_retry_count[job_id] >= retry_limit:
               log(f"[CPU {cpu_id}] Job {job_id} could not be scheduled after {retry_limit} retries. Discarding.")
            else:
               log(f"[CPU {cpu_id}] Job {job_id} does not match affinity or exceeds CPU limit, returning to queue.")
               job_queue.put(job)
            continue

         log(f"[CPU {cpu_id}] Executing Job {job_id}")
         
         job["Start"] = datetime.now()
         
         # Simulate CPU-bound work
         start_comp = time.time()
         duration = job["Duration"]
         while time.time() - start_comp < duration:
            x = 0
            for i in range(1000000):
               x +=i
               
         job["End"] = datetime.now()
         job["CPU"] = cpu_id

         with lock: 
            completed_jobs.append(job)
         log(f"[CPU {cpu_id}] Completed Job {job_id}")
         
      except multiprocessing.queues.Empty:
         continue

   log(f"[CPU {cpu_id}] Exit signal received.")

# monitor jobs and log them
def monitor_jobs(completed_jobs, stop_signal, lock):
   while not stop_signal.is_set():
      with lock:
         log(f"Monitor: {len(completed_jobs)} jobs completed so far.")
      time.sleep(5)


# Add a callback for dynamic performance metrics
@app.callback(
    Output("performance-metrics", "children"),
    Input("interval-component", "n_intervals")
)
def update_performance_metrics(n):
   global system_start_time
   global num_cpus
   
   total_system_time = (datetime.now() - system_start_time).total_seconds()

   if total_system_time <= 0:
      return [
            html.H3("Performance Metrics", style={"color": "blue"}),
            html.P("No valid system runtime detected."),
        ]

    # Filter valid jobs
   valid_jobs = [
        job for job in completed_jobs
        if all(key in job for key in ["Arrival", "Start", "End"])
    ]

   total_jobs = len(valid_jobs)
   if total_jobs == 0:
      return [
            html.H3("Performance Metrics", style={"color": "blue"}),
            html.P("No jobs completed yet."),
        ]

    # Calculate metrics
   total_turnaround_time = sum(
        (job["End"] - job["Arrival"]).total_seconds()
        for job in valid_jobs
    )
   total_waiting_time = sum(
        max(0, ((job["End"] - job["Arrival"]).total_seconds() - job["Duration"]))
        for job in valid_jobs
    )
   total_response_time = sum(
        max(0, (job["Start"] - job["Arrival"]).total_seconds())
        for job in valid_jobs
    )

   total_execution_time = sum(
        (job["End"] - job["Start"]).total_seconds()
        for job in valid_jobs
    )


   # dynamically updated number of CPUs
   cpu_utilization = (total_execution_time / (num_cpus.value * total_system_time)) * 100
   throughput = total_jobs / total_system_time  # Jobs per second   

   # Performance Metrics UI
   return [
        html.H3("Performance Metrics", style={"color": "blue"}),
        html.P(f"CPU Utilization: {cpu_utilization:.2f}%"),
        html.P(f"Average Turnaround Time: {total_turnaround_time / total_jobs:.2f}s"),
        html.P(f"Average Waiting Time: {total_waiting_time / total_jobs:.2f}s"),
        html.P(f"Average Response Time: {total_response_time / total_jobs:.2f}s"),
        html.P(f"Throughput: {throughput:.2f} jobs/sec"),
    ]


# Dash layout
app.layout = html.Div([
    html.H1(
        "CIDS - 429 Operating Systems",
        style={
            "background-color": "maroon",
            "color": "white",
            "padding": "20px",
            "text-align": "center",
            "border-radius": "0px",
            "font-size": "24px",
            "font-weight": "bold",
            "margin-top": "0px",
            "margin-bottom": "0px"
        }
    ),
    html.Div([
        html.H2(
            "Interactive Real-Time CPU Scheduling Dashboard",
            style={
                "background-color": "yellow",
                "color": "red",
                "padding": "50px",
                "text-align": "center",
                "border-radius": "0px",
                "font-size": "20px",
                "margin-top": "0px",
                "margin-bottom": "20px",
                "position": "relative", 
            }
        ),
        html.Div(
            id="performance-metrics",
            style={
                "position": "absolute",
                "top": "0px",
                "left": "0px",
                "padding": "5px",
                "background-color": "yellow", 
                "width": "180px",
                "flex-shrink": "0",
                "font-size": "14px",
                "color": "blue",
                "z-index": "1", 
            },
        ),
    ], style={"position": "relative"}),
    html.Div([
        html.Label("Set Maximum Jobs:"),
        dcc.Input(
            id="max-jobs-input",
            type="number",
            value=DEFAULT_MAX_JOBS,
            style={
                "margin-right": "20px",
                "padding": "10px",
                "border-radius": "5px",
                "border": "1px solid #ccc",
                "font-size": "14px"
            }
        ),
        html.Label("Set Number of CPUs:"),
        dcc.Input(
            id="num-cpus-input",
            type="number",
            value=DEFAULT_NUM_CPUS,
            style={
                "margin-right": "20px",
                "padding": "10px",
                "border-radius": "5px",
                "border": "1px solid #ccc",
                "font-size": "14px"
            }
        ),
        html.Button(
            "Apply Settings",
            id="apply-settings-btn",
            style={
                "background-color": "maroon",
                "color": "white",
                "padding": "10px 20px",
                "border": "none",
                "border-radius": "5px",
                "cursor": "pointer",
                "font-size": "16px"
            }
        )
    ], style={
        "display": "flex",
        "align-items": "center",
        "margin-left": "120px",
        "justify-content": "center",
        "margin-bottom": "20px",
    }),
   
    dcc.Graph(
        id="gantt-chart",
        style={
            "box-shadow": "0px 4px 8px rgba(0, 0, 0, 0.1)",
            "border-radius": "10px",
            "background-color": "white"
        }
    ),
    dcc.Interval(
        id="interval-component",
        interval=2000, 
        n_intervals=0
    )
], style={
    "background-color": "#f4f4f4",
    "padding": "20px",
    "font-family": "Arial, sans-serif"
})

@app.callback(
   Output("gantt-chart", "figure"),
    Input("interval-component", "n_intervals")
)
def update_gantt_chart(n):
   chart_data = []
   with lock:
      for entry in completed_jobs:
         chart_data.append(dict(
               Task=f"Job {entry['Job ID']}",
                Start=entry["Start"].strftime("%Y-%m-%d %H:%M:%S"),
                Finish=entry["End"].strftime("%Y-%m-%d %H:%M:%S"),
                Resource=f"CPU {entry['CPU']}",
                Description=f"Affinity: {entry['Affinity']}, Retries: {entry.get('Retries', 0)}"
            ))
   if chart_data:
      fig = ff.create_gantt(chart_data, index_col="Resource", show_colorbar=True, group_tasks=True, title="Dynamic Gantt Chart")
      fig.update_layout(
         xaxis_title = "Time (seconds)",
         yaxis_title = "Jobs",
         title = "Dynamic Gantt Chart for CPU Scheduling",
         title_x = 0.5,
         yaxis = dict(
            automargin=True,
            tickfont=dict(size=10),
            dtick=1,
            showgrid=False,
            ),
      )
      return fig
   else:
      return {
           "data": [],
            "layout": {
               "title": "Dynamic Gantt Chart",
                "xaxis": {"title": "Time"},
                "yaxis": {"title": "Tasks"},
                "annotations": [
                   {
                       "text": "No jobs have been completed yet.",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {"size": 16}
                    }
                ]
            }
        }

@app.callback(
   Output("interval-component", "disabled"),
    [Input("apply-settings-btn", "n_clicks"),
     Input("max-jobs-input", "value"),
     Input("num-cpus-input", "value")]
)
def apply_settings(n_clicks, max_jobs_value, num_cpus_value):
   global generator_process, processes, monitor_process
   global MAX_JOBS, NUM_CPUS
   if n_clicks:
      max_jobs.value = max_jobs_value if max_jobs_value else max_jobs.value
      num_cpus.value = num_cpus_value if num_cpus_value else num_cpus.value

      log(f"Settings updated: MAX_JOBS={max_jobs.value}, NUM_CPUS={num_cpus.value}")

      # Restart scheduling processes with updated CPU count
      stop_signal.set()
      for process in processes:
         process.join()
      generator_process.join()
      monitor_process.join()

      # restart job generation and monitoring with new settings
      stop_signal.clear()
      generator_process = multiprocessing.Process(target=generate_jobs, args=(job_queue, stop_signal, max_jobs, num_cpus))
      generator_process.start()

      processes = []
      for cpu_id in range(num_cpus.value):
         process = multiprocessing.Process(target=schedule_jobs, args=(cpu_id, job_queue, completed_jobs, stop_signal, lock, num_cpus))
         processes.append(process)
         process.start()

      monitor_process = multiprocessing.Process(target=monitor_jobs, args=(completed_jobs, stop_signal, lock))
      monitor_process.start()

   return False

def main():
   global system_start_time
   system_start_time = datetime.now()
   
   global completed_jobs, lock, max_jobs, num_cpus, generator_process, processes, monitor_process, stop_signal, job_queue 
   job_queue = multiprocessing.Queue()
   manager = multiprocessing.Manager()
   completed_jobs = manager.list()
   lock = manager.Lock()  # create a lock
   stop_signal = multiprocessing.Event()

   # dynamic variables for settings
   max_jobs = manager.Value("i", DEFAULT_MAX_JOBS)
   num_cpus = manager.Value("i", DEFAULT_NUM_CPUS)

   # Start job generation process
   generator_process = multiprocessing.Process(target=generate_jobs, args=(job_queue, stop_signal, max_jobs, num_cpus))
   generator_process.start()

   # Start job scheduling processes
   processes = []
   for cpu_id in range(DEFAULT_NUM_CPUS):
      process = multiprocessing.Process(target=schedule_jobs, args=(cpu_id, job_queue, completed_jobs, stop_signal, lock, num_cpus))
      processes.append(process)
      process.start()

   # monitoring process
   monitor_process = multiprocessing.Process(target=monitor_jobs, args=(completed_jobs, stop_signal, lock))
   monitor_process.start()

   # automatically open browser to display the chart
   webbrowser.open_new("http://127.0.0.1:8050/")

   # run dash app
   try:
      log("Starting Dash app for real-time Gantt chart updates...")
      app.run_server(debug=False, use_reloader=False)
   except KeyboardInterrupt:
      log("Shutting down ...")
   finally:
      stop_signal.set()
      generator_process.join()
      for process in processes:
         process.join()
      monitor_process.join()
      log("All processes have completed.")

   # summary and Gantt chart generation
   log(f"Summary: {len(completed_jobs)} jobs were completed.")
   for job in completed_jobs:
      log(f"Job {job['Job ID']} completed on CPU {job['CPU']} with duration {job['Duration']} seconds.")

   chart_data = []
   for entry in completed_jobs:
      chart_data.append(dict(
           Task=f"Job {entry['Job ID']}",
            Start=entry["Start"].strftime("%Y-%m-%d %H:%M:%S"),
            Finish=entry["End"].strftime("%Y-%m-%d %H:%M:%S"),
            Resource=f"CPU {entry['CPU']}"
        ))
   fig = ff.create_gantt(chart_data, index_col="Resource", show_colorbar=True, group_tasks=True, title="Final Gantt Chart for CPU Scheduling")
   fig.show()

if __name__ == "__main__":
   main()