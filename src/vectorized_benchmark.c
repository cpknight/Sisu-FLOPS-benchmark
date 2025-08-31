#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>
#include <immintrin.h>  // AVX2 intrinsics
#include <omp.h>        // OpenMP
#include <unistd.h>     // for sysconf

double get_time() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec + tv.tv_usec / 1000000.0;
}

// Single-threaded scalar benchmark
double scalar_benchmark(long long operations) {
    volatile double a = 1.23456789;
    volatile double b = 9.87654321;
    volatile double result = 0.0;
    
    double start_time = get_time();
    
    for (long long i = 0; i < operations; i++) {
        result = a * b + result;
        a = result * 0.999999;
        b = a + 1.000001;
    }
    
    double end_time = get_time();
    double elapsed = end_time - start_time;
    
    // Prevent the result from being optimized away
    if (result == 0.0) printf("Unexpected result\n");
    
    return elapsed;
}

// AVX2 vectorized benchmark (processes 4 doubles at once)
double vectorized_benchmark(long long operations) {
    // Align data for SIMD
    __attribute__((aligned(32))) double a_vals[4] = {1.1, 1.2, 1.3, 1.4};
    __attribute__((aligned(32))) double b_vals[4] = {2.1, 2.2, 2.3, 2.4};
    __attribute__((aligned(32))) double results[4] = {0.0, 0.0, 0.0, 0.0};
    
    __m256d a_vec = _mm256_load_pd(a_vals);
    __m256d b_vec = _mm256_load_pd(b_vals);
    __m256d result_vec = _mm256_load_pd(results);
    __m256d mult_factor = _mm256_set1_pd(0.999999);
    __m256d add_factor = _mm256_set1_pd(1.000001);
    
    double start_time = get_time();
    
    for (long long i = 0; i < operations / 4; i++) {
        // 4 multiply-add operations in parallel
        result_vec = _mm256_fmadd_pd(a_vec, b_vec, result_vec);
        a_vec = _mm256_mul_pd(result_vec, mult_factor);
        b_vec = _mm256_add_pd(a_vec, add_factor);
    }
    
    double end_time = get_time();
    double elapsed = end_time - start_time;
    
    // Store results to prevent optimization
    _mm256_store_pd(results, result_vec);
    if (results[0] == 0.0) printf("Unexpected result\n");
    
    return elapsed;
}

// Multi-threaded benchmark
double multithreaded_benchmark(long long operations, int num_threads) {
    volatile double global_result = 0.0;
    
    omp_set_num_threads(num_threads);
    
    double start_time = get_time();
    
    #pragma omp parallel
    {
        double local_a = 1.23456789 + omp_get_thread_num() * 0.1;
        double local_b = 9.87654321 + omp_get_thread_num() * 0.1;
        double local_result = 0.0;
        
        long long ops_per_thread = operations / num_threads;
        
        for (long long i = 0; i < ops_per_thread; i++) {
            local_result = local_a * local_b + local_result;
            local_a = local_result * 0.999999;
            local_b = local_a + 1.000001;
        }
        
        #pragma omp atomic
        global_result += local_result;
    }
    
    double end_time = get_time();
    double elapsed = end_time - start_time;
    
    // Prevent optimization
    if (global_result == 0.0) printf("Unexpected result\n");
    
    return elapsed;
}

// Multi-threaded vectorized benchmark (best of both worlds)
double multithreaded_vectorized_benchmark(long long operations, int num_threads) {
    volatile double global_result = 0.0;
    
    omp_set_num_threads(num_threads);
    
    double start_time = get_time();
    
    #pragma omp parallel
    {
        int thread_id = omp_get_thread_num();
        
        // Align data for SIMD
        __attribute__((aligned(32))) double a_vals[4] = {
            1.1 + thread_id * 0.1, 1.2 + thread_id * 0.1, 
            1.3 + thread_id * 0.1, 1.4 + thread_id * 0.1
        };
        __attribute__((aligned(32))) double b_vals[4] = {
            2.1 + thread_id * 0.1, 2.2 + thread_id * 0.1, 
            2.3 + thread_id * 0.1, 2.4 + thread_id * 0.1
        };
        __attribute__((aligned(32))) double results[4] = {0.0, 0.0, 0.0, 0.0};
        
        __m256d a_vec = _mm256_load_pd(a_vals);
        __m256d b_vec = _mm256_load_pd(b_vals);
        __m256d result_vec = _mm256_load_pd(results);
        __m256d mult_factor = _mm256_set1_pd(0.999999);
        __m256d add_factor = _mm256_set1_pd(1.000001);
        
        long long ops_per_thread = (operations / num_threads) / 4; // Divide by 4 for vectorization
        
        for (long long i = 0; i < ops_per_thread; i++) {
            result_vec = _mm256_fmadd_pd(a_vec, b_vec, result_vec);
            a_vec = _mm256_mul_pd(result_vec, mult_factor);
            b_vec = _mm256_add_pd(a_vec, add_factor);
        }
        
        _mm256_store_pd(results, result_vec);
        double thread_result = results[0] + results[1] + results[2] + results[3];
        
        #pragma omp atomic
        global_result += thread_result;
    }
    
    double end_time = get_time();
    double elapsed = end_time - start_time;
    
    // Prevent optimization
    if (global_result == 0.0) printf("Unexpected result\n");
    
    return elapsed;
}

int main() {
    const long long operations = 400000000LL; // 400 million operations
    int num_cores = sysconf(_SC_NPROCESSORS_ONLN);
    
    printf("=== Advanced FLOPS Benchmark ===\n");
    printf("CPU: 13th Gen Intel Core i5-1335U\n");
    printf("Available cores: %d\n", num_cores);
    printf("Operations per test: %lld\n\n", operations);
    
    // 1. Single-threaded scalar benchmark
    printf("1. Single-threaded Scalar Benchmark:\n");
    double scalar_time = scalar_benchmark(operations);
    double scalar_flops = operations * 4.0;
    double scalar_mflops = (scalar_flops / scalar_time) / 1000000.0;
    printf("   Time: %.6f seconds\n", scalar_time);
    printf("   MFLOPS: %.2f\n\n", scalar_mflops);
    
    // 2. Single-threaded vectorized benchmark
    printf("2. Single-threaded Vectorized (AVX2) Benchmark:\n");
    double vec_time = vectorized_benchmark(operations);
    double vec_flops = operations * 4.0; // Same number of logical operations, but vectorized
    double vec_mflops = (vec_flops / vec_time) / 1000000.0;
    printf("   Time: %.6f seconds\n", vec_time);
    printf("   MFLOPS: %.2f\n", vec_mflops);
    printf("   Speedup vs scalar: %.2fx\n\n", scalar_time / vec_time);
    
    // 3. Multi-threaded scalar benchmark
    printf("3. Multi-threaded Scalar Benchmark (%d threads):\n", num_cores);
    double mt_time = multithreaded_benchmark(operations, num_cores);
    double mt_flops = operations * 4.0;
    double mt_mflops = (mt_flops / mt_time) / 1000000.0;
    printf("   Time: %.6f seconds\n", mt_time);
    printf("   MFLOPS: %.2f\n", mt_mflops);
    printf("   Speedup vs scalar: %.2fx\n\n", scalar_time / mt_time);
    
    // 4. Multi-threaded vectorized benchmark (maximum performance)
    printf("4. Multi-threaded Vectorized Benchmark (%d threads + AVX2):\n", num_cores);
    double mtv_time = multithreaded_vectorized_benchmark(operations, num_cores);
    double mtv_flops = operations * 4.0;
    double mtv_mflops = (mtv_flops / mtv_time) / 1000000.0;
    printf("   Time: %.6f seconds\n", mtv_time);
    printf("   MFLOPS: %.2f\n", mtv_mflops);
    printf("   Speedup vs scalar: %.2fx\n\n", scalar_time / mtv_time);
    
    // Summary
    printf("=== Performance Summary ===\n");
    printf("Single-threaded scalar:      %8.2f MFLOPS\n", scalar_mflops);
    printf("Single-threaded vectorized:  %8.2f MFLOPS\n", vec_mflops);
    printf("Multi-threaded scalar:       %8.2f MFLOPS\n", mt_mflops);
    printf("Multi-threaded vectorized:   %8.2f MFLOPS (%.2f GFLOPS)\n", 
           mtv_mflops, mtv_mflops / 1000.0);
    
    return 0;
}
