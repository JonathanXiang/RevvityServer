import requests
import subprocess
import os
import csv
import win32com.client

class RevvityLiquidHandler:
    def __init__(self, janus_exe_path: str = r"C:\Packard\Janus\bin\JANUS.exe", protocol_dir: str = r"C:\Packard\Janus\Protocols", parameter_file=r"C:\path\to\params.csv"):
        self.janus_exe_path = janus_exe_path
        self.protocol_dir = protocol_dir
        self.parameter_file = parameter_file
        self.parameters = {}
        try:
            self.winp = win32com.client.Dispatch("WinPREP.Auto")
        except Exception as e:
            self.winp = None
            self._status = f"Error: {e}"

    def get_protocols(self):
        protocols = []
        for root, _, files in os.walk(self.protocol_dir):
            for fname in files:
                if fname.lower().endswith('.mpt'):
                    protocols.append(os.path.join(root, fname))
        return protocols

    def run_protocol(self, protocol_path: str):
        cmd = f'"{self.janus_exe_path}" /r "{protocol_path}"'
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return {
            "command": cmd,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    def get_parameters(self):
        parameters = {}
        try:
            with open(self.parameter_file, newline='') as csvfile:
                dialect = csv.Sniffer().sniff(csvfile.read(1024))
                csvfile.seek(0)
                reader = csv.DictReader(csvfile, dialect=dialect)
                for row in reader:
                    parameters.update(row)
                    break
        except Exception as e:
            parameters = {"error": str(e)}
        return parameters

    def set_parameters(self, new_params: dict):
        try:
            with open(self.parameter_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=new_params.keys())
                writer.writeheader()
                writer.writerow(new_params)
            return True
        except Exception as e:
            return {"error": str(e)}

    def get_status(self):
        if self.winp is None:
            return self._status
        try:
            is_running = self.winp.IsRunning
            status_code = self.winp.StatusCode
            error_code = self.winp.ErrorCode
            error_msg = self.winp.ErrorMessage

            status_summary = {
                "IsRunning": is_running,
                "StatusCode": status_code,
                "ErrorCode": error_code,
                "ErrorMessage": error_msg,
            }
            return status_summary
        except Exception as e:
            return {"Error": str(e)}

    def count_tips_used(self):
        try:
            log_file = r"C:\Packard\Janus\Bin\dt_temp"
            tips_used = 0
            with open(log_file, "r") as f:
                for line in f:
                    if line.strip().upper() == "X":
                        tips_used += 1
            return tips_used
        except Exception as e:
            return {"error": str(e)}
        
    def count_tips_available(self):
        try:
            log_file = r"C:\Packard\Janus\Bin\dt_temp"
            tips_avail = 0
            with open(log_file, "r") as f:
                for line in f:
                    if line.strip().upper() == "Y":
                        tips_avail += 1
            return tips_avail
        except Exception as e:
            return {"error": str(e)}