import time
import os

class SystemMonitorEngine:
    def __init__(self):
        self.prev_cpu_total = 0
        self.prev_cpu_idle = 0
        self.last_cpu_percent = 0.0

        self.last_ram_used_mb = 0
        self.last_ram_total_mb = 0
        self.last_ram_percent = 0.0

        self.prev_net_rx = 0
        self.prev_net_tx = 0
        self.prev_net_time = 0.0
        self.last_download_kbps = 0.0
        self.last_upload_kbps = 0.0

        self.last_cpu_temp = 0.0

    def update_cpu(self):
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline()
                if line.startswith('cpu '):
                    parts = [float(x) for x in line.split()[1:]]
                    idle = parts[3] + parts[4]  # idle + iowait
                    total = sum(parts)
                    if self.prev_cpu_total > 0:
                        delta_total = total - self.prev_cpu_total
                        delta_idle = idle - self.prev_cpu_idle
                        if delta_total > 0:
                            self.last_cpu_percent = max(0.0, min(100.0, (1.0 - (delta_idle / delta_total)) * 100.0))
                    self.prev_cpu_total = total
                    self.prev_cpu_idle = idle
        except Exception:
            pass

    def update_ram(self):
        try:
            total_kb = 0
            avail_kb = 0
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        total_kb = int(line.split()[1])
                    elif line.startswith('MemAvailable:'):
                        avail_kb = int(line.split()[1])
            if total_kb > 0:
                used_kb = total_kb - avail_kb
                self.last_ram_total_mb = total_kb // 1024
                self.last_ram_used_mb = used_kb // 1024
                self.last_ram_percent = max(0.0, min(100.0, (used_kb / total_kb) * 100.0))
        except Exception:
            pass

    def update_net(self):
        try:
            total_rx = 0
            total_tx = 0
            with open('/proc/net/dev', 'r') as f:
                lines = f.readlines()[2:]
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('lo:'):
                        continue
                    if ':' in line:
                        _, data = line.split(':', 1)
                        parts = data.split()
                        if len(parts) >= 9:
                            total_rx += int(parts[0])
                            total_tx += int(parts[8])

            now = time.monotonic()
            if self.prev_net_time > 0 and self.prev_net_rx > 0:
                delta_time = now - self.prev_net_time
                if delta_time > 0:
                    delta_rx = total_rx - self.prev_net_rx
                    delta_tx = total_tx - self.prev_net_tx
                    self.last_download_kbps = max(0.0, (delta_rx / delta_time) / 1024.0)
                    self.last_upload_kbps = max(0.0, (delta_tx / delta_time) / 1024.0)

            self.prev_net_rx = total_rx
            self.prev_net_tx = total_tx
            self.prev_net_time = now
        except Exception:
            pass

    def update_temp(self):
        try:
            if os.path.exists('/sys/class/thermal/thermal_zone0/temp'):
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp_raw = int(f.read().strip())
                    self.last_cpu_temp = temp_raw / 1000.0 if temp_raw > 1000 else float(temp_raw)
        except Exception:
            pass

    def poll(self):
        self.update_cpu()
        self.update_ram()
        self.update_net()
        self.update_temp()
        return {
            'cpu_percent': self.last_cpu_percent,
            'ram_used_mb': self.last_ram_used_mb,
            'ram_total_mb': self.last_ram_total_mb,
            'ram_percent': self.last_ram_percent,
            'download_kbps': self.last_download_kbps,
            'upload_kbps': self.last_upload_kbps,
            'cpu_temp': self.last_cpu_temp,
        }

system_engine = SystemMonitorEngine()
