# Makefile for FLOPS Benchmark Suite
# Automatically detects available features and compiles appropriate benchmarks

CC = gcc
CFLAGS_BASE = -O3 -Wall -Wextra
CFLAGS_MATH = -lm
LDFLAGS = 

# Feature detection
HAS_OPENMP := $(shell echo 'int main(){return 0;}' | $(CC) -fopenmp -x c - -o /tmp/test_openmp 2>/dev/null && echo 1 || echo 0)
HAS_AVX2 := $(shell echo 'int main(){return 0;}' | $(CC) -mavx2 -x c - -o /tmp/test_avx2 2>/dev/null && echo 1 || echo 0)
HAS_FMA := $(shell echo 'int main(){return 0;}' | $(CC) -mfma -x c - -o /tmp/test_fma 2>/dev/null && echo 1 || echo 0)
HAS_OPENCL := $(shell echo 'int main(){return 0;}' | $(CC) -lOpenCL -x c - -o /tmp/test_opencl 2>/dev/null && echo 1 || echo 0)
HAS_NATIVE := $(shell echo 'int main(){return 0;}' | $(CC) -march=native -x c - -o /tmp/test_native 2>/dev/null && echo 1 || echo 0)

# Build flags based on detected features
CFLAGS = $(CFLAGS_BASE)

ifeq ($(HAS_NATIVE),1)
    CFLAGS += -march=native
endif

ifeq ($(HAS_OPENMP),1)
    CFLAGS += -fopenmp
    LDFLAGS += -fopenmp
endif

ifeq ($(HAS_AVX2),1)
    CFLAGS += -mavx2
endif

ifeq ($(HAS_FMA),1)
    CFLAGS += -mfma
endif

# Targets
TARGETS = basic_benchmark
ifeq ($(HAS_OPENMP),1)
ifeq ($(HAS_AVX2),1)
    TARGETS += vectorized_benchmark
endif
endif

ifeq ($(HAS_OPENCL),1)
    TARGETS += gpu_benchmark
endif

.PHONY: all clean info install-deps

all: info $(TARGETS)
	@echo ""
	@echo "🎉 Build complete! Available benchmarks:"
	@for target in $(TARGETS); do echo "  - $$target"; done
	@echo ""
	@echo "Run 'python3 benchmark_runner.py' to execute benchmarks"

info:
	@echo "=== Build Configuration ==="
	@echo "Compiler: $(CC)"
	@echo "OpenMP support: $(if $(filter 1,$(HAS_OPENMP)),✓ Available,✗ Not available)"
	@echo "AVX2 support: $(if $(filter 1,$(HAS_AVX2)),✓ Available,✗ Not available)"
	@echo "FMA support: $(if $(filter 1,$(HAS_FMA)),✓ Available,✗ Not available)"
	@echo "OpenCL support: $(if $(filter 1,$(HAS_OPENCL)),✓ Available,✗ Not available)"
	@echo "Native arch: $(if $(filter 1,$(HAS_NATIVE)),✓ Available,✗ Not available)"
	@echo "CFLAGS: $(CFLAGS)"
	@echo ""

basic_benchmark: src/flops_benchmark.c
	$(CC) $(CFLAGS_BASE) -o $@ $< $(CFLAGS_MATH)

vectorized_benchmark: src/vectorized_benchmark.c
	$(CC) $(CFLAGS) -o $@ $< $(CFLAGS_MATH) $(LDFLAGS)

gpu_benchmark: src/gpu_benchmark.c
	$(CC) $(CFLAGS_BASE) -o $@ $< -lOpenCL

# Python dependencies (optional)
install-deps:
	@echo "Installing Python dependencies..."
	pip3 install --user rich click psutil || echo "Note: Install python3-pip if not available"

# Create capabilities JSON for Python script
capabilities.json: Makefile
	@echo "Generating capabilities file..."
	@echo '{' > $@
	@echo '  "openmp": $(HAS_OPENMP),' >> $@
	@echo '  "avx2": $(HAS_AVX2),' >> $@
	@echo '  "fma": $(HAS_FMA),' >> $@
	@echo '  "opencl": $(HAS_OPENCL),' >> $@
	@echo '  "native": $(HAS_NATIVE),' >> $@
	@echo '  "targets": [$(foreach target,$(TARGETS),"$(target)"$(if $(filter-out $(lastword $(TARGETS)),$(target)),$(comma)))]' >> $@
	@echo '}' >> $@

clean:
	rm -f $(TARGETS) capabilities.json
	rm -f /tmp/test_*

help:
	@echo "Available targets:"
	@echo "  all          - Build all available benchmarks"
	@echo "  info         - Show build configuration"
	@echo "  install-deps - Install Python dependencies"
	@echo "  clean        - Remove built files"
	@echo "  help         - Show this help"
