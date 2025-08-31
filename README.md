# Sisu FLOPS Benchmark Suite 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![C](https://img.shields.io/badge/c-%2300599C.svg?style=flat&logo=c&logoColor=white)](https://en.wikipedia.org/wiki/C_(programming_language))
[![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey)](https://github.com/cpknight/Sisu-FLOPS-benchmark)

A comprehensive floating-point performance benchmark suite that automatically detects system capabilities and runs appropriate tests. **Sisu** (Finnish for "determination" or "grit") reflects the persistent pursuit of maximum computational performance.

![Demo](https://via.placeholder.com/800x400/1a1a1a/00ff00?text=Beautiful+CLI+Output+Screenshot)

## ✨ Features

- 🔍 **Smart Capability Detection**: Automatically detects AVX2, OpenMP, OpenCL support
- 🏎️ **Multiple Benchmark Types**: 
  - Single-threaded scalar operations
  - Multi-threaded with OpenMP
  - Vectorized operations with AVX2/FMA
  - GPU compute with OpenCL (if available)
- 🎨 **Beautiful CLI Output**: Rich terminal interface with tables, progress bars, and colors
- 🌐 **Cross-Platform**: Works on different systems with graceful capability detection
- 📊 **Comprehensive Results**: Detailed performance analysis with speedup calculations

## Quick Start

### 1. Build Benchmarks
```bash
make
```

### 2. Run Benchmarks
```bash
python3 benchmark_runner.py
```

### 3. Detailed Output
```bash
python3 benchmark_runner.py --verbose
```

### 4. Build and Run in One Command
```bash
python3 benchmark_runner.py --build
```

## Requirements

### Essential
- GCC compiler
- Make

### Optional (for enhanced features)
- OpenMP support (`libgomp-dev` on Ubuntu)
- Python packages: `rich`, `click`, `psutil`

Install Python dependencies:
```bash
pip3 install rich click psutil
# or
make install-deps
```

## Benchmark Types

### Basic Benchmark
- Single-threaded scalar floating-point operations
- Baseline performance measurement

### Vectorized Benchmark  
- Multi-threaded execution using all CPU cores
- AVX2 vectorization (4 operations per instruction)
- FMA (Fused Multiply-Add) instructions
- Represents maximum CPU floating-point performance

### GPU Benchmark (if available)
- OpenCL-based GPU compute
- Utilizes integrated or discrete GPU
- Requires OpenCL runtime and development headers

## System Compatibility

The benchmark automatically adapts to your system:

- **No OpenMP**: Builds basic benchmark only
- **No AVX2**: Falls back to scalar operations
- **No OpenCL**: Skips GPU benchmark
- **No Python packages**: Uses fallback text output

## Expected Performance

Typical results for modern systems:
- **Basic**: 500-1,000 MFLOPS
- **Vectorized**: 10-50 GFLOPS (CPU)
- **GPU**: 50-500+ GFLOPS (depends on GPU)

## 📁 Project Structure

```
Sisu-FLOPS-benchmark/
├── src/
│   ├── flops_benchmark.c      # Basic single-threaded benchmark
│   ├── vectorized_benchmark.c # Advanced multi-threaded + vectorized benchmark
│   └── gpu_benchmark.c        # OpenCL GPU benchmark
├── benchmark_runner.py        # Python CLI wrapper
├── Makefile                   # Smart build system
├── README.md                  # This documentation
├── LICENSE                    # MIT License
└── .gitignore                 # Git ignore rules
```

## Usage Examples

```bash
# Quick run
python3 benchmark_runner.py

# Build and run with detailed output
python3 benchmark_runner.py --build --verbose

# Just build benchmarks
make

# Clean build artifacts
make clean

# Show build configuration
make info
```

## Troubleshooting

### OpenMP Not Available
Install development package:
```bash
# Ubuntu/Debian
sudo apt install libgomp1 libomp-dev

# CentOS/RHEL
sudo yum install libgomp-devel
```

### OpenCL Not Available
Install OpenCL:
```bash
# Ubuntu/Debian  
sudo apt install opencl-headers ocl-icd-opencl-dev

# For Intel GPU
sudo apt install intel-opencl-icd
```

### Python Packages Missing
```bash
pip3 install --user rich click psutil
```

## Understanding Results

- **MFLOPS**: Million Floating-Point Operations Per Second
- **GFLOPS**: Billion Floating-Point Operations Per Second  
- **Relative**: Performance multiplier compared to baseline
- **Vectorized**: Uses SIMD instructions for parallel operations
- **Multi-threaded**: Utilizes all CPU cores simultaneously

The "Vectorized" benchmark typically provides the best CPU performance by combining both multi-threading and vectorization.

## 📈 Sample Results

```
🚀 FLOPS Benchmark Suite
High-Performance Floating-Point Benchmarking

                        System Information                        
┌──────────────────────┬─────────────────────────────────────────┐
│ Component            │ Details                                 │
├──────────────────────┼─────────────────────────────────────────┤
│ CPU Model            │ 13th Gen Intel(R) Core(TM) i5-1335U     │
│ CPU Cores            │ 10 cores, 12 threads                    │
│ Memory               │ 23.3 GB                                 │
│ Platform             │ Linux 6.12.10-76061203-generic          │
│ Features             │ ✓ OPENMP ✓ AVX2 ✓ FMA ✓ NATIVE ✗ OPENCL │
└──────────────────────┴─────────────────────────────────────────┘

                             🏆 Benchmark Results                             
┌──────────────────────┬──────────────────────┬─────────────────┬────────────┐
│ Benchmark            │ Performance          │ Relative        │ Duration   │
├──────────────────────┼──────────────────────┼─────────────────┼────────────┤
│ Basic                │ 624 MFLOPS           │ 1.0x            │ 0.6s       │
│ Vectorized           │ 46.95 GFLOPS         │ 75.3x           │ 2.7s       │
└──────────────────────┴──────────────────────┴─────────────────┴────────────┘

🎯 Peak Performance: 46.95 GFLOPS
💡 Best Configuration: Vectorized
⚡ Speed Improvement: 75.3x over baseline
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/cpknight/Sisu-FLOPS-benchmark.git
   cd Sisu-FLOPS-benchmark
   ```

2. **Install dependencies (optional)**
   ```bash
   # For enhanced CLI output
   pip3 install rich click psutil
   
   # Or use make
   make install-deps
   ```

3. **Build and run**
   ```bash
   make
   python3 benchmark_runner.py
   ```

## 🎯 Benchmarks Explained

| Benchmark | Description | Technology | Expected Speedup |
|-----------|-------------|------------|------------------|
| **Basic** | Single-threaded, scalar operations | Standard C | 1x (baseline) |
| **Vectorized** | Multi-threaded + SIMD | OpenMP + AVX2/FMA | 20-100x |
| **GPU** | Parallel compute on GPU | OpenCL | 50-1000x* |

*GPU performance varies significantly based on hardware

## 💻 System Requirements

### Minimum
- GCC 4.9+ or Clang 3.4+
- Make
- POSIX-compliant system (Linux, macOS, WSL)

### Recommended
- GCC 9+ (for best optimization)
- CPU with AVX2 support (2013+)
- OpenMP support
- Python 3.7+ with `rich`, `click`, `psutil`

### Optional
- OpenCL 1.2+ runtime and headers
- GPU with OpenCL support

## 🏗️ Architecture

The benchmark suite consists of:

```
Sisu-FLOPS-benchmark/
├── src/
│   ├── flops_benchmark.c      # Basic benchmark
│   ├── vectorized_benchmark.c # Advanced CPU benchmark
│   └── gpu_benchmark.c        # GPU/OpenCL benchmark
├── benchmark_runner.py        # Python CLI wrapper
├── Makefile                   # Smart build system
├── README.md                  # This file
└── LICENSE                    # MIT License
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Areas for improvement:

- Additional GPU backends (CUDA, Vulkan Compute)
- ARM NEON vectorization support
- Additional benchmark algorithms (matrix multiplication, FFT)
- Windows MSVC support
- Continuous Integration setup

## 📊 Performance Tips

To get the best performance:

1. **Close other applications** to reduce CPU/memory contention
2. **Set CPU governor to performance**: `sudo cpupower frequency-set -g performance`
3. **Disable CPU throttling** if thermal limits are hit
4. **Use latest GCC** for best auto-vectorization
5. **Run multiple times** and take the best result

## 🔬 Technical Details

### Floating-Point Operations Counted
- **Fused Multiply-Add (FMA)**: `a * b + c` (counted as 2 ops)
- **Multiplication**: `a * b` (counted as 1 op)
- **Addition**: `a + b` (counted as 1 op)

### Vectorization
- **AVX2**: 256-bit vectors, 4 double-precision ops per instruction
- **FMA**: Fused multiply-add reduces latency and increases throughput
- **OpenMP**: Thread-level parallelism across all CPU cores

## 📝 Credits

This benchmark suite was created with the assistance of:
- **[Warp Terminal](https://www.warp.dev/)** - The AI-powered terminal that made development seamless
- **Claude 3.5 Sonnet** - AI assistance for code generation and optimization
- **cpknight** - Project creator and maintainer

Special thanks to the open-source community for the foundational libraries:
- **OpenMP** for multi-threading
- **Intel Intrinsics** for vectorization
- **OpenCL** for GPU compute
- **Rich** for beautiful terminal output
