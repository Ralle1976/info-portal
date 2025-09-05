#!/usr/bin/env python3
"""
Performance Benchmark Suite für QR-Info-Portal
Analysiert und optimiert die Performance der Anwendung
"""
import time
import requests
import statistics
import json
import psutil
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import subprocess
import threading


class PerformanceBenchmark:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = {}
        self.server_process = None
        
    def start_server(self):
        """Startet den Flask Server für Tests"""
        try:
            # Prüfe ob Server bereits läuft
            response = requests.get(f"{self.base_url}/healthz", timeout=2)
            print("Server ist bereits verfügbar")
            return True
        except:
            print("Starte Flask Server...")
            # Server im Hintergrund starten
            env = os.environ.copy()
            env['FLASK_ENV'] = 'production'
            self.server_process = subprocess.Popen(
                ['python', 'run.py'],
                cwd='/mnt/c/Users/tango/Desktop/Homepage/qr-info-portal'
            )
            # Warte auf Server-Start
            for _ in range(10):
                try:
                    response = requests.get(f"{self.base_url}/healthz", timeout=2)
                    if response.status_code == 200:
                        print("Server erfolgreich gestartet")
                        return True
                except:
                    time.sleep(1)
            return False
    
    def measure_page_performance(self, endpoint: str, iterations: int = 10) -> Dict:
        """Misst Performance einer spezifischen Seite"""
        times = []
        sizes = []
        status_codes = []
        
        for i in range(iterations):
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}{endpoint}")
                end_time = time.time()
                
                times.append(end_time - start_time)
                sizes.append(len(response.content))
                status_codes.append(response.status_code)
                
                # Kurze Pause zwischen Requests
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Fehler bei Request {i+1}: {e}")
                continue
        
        if not times:
            return {"error": "Keine erfolgreichen Requests"}
        
        return {
            "endpoint": endpoint,
            "avg_time": statistics.mean(times),
            "median_time": statistics.median(times),
            "min_time": min(times),
            "max_time": max(times),
            "avg_size": statistics.mean(sizes),
            "total_requests": len(times),
            "successful_requests": len([sc for sc in status_codes if sc == 200])
        }
    
    def measure_system_resources(self, duration_seconds: int = 30):
        """Misst Systemressourcen während der Laufzeit"""
        cpu_usage = []
        memory_usage = []
        
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            cpu_usage.append(psutil.cpu_percent(interval=1))
            memory_usage.append(psutil.virtual_memory().percent)
        
        return {
            "avg_cpu": statistics.mean(cpu_usage),
            "max_cpu": max(cpu_usage),
            "avg_memory": statistics.mean(memory_usage),
            "max_memory": max(memory_usage)
        }
    
    def analyze_asset_sizes(self) -> Dict:
        """Analysiert Asset-Größen"""
        static_dir = Path('/mnt/c/Users/tango/Desktop/Homepage/qr-info-portal/app/static')
        assets = {}
        
        # CSS Files
        css_dir = static_dir / 'css'
        if css_dir.exists():
            css_files = list(css_dir.glob('*.css'))
            assets['css'] = {
                'count': len(css_files),
                'total_size': sum(f.stat().st_size for f in css_files),
                'files': [{'name': f.name, 'size': f.stat().st_size} for f in css_files]
            }
        
        # JS Files
        js_dir = static_dir / 'js'
        if js_dir.exists():
            js_files = list(js_dir.glob('*.js'))
            assets['js'] = {
                'count': len(js_files),
                'total_size': sum(f.stat().st_size for f in js_files),
                'files': [{'name': f.name, 'size': f.stat().st_size} for f in js_files]
            }
        
        # QR Images
        qr_dir = static_dir / 'qr'
        if qr_dir.exists():
            qr_files = list(qr_dir.glob('*.png')) + list(qr_dir.glob('*.svg'))
            assets['qr'] = {
                'count': len(qr_files),
                'total_size': sum(f.stat().st_size for f in qr_files),
                'files': [{'name': f.name, 'size': f.stat().st_size} for f in qr_files]
            }
        
        return assets
    
    def run_comprehensive_benchmark(self):
        """Führt vollständige Performance-Analyse durch"""
        print("🚀 Starte Performance-Benchmark...")
        
        # Server starten
        if not self.start_server():
            print("❌ Server konnte nicht gestartet werden")
            return None
        
        # Warte kurz für Server-Stabilisierung
        time.sleep(2)
        
        endpoints = [
            "/",
            "/week", 
            "/month",
            "/kiosk/single",
            "/kiosk/triple",
            "/qr",
            "/qr.svg",
            "/healthz"
        ]
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "pages": {},
            "assets": self.analyze_asset_sizes(),
            "system": {}
        }
        
        # Teste jede Seite
        for endpoint in endpoints:
            print(f"🔍 Teste {endpoint}...")
            page_result = self.measure_page_performance(endpoint)
            results["pages"][endpoint] = page_result
        
        # System-Ressourcen messen
        print("📊 Messe Systemressourcen...")
        results["system"] = self.measure_system_resources(30)
        
        # Speichere Ergebnisse
        with open('performance_baseline_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        self.results = results
        return results
    
    def generate_report(self):
        """Generiert Performance-Report"""
        if not self.results:
            print("❌ Keine Benchmark-Ergebnisse verfügbar")
            return
        
        report_lines = [
            "# Performance Baseline Report",
            f"**Generated:** {self.results['timestamp']}",
            "",
            "## Page Performance (ms)",
            ""
        ]
        
        # Page Performance Table
        for endpoint, data in self.results["pages"].items():
            if "error" in data:
                report_lines.append(f"- **{endpoint}**: ERROR - {data['error']}")
            else:
                avg_time_ms = data["avg_time"] * 1000
                size_kb = data["avg_size"] / 1024
                report_lines.append(
                    f"- **{endpoint}**: {avg_time_ms:.1f}ms (avg), {size_kb:.1f}KB"
                )
        
        report_lines.extend([
            "",
            "## Asset Analysis",
            ""
        ])
        
        # Asset Analysis
        for asset_type, data in self.results["assets"].items():
            size_kb = data["total_size"] / 1024
            report_lines.append(f"- **{asset_type.upper()}**: {data['count']} files, {size_kb:.1f}KB total")
        
        report_lines.extend([
            "",
            "## System Resources",
            f"- **CPU**: {self.results['system']['avg_cpu']:.1f}% (avg), {self.results['system']['max_cpu']:.1f}% (max)",
            f"- **Memory**: {self.results['system']['avg_memory']:.1f}% (avg), {self.results['system']['max_memory']:.1f}% (max)",
            ""
        ])
        
        # Performance Issues Identified
        issues = self._identify_performance_issues()
        if issues:
            report_lines.extend([
                "## 🚨 Performance Issues Identified",
                ""
            ])
            for issue in issues:
                report_lines.append(f"- {issue}")
        
        report = "\n".join(report_lines)
        
        with open('performance_baseline_report.md', 'w') as f:
            f.write(report)
        
        print("📄 Performance Report generiert: performance_baseline_report.md")
        return report
    
    def _identify_performance_issues(self) -> List[str]:
        """Identifiziert Performance-Probleme"""
        issues = []
        
        # Prüfe Page Load Times
        for endpoint, data in self.results["pages"].items():
            if "error" not in data and data["avg_time"] > 1.0:
                issues.append(f"Langsame Seite {endpoint}: {data['avg_time']*1000:.1f}ms")
        
        # Prüfe Asset-Größen
        assets = self.results["assets"]
        if assets.get("css", {}).get("total_size", 0) > 100 * 1024:  # 100KB
            size_kb = assets["css"]["total_size"] / 1024
            issues.append(f"CSS-Assets zu groß: {size_kb:.1f}KB ({assets['css']['count']} Dateien)")
        
        if assets.get("js", {}).get("total_size", 0) > 200 * 1024:  # 200KB
            size_kb = assets["js"]["total_size"] / 1024
            issues.append(f"JS-Assets zu groß: {size_kb:.1f}KB ({assets['js']['count']} Dateien)")
        
        # Prüfe QR-Images
        if assets.get("qr", {}).get("count", 0) > 10:
            count = assets["qr"]["count"]
            issues.append(f"Zu viele QR-Codes: {count} Dateien (vermutlich temporäre)")
        
        return issues


if __name__ == "__main__":
    print("🎯 Performance Optimization Agent - QR-Info-Portal")
    print("=" * 60)
    
    benchmark = PerformanceBenchmark()
    
    # Baseline messen
    results = benchmark.run_comprehensive_benchmark()
    if results:
        benchmark.generate_report()
        print("✅ Baseline-Messung abgeschlossen")
    else:
        print("❌ Benchmark fehlgeschlagen")