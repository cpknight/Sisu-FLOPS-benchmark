#!/usr/bin/env python3
"""
FLOPS Benchmark Suite Runner
A beautiful command-line interface for running floating-point performance benchmarks
"""

import subprocess
import time
import os
import sys
import json
import platform
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    import click
    CLICK_AVAILABLE = True
except ImportError:
    CLICK_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class BenchmarkRunner:
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.results = {}
        self.capabilities = self._detect_capabilities()
        
    def _detect_capabilities(self) -> Dict:
        """Detect system capabilities and available benchmarks"""
        caps = {
            "cpu_info": self._get_cpu_info(),
            "memory_info": self._get_memory_info(),
            "benchmarks": self._detect_benchmarks(),
            "features": self._detect_features()
        }
        return caps
    
    def _get_cpu_info(self) -> Dict:
        """Get CPU information"""
        info = {
            "model": "Unknown",
            "cores": os.cpu_count() or 1,
            "threads": os.cpu_count() or 1
        }
        
        try:
            # Try to get CPU model from /proc/cpuinfo
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'model name' in line:
                        info["model"] = line.split(':')[1].strip()
                        break
        except:
            pass
            
        if PSUTIL_AVAILABLE:
            try:
                info["cores"] = psutil.cpu_count(logical=False)
                info["threads"] = psutil.cpu_count(logical=True)
            except:
                pass
                
        return info
    
    def _get_memory_info(self) -> Dict:
        """Get memory information"""
        info = {"total_gb": "Unknown"}
        
        if PSUTIL_AVAILABLE:
            try:
                mem = psutil.virtual_memory()
                info["total_gb"] = f"{mem.total / (1024**3):.1f}"
            except:
                pass
                
        return info
    
    def _detect_benchmarks(self) -> Dict:
        """Detect which benchmark executables are available"""
        benchmarks = {}
        benchmark_files = [
            ("basic", "basic_benchmark"),
            ("vectorized", "vectorized_benchmark"), 
            ("gpu", "gpu_benchmark")
        ]
        
        for name, filename in benchmark_files:
            path = Path(filename).resolve()  # Get absolute path
            benchmarks[name] = {
                "available": path.exists() and path.is_file(),
                "path": str(path),
                "executable": os.access(path, os.X_OK) if path.exists() else False
            }
            
        return benchmarks
    
    def _detect_features(self) -> Dict:
        """Detect compiler and system features"""
        features = {}
        
        # Test compiler features
        test_flags = [
            ("openmp", "-fopenmp"),
            ("avx2", "-mavx2"),
            ("fma", "-mfma"),
            ("native", "-march=native")
        ]
        
        for feature, flag in test_flags:
            try:
                result = subprocess.run(
                    ["gcc", flag, "-x", "c", "-", "-o", "/tmp/test_feature"],
                    input="int main(){return 0;}",
                    text=True,
                    capture_output=True
                )
                features[feature] = result.returncode == 0
            except:
                features[feature] = False
        
        # Test OpenCL
        try:
            result = subprocess.run(
                ["gcc", "-lOpenCL", "-x", "c", "-", "-o", "/tmp/test_opencl"],
                input="int main(){return 0;}",
                text=True,
                capture_output=True
            )
            features["opencl"] = result.returncode == 0
        except:
            features["opencl"] = False
            
        return features
    
    def _run_benchmark(self, benchmark_name: str, executable_path: str) -> Optional[Dict]:
        """Run a benchmark and parse its output"""
        try:
            start_time = time.time()
            result = subprocess.run([executable_path], capture_output=True, text=True, timeout=120)
            end_time = time.time()
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr,
                    "duration": end_time - start_time
                }
            
            # Parse output for MFLOPS values
            mflops_values = []
            gflops_values = []
            
            for line in result.stdout.split('\n'):
                # Look for MFLOPS values
                mflops_match = re.search(r'MFLOPS:\s*([\d.]+)', line)
                if mflops_match:
                    mflops_values.append(float(mflops_match.group(1)))
                
                # Look for GFLOPS values  
                gflops_match = re.search(r'([\d.]+)\s*GFLOPS', line)
                if gflops_match:
                    gflops_values.append(float(gflops_match.group(1)))
            
            return {
                "success": True,
                "output": result.stdout,
                "mflops_values": mflops_values,
                "gflops_values": gflops_values,
                "max_mflops": max(mflops_values) if mflops_values else 0,
                "max_gflops": max(gflops_values) if gflops_values else max(mflops_values)/1000 if mflops_values else 0,
                "duration": end_time - start_time
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Benchmark timed out after 120 seconds",
                "duration": 120
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": 0
            }
    
    def _print_header(self):
        """Print beautiful header"""
        if RICH_AVAILABLE:
            title = Text("🚀 FLOPS Benchmark Suite", style="bold magenta")
            subtitle = Text("High-Performance Floating-Point Benchmarking", style="dim")
            
            panel = Panel.fit(
                f"{title}\n{subtitle}",
                border_style="blue",
                padding=(1, 2)
            )
            self.console.print(panel)
        else:
            print("=" * 60)
            print("🚀 FLOPS Benchmark Suite")
            print("High-Performance Floating-Point Benchmarking")
            print("=" * 60)
    
    def _print_system_info(self):
        """Print system information"""
        cpu_info = self.capabilities["cpu_info"]
        mem_info = self.capabilities["memory_info"]
        features = self.capabilities["features"]
        
        if RICH_AVAILABLE:
            table = Table(title="System Information", box=box.ROUNDED)
            table.add_column("Component", style="cyan", width=20)
            table.add_column("Details", style="white")
            
            table.add_row("CPU Model", cpu_info["model"])
            table.add_row("CPU Cores", f"{cpu_info['cores']} cores, {cpu_info['threads']} threads")
            table.add_row("Memory", f"{mem_info['total_gb']} GB")
            table.add_row("Platform", f"{platform.system()} {platform.release()}")
            
            # Feature availability
            feature_status = []
            for feature, available in features.items():
                status = "✓" if available else "✗"
                color = "green" if available else "red"
                feature_status.append(f"[{color}]{status}[/{color}] {feature.upper()}")
            
            table.add_row("Features", " ".join(feature_status))
            
            self.console.print(table)
        else:
            print("\n=== System Information ===")
            print(f"CPU Model: {cpu_info['model']}")
            print(f"CPU Cores: {cpu_info['cores']} cores, {cpu_info['threads']} threads")
            print(f"Memory: {mem_info['total_gb']} GB")
            print(f"Platform: {platform.system()} {platform.release()}")
            
            feature_list = []
            for feature, available in features.items():
                status = "✓" if available else "✗"
                feature_list.append(f"{status} {feature.upper()}")
            print(f"Features: {', '.join(feature_list)}")
    
    def _print_benchmark_status(self):
        """Print available benchmarks"""
        benchmarks = self.capabilities["benchmarks"]
        
        if RICH_AVAILABLE:
            table = Table(title="Available Benchmarks", box=box.ROUNDED)
            table.add_column("Benchmark", style="cyan", width=25)
            table.add_column("Status", style="white", width=15)
            table.add_column("Description", style="dim")
            
            descriptions = {
                "basic": "Single-threaded scalar operations",
                "vectorized": "Multi-threaded + AVX2 vectorization",
                "gpu": "GPU/OpenCL compute (if available)"
            }
            
            for name, info in benchmarks.items():
                if info["available"] and info["executable"]:
                    status = "[green]✓ Ready[/green]"
                elif info["available"]:
                    status = "[yellow]⚠ Not executable[/yellow]"
                else:
                    status = "[red]✗ Missing[/red]"
                
                table.add_row(name.title(), status, descriptions.get(name, ""))
            
            self.console.print(table)
        else:
            print("\n=== Available Benchmarks ===")
            descriptions = {
                "basic": "Single-threaded scalar operations",
                "vectorized": "Multi-threaded + AVX2 vectorization", 
                "gpu": "GPU/OpenCL compute (if available)"
            }
            
            for name, info in benchmarks.items():
                if info["available"] and info["executable"]:
                    status = "✓ Ready"
                elif info["available"]:
                    status = "⚠ Not executable"
                else:
                    status = "✗ Missing"
                
                print(f"  {name.title()}: {status} - {descriptions.get(name, '')}")
    
    def run_benchmarks(self, verbose: bool = False):
        """Run all available benchmarks with beautiful output"""
        self._print_header()
        self._print_system_info()
        self._print_benchmark_status()
        
        available_benchmarks = [
            (name, info) for name, info in self.capabilities["benchmarks"].items()
            if info["available"] and info["executable"]
        ]
        
        if not available_benchmarks:
            if RICH_AVAILABLE:
                self.console.print("\n[red]❌ No benchmarks available to run![/red]")
                self.console.print("[yellow]Run 'make' to build benchmarks first.[/yellow]")
            else:
                print("\n❌ No benchmarks available to run!")
                print("Run 'make' to build benchmarks first.")
            return
        
        # Results table
        if RICH_AVAILABLE:
            self.console.print(f"\n🏃 Running {len(available_benchmarks)} benchmark(s)...\n")
        else:
            print(f"\n🏃 Running {len(available_benchmarks)} benchmark(s)...\n")
        
        results_data = []
        
        for benchmark_name, benchmark_info in available_benchmarks:
            if RICH_AVAILABLE:
                with self.console.status(f"[bold green]Running {benchmark_name} benchmark...", spinner="dots"):
                    result = self._run_benchmark(benchmark_name, benchmark_info["path"])
            else:
                print(f"Running {benchmark_name} benchmark...")
                result = self._run_benchmark(benchmark_name, benchmark_info["path"])
            
            if result["success"]:
                results_data.append({
                    "name": benchmark_name,
                    "mflops": result["max_mflops"],
                    "gflops": result["max_gflops"],
                    "duration": result["duration"],
                    "details": result["mflops_values"]
                })
                
                if verbose and RICH_AVAILABLE:
                    self.console.print(f"[green]✓[/green] {benchmark_name} completed in {result['duration']:.2f}s")
                elif verbose:
                    print(f"✓ {benchmark_name} completed in {result['duration']:.2f}s")
            else:
                if RICH_AVAILABLE:
                    self.console.print(f"[red]✗[/red] {benchmark_name} failed: {result['error']}")
                else:
                    print(f"✗ {benchmark_name} failed: {result['error']}")
        
        # Display results
        self._display_results(results_data)
        
        # Display detailed output if verbose
        if verbose:
            self._display_detailed_output()
    
    def _display_results(self, results_data: List[Dict]):
        """Display benchmark results in a beautiful table"""
        if not results_data:
            return
            
        if RICH_AVAILABLE:
            # Create results table
            table = Table(title="🏆 Benchmark Results", box=box.HEAVY_EDGE)
            table.add_column("Benchmark", style="cyan", width=20)
            table.add_column("Performance", style="white", width=20)
            table.add_column("Relative", style="yellow", width=15)
            table.add_column("Duration", style="dim", width=10)
            
            # Find baseline (basic benchmark) for relative comparison
            baseline_mflops = None
            for result in results_data:
                if result["name"] == "basic":
                    baseline_mflops = result["mflops"]
                    break
            if not baseline_mflops and results_data:
                baseline_mflops = min(r["mflops"] for r in results_data)
            
            # Add rows
            for result in results_data:
                name = result["name"].title()
                
                if result["gflops"] >= 1.0:
                    perf = f"{result['gflops']:.2f} GFLOPS"
                    perf_style = "bold green"
                else:
                    perf = f"{result['mflops']:.0f} MFLOPS"
                    perf_style = "green" if result["mflops"] > 1000 else "yellow"
                
                relative = f"{result['mflops']/baseline_mflops:.1f}x" if baseline_mflops else "N/A"
                duration = f"{result['duration']:.1f}s"
                
                table.add_row(
                    name,
                    Text(perf, style=perf_style),
                    relative,
                    duration
                )
            
            self.console.print(table)
            
            # Summary stats
            max_result = max(results_data, key=lambda x: x["mflops"])
            total_gflops = max_result["gflops"]
            
            summary = Panel(
                f"🎯 Peak Performance: [bold green]{total_gflops:.2f} GFLOPS[/bold green]\n"
                f"💡 Best Configuration: [cyan]{max_result['name'].title()}[/cyan]\n"
                f"⚡ Speed Improvement: [yellow]{max_result['mflops']/baseline_mflops:.1f}x over baseline[/yellow]",
                title="Summary",
                border_style="green"
            )
            self.console.print(summary)
            
        else:
            # Fallback text output
            print("\n=== Benchmark Results ===")
            print(f"{'Benchmark':<20} {'Performance':<20} {'Relative':<15} {'Duration':<10}")
            print("-" * 65)
            
            baseline_mflops = None
            for result in results_data:
                if result["name"] == "basic":
                    baseline_mflops = result["mflops"]
                    break
            if not baseline_mflops and results_data:
                baseline_mflops = min(r["mflops"] for r in results_data)
            
            for result in results_data:
                name = result["name"].title()
                
                if result["gflops"] >= 1.0:
                    perf = f"{result['gflops']:.2f} GFLOPS"
                else:
                    perf = f"{result['mflops']:.0f} MFLOPS"
                
                relative = f"{result['mflops']/baseline_mflops:.1f}x" if baseline_mflops else "N/A"
                duration = f"{result['duration']:.1f}s"
                
                print(f"{name:<20} {perf:<20} {relative:<15} {duration:<10}")
            
            # Summary
            max_result = max(results_data, key=lambda x: x["mflops"])
            print(f"\n🎯 Peak Performance: {max_result['gflops']:.2f} GFLOPS")
            print(f"💡 Best Configuration: {max_result['name'].title()}")
    
    def _display_detailed_output(self):
        """Display detailed benchmark output"""
        if RICH_AVAILABLE:
            self.console.print("\n" + "="*60)
            self.console.print("[bold]Detailed Benchmark Output:[/bold]")
            self.console.print("="*60)
        else:
            print("\n" + "="*60)
            print("Detailed Benchmark Output:")
            print("="*60)
        
        for name, result in self.results.items():
            if result.get("success"):
                if RICH_AVAILABLE:
                    panel = Panel(
                        result["output"],
                        title=f"{name.title()} Benchmark",
                        border_style="blue"
                    )
                    self.console.print(panel)
                else:
                    print(f"\n--- {name.title()} Benchmark ---")
                    print(result["output"])


def check_dependencies():
    """Check for required dependencies and provide installation instructions"""
    missing = []
    
    if not RICH_AVAILABLE:
        missing.append("rich")
    if not CLICK_AVAILABLE:
        missing.append("click") 
    if not PSUTIL_AVAILABLE:
        missing.append("psutil")
    
    if missing:
        print("⚠️  Some optional Python packages are missing for enhanced output:")
        print(f"   Missing: {', '.join(missing)}")
        print(f"   Install with: pip3 install --user {' '.join(missing)}")
        print("   Continuing with basic output...\n")


@click.command() if CLICK_AVAILABLE else lambda f: f
@click.option('--verbose', '-v', is_flag=True, help='Show detailed benchmark output')
@click.option('--build', '-b', is_flag=True, help='Build benchmarks before running')
def main(verbose: bool = False, build: bool = False):
    """Run comprehensive floating-point performance benchmarks"""
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    check_dependencies()
    
    if build:
        print("🔨 Building benchmarks...")
        result = subprocess.run(["make", "all"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Build failed: {result.stderr}")
            return
        print("✅ Build successful!\n")
    
    runner = BenchmarkRunner()
    runner.run_benchmarks(verbose=verbose)


if __name__ == "__main__":
    if CLICK_AVAILABLE:
        main()
    else:
        # Fallback without click
        verbose = "--verbose" in sys.argv or "-v" in sys.argv
        build = "--build" in sys.argv or "-b" in sys.argv
        main(verbose, build)
