import requests
import subprocess
import os
import csv
import win32com.client

class RevvityLiquidHandler:
    def __init__(self, janus_exe_path: str = r"C:\Packard\Janus\Bin\JANUS.exe", protocol_dir: str = r"C:\Packard\Janus\Protocols", parameter_file=r"C:\path\to\params.csv"):
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

    def get_parameters(self, param_file, column_index: int = 0):
        values = []
        try:
            with open(param_file, newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if column_index < len(row):
                        values.append(row[column_index])
                    else:
                        values.append(None)
        except Exception as e:
            parameters = {"error": str(e)}
        return values

    def set_parameters(self, new_params: dict, param_file):
        try:
            with open(param_file, 'w', newline='') as csvfile:
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