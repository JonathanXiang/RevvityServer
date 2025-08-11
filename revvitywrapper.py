import requests
import subprocess
import os
import csv
import win32com.client
import os, re, json, csv

class RevvityLiquidHandler:

    COORD_RE = re.compile(r'([A-G])\s*([1-9])', re.IGNORECASE)

    def __init__(self, janus_exe_path: str = r"C:\Packard\Janus\Bin\JANUS.exe", protocol_dir: str = r"C:\Packard\Janus\Protocols", parameter_file=r"C:\path\to\params.csv", dt_folder=r"C:\Packard\Janus\Bin\dt_temp"):
        self.janus_exe_path = janus_exe_path
        self.protocol_dir = protocol_dir
        self.parameter_file = parameter_file
        self.parameters = {}
        self.dt_folder = dt_folder
        self._tip_availability = {}
        
        try:
            self.winp = win32com.client.Dispatch("WinPREP.Auto")
        except Exception as e:
            self.winp = None
            self._status = f"Error: {e}"

    def _extract_coord_from_filename(self, filename: str) -> str | None:
        m = self.COORD_RE.search(os.path.basename(filename))
        return f"{m.group(1).upper()}{m.group(2)}" if m else None

    def _count_available_in_dt(self, dt_path: str) -> int:
        count = 0
        with open(dt_path, "r") as f:
            for line in f:
                if line.strip().upper() == "Y":
                    count += 1
        return count

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
        
    def _find_dt_for_coord(self, folder: str, coord: str) -> str | None:
        token = coord.upper()
        for fn in os.listdir(folder):
            if not fn.lower().endswith(".dt"):
                continue
            name = os.path.splitext(fn)[0].upper()
            if token in re.findall(r'[A-G][1-9]', name):
                return os.path.join(folder, fn)
        return None

    def refresh_tip_availability(self) -> dict:
        if not os.path.isdir(self.dt_folder):
            raise FileNotFoundError(f"Folder not found: {self.dt_folder}")

        new_state = {}
        for fn in os.listdir(self.dt_folder):
            if not fn.lower().endswith(".dt"):
                continue

            coord = self._extract_coord_from_filename(fn)
            if not coord:
                continue

            tray_number = len(new_state) + 1
            dt_path = os.path.join(self.dt_folder, fn)
            available = self._count_available_in_dt(dt_path)

            new_state[str(tray_number)] = {coord: available}

        self._tip_availability = new_state
        return self._tip_availability