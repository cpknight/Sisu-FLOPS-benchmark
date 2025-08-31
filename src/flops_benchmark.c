#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>

double get_time() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec + tv.tv_usec / 1000000.0;
}

int main() {
    const long long operations = 100000000LL; // 100 million operations
    volatile double a = 1.23456789;
    volatile double b = 9.87654321;
    volatile double result = 0.0;
    
    printf("Running floating-point benchmark...\n");
    printf("Operations: %lld\n", operations);
    
    double start_time = get_time();
    
    // Perform floating-point operations
    for (long long i = 0; i < operations; i++) {
        result = a * b + result;
        a = result * 0.999999;
        b = a + 1.000001;
    }
    
    double end_time = get_time();
    double elapsed = end_time - start_time;
    
    // Each loop iteration performs 4 floating-point operations:
    // 1 multiplication, 1 addition, 1 multiplication, 1 addition
    double total_flops = operations * 4.0;
    double mflops = (total_flops / elapsed) / 1000000.0;
    
    printf("Elapsed time: %.6f seconds\n", elapsed);
    printf("Total FLOPS: %.0f\n", total_flops);
    printf("MFLOPS: %.2f\n", mflops);
    printf("Result (to prevent optimization): %f\n", result);
    
    return 0;
}
