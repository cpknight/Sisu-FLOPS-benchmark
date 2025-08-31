#define CL_TARGET_OPENCL_VERSION 120
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <CL/cl.h>

double get_time() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec + tv.tv_usec / 1000000.0;
}

const char *kernel_source = 
"__kernel void flops_kernel(__global float* results, const int operations_per_work_item) {\n"
"    int gid = get_global_id(0);\n"
"    float a = 1.23456f + gid * 0.001f;\n"
"    float b = 9.87654f + gid * 0.001f;\n"
"    float result = 0.0f;\n"
"    \n"
"    for (int i = 0; i < operations_per_work_item; i++) {\n"
"        result = fma(a, b, result);  // fused multiply-add\n"
"        a = result * 0.999999f;\n"
"        b = a + 1.000001f;\n"
"    }\n"
"    \n"
"    results[gid] = result;\n"
"}\n";

int main() {
    cl_platform_id platform;
    cl_device_id device;
    cl_context context;
    cl_command_queue queue;
    cl_program program;
    cl_kernel kernel;
    cl_mem buffer;
    cl_int err;
    
    // Get platform
    err = clGetPlatformIDs(1, &platform, NULL);
    if (err != CL_SUCCESS) {
        printf("Error getting OpenCL platform: %d\n", err);
        return 1;
    }
    
    // Get device (prefer GPU, fallback to CPU)
    err = clGetDeviceIDs(platform, CL_DEVICE_TYPE_GPU, 1, &device, NULL);
    if (err != CL_SUCCESS) {
        printf("No GPU found, trying CPU...\n");
        err = clGetDeviceIDs(platform, CL_DEVICE_TYPE_CPU, 1, &device, NULL);
        if (err != CL_SUCCESS) {
            printf("No OpenCL device found: %d\n", err);
            return 1;
        }
    }
    
    // Get device info
    char device_name[256];
    size_t max_work_group_size;
    cl_uint compute_units;
    
    clGetDeviceInfo(device, CL_DEVICE_NAME, sizeof(device_name), device_name, NULL);
    clGetDeviceInfo(device, CL_DEVICE_MAX_WORK_GROUP_SIZE, sizeof(max_work_group_size), &max_work_group_size, NULL);
    clGetDeviceInfo(device, CL_DEVICE_MAX_COMPUTE_UNITS, sizeof(compute_units), &compute_units, NULL);
    
    printf("=== GPU/OpenCL Benchmark ===\n");
    printf("Device: %s\n", device_name);
    printf("Compute Units: %u\n", compute_units);
    printf("Max Work Group Size: %zu\n\n", max_work_group_size);
    
    // Create context and command queue
    context = clCreateContext(NULL, 1, &device, NULL, NULL, &err);
    if (err != CL_SUCCESS) {
        printf("Error creating context: %d\n", err);
        return 1;
    }
    
    queue = clCreateCommandQueue(context, device, 0, &err);
    if (err != CL_SUCCESS) {
        printf("Error creating command queue: %d\n", err);
        return 1;
    }
    
    // Create and build program
    program = clCreateProgramWithSource(context, 1, &kernel_source, NULL, &err);
    if (err != CL_SUCCESS) {
        printf("Error creating program: %d\n", err);
        return 1;
    }
    
    err = clBuildProgram(program, 1, &device, "-cl-fast-relaxed-math", NULL, NULL);
    if (err != CL_SUCCESS) {
        printf("Error building program: %d\n", err);
        
        // Get build log
        size_t log_size;
        clGetProgramBuildInfo(program, device, CL_PROGRAM_BUILD_LOG, 0, NULL, &log_size);
        char *log = malloc(log_size);
        clGetProgramBuildInfo(program, device, CL_PROGRAM_BUILD_LOG, log_size, log, NULL);
        printf("Build log: %s\n", log);
        free(log);
        return 1;
    }
    
    // Create kernel
    kernel = clCreateKernel(program, "flops_kernel", &err);
    if (err != CL_SUCCESS) {
        printf("Error creating kernel: %d\n", err);
        return 1;
    }
    
    // Set up benchmark parameters
    size_t global_work_size = compute_units * 256; // 256 work items per compute unit
    int operations_per_work_item = 1000000; // 1M operations per work item
    
    printf("Global work size: %zu\n", global_work_size);
    printf("Operations per work item: %d\n", operations_per_work_item);
    
    // Create buffer for results
    buffer = clCreateBuffer(context, CL_MEM_WRITE_ONLY, sizeof(float) * global_work_size, NULL, &err);
    if (err != CL_SUCCESS) {
        printf("Error creating buffer: %d\n", err);
        return 1;
    }
    
    // Set kernel arguments
    clSetKernelArg(kernel, 0, sizeof(cl_mem), &buffer);
    clSetKernelArg(kernel, 1, sizeof(int), &operations_per_work_item);
    
    // Run benchmark
    printf("Running GPU benchmark...\n");
    
    double start_time = get_time();
    
    err = clEnqueueNDRangeKernel(queue, kernel, 1, NULL, &global_work_size, NULL, 0, NULL, NULL);
    if (err != CL_SUCCESS) {
        printf("Error executing kernel: %d\n", err);
        return 1;
    }
    
    clFinish(queue); // Wait for completion
    
    double end_time = get_time();
    double elapsed = end_time - start_time;
    
    // Calculate performance
    long long total_operations = (long long)global_work_size * operations_per_work_item;
    double total_flops = total_operations * 4.0; // 4 FP ops per iteration (FMA + mul + add)
    double mflops = (total_flops / elapsed) / 1000000.0;
    
    printf("Elapsed time: %.6f seconds\n", elapsed);
    printf("Total operations: %lld\n", total_operations);
    printf("Total FLOPS: %.0f\n", total_flops);
    printf("GPU MFLOPS: %.2f (%.2f GFLOPS)\n", mflops, mflops / 1000.0);
    
    // Cleanup
    clReleaseMemObject(buffer);
    clReleaseKernel(kernel);
    clReleaseProgram(program);
    clReleaseCommandQueue(queue);
    clReleaseContext(context);
    
    return 0;
}
