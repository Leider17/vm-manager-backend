import csv
import os
import time

# path = '/var/log/vm-manager/'
file_path = 'performance_log.csv'
csv_header = ['timestamp','operation','vm_name','duration_seconds','status', 'host_memory','used_disk',"cpu_cores"]

def log_performance(operation: str, vm_name: str, duration: float, status: str, host_memory, used_disk, cpu_cores):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    data = [timestamp, operation, vm_name, round(duration, 4), status, host_memory, used_disk, cpu_cores]
    
    file_exists = os.path.exists(file_path)
    
    try:
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            
            if not file_exists:
                writer.writerow(csv_header)
                
            
            writer.writerow(data)
    except Exception as e:
        print("no se pudo escribir en el archivo de rendimiento")