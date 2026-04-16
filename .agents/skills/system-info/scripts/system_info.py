#!/usr/bin/env python3
"""
System Info Tool
Based on: https://github.com/giampaolo/psutil

Usage:
    python system_info.py
    python system_info.py --cpu
    python system_info.py --memory
"""

import argparse
import os
import platform
import sys

def format_bytes(bytes_val):
    """Format bytes to human readable."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} PB"

def get_basic_info():
    """Get basic system info without psutil."""
    return {
        'system': platform.system(),
        'node': platform.node(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python': platform.python_version()
    }

def get_cpu_info():
    """Get CPU information."""
    try:
        import psutil
        return {
            'cores_physical': psutil.cpu_count(logical=False),
            'cores_logical': psutil.cpu_count(logical=True),
            'usage_percent': psutil.cpu_percent(interval=1),
            'freq': psutil.cpu_freq()
        }
    except ImportError:
        return {'cores': os.cpu_count()}

def get_memory_info():
    """Get memory information."""
    try:
        import psutil
        mem = psutil.virtual_memory()
        return {
            'total': format_bytes(mem.total),
            'available': format_bytes(mem.available),
            'used': format_bytes(mem.used),
            'percent': mem.percent
        }
    except ImportError:
        return None

def get_disk_info():
    """Get disk information."""
    try:
        import psutil
        partitions = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                partitions.append({
                    'device': part.device,
                    'mountpoint': part.mountpoint,
                    'total': format_bytes(usage.total),
                    'used': format_bytes(usage.used),
                    'free': format_bytes(usage.free),
                    'percent': usage.percent
                })
            except:
                pass
        return partitions
    except ImportError:
        return None

def main():
    parser = argparse.ArgumentParser(description="System information")
    parser.add_argument('--cpu', '-c', action='store_true')
    parser.add_argument('--memory', '-m', action='store_true')
    parser.add_argument('--disk', '-d', action='store_true')
    parser.add_argument('--processes', '-p', action='store_true')
    parser.add_argument('--top', '-t', type=int, default=10)
    args = parser.parse_args()
    
    if args.cpu:
        info = get_cpu_info()
        print("CPU Information:")
        for k, v in info.items():
            print(f"  {k}: {v}")
    
    elif args.memory:
        info = get_memory_info()
        if info:
            print("Memory Information:")
            for k, v in info.items():
                print(f"  {k}: {v}")
        else:
            print("Install psutil for memory info: pip install psutil")
    
    elif args.disk:
        disks = get_disk_info()
        if disks:
            print("Disk Information:")
            for d in disks:
                print(f"\n  {d['device']} ({d['mountpoint']})")
                print(f"    Total: {d['total']}, Used: {d['used']} ({d['percent']}%)")
        else:
            print("Install psutil for disk info: pip install psutil")
    
    else:
        # Overview
        info = get_basic_info()
        print("System Information")
        print("=" * 40)
        for k, v in info.items():
            print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
