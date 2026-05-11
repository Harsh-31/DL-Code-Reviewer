// sample.cu — vector addition kernel with intentional issues for review testing

#include <stdio.h>

// BUG 1: No bounds check — out-of-bounds memory access when n % blockDim.x != 0
// BUG 2: No CUDA error checking on malloc, memcpy, or kernel launch
// BUG 3: No cudaDeviceSynchronize before reading result
// BUG 4: d_a, d_b, d_c never freed — memory leak

__global__ void vectorAdd(float* a, float* b, float* c, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    c[idx] = a[idx] + b[idx];  // missing: if (idx < n)
}

int main() {
    int n = 1000;
    size_t size = n * sizeof(float);

    float *h_a = (float*)malloc(size);
    float *h_b = (float*)malloc(size);
    float *h_c = (float*)malloc(size);

    for (int i = 0; i < n; i++) { h_a[i] = i; h_b[i] = i * 2; }

    float *d_a, *d_b, *d_c;
    cudaMalloc(&d_a, size);  // no error check
    cudaMalloc(&d_b, size);
    cudaMalloc(&d_c, size);

    cudaMemcpy(d_a, h_a, size, cudaMemcpyHostToDevice);
    cudaMemcpy(d_b, h_b, size, cudaMemcpyHostToDevice);

    vectorAdd<<<4, 256>>>(d_a, d_b, d_c, n);  // 4*256=1024 > 1000, no bounds check

    cudaMemcpy(h_c, d_c, size, cudaMemcpyDeviceToHost);  // no sync before this

    printf("c[0] = %f\n", h_c[0]);

    free(h_a); free(h_b); free(h_c);
    // missing: cudaFree(d_a), cudaFree(d_b), cudaFree(d_c)
    return 0;
}
