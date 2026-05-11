# CUDA Review Guidelines

## Memory Safety
- Always perform bounds checking: `if (idx < n)` before memory access
- Check for out-of-bounds global memory access
- Avoid stack overflow — keep local arrays small in kernels

## Error Handling
- Check ALL CUDA API calls: `cudaMalloc`, `cudaMemcpy`, `cudaFree`
- Check kernel launch errors with `cudaGetLastError()` after launch
- Call `cudaDeviceSynchronize()` before checking async errors

## Performance
- Ensure coalesced global memory access (threads access adjacent addresses)
- Avoid warp divergence (threads in a warp should follow the same branch)
- Use shared memory for frequently reused data
- Choose block size as a multiple of 32 (warp size)

## Synchronization
- Use `__syncthreads()` when threads in a block share data via shared memory
- Never assume execution order between blocks
- Avoid race conditions on global memory without atomics

## Resource Management
- Always free device memory: `cudaFree()`
- Verify device memory allocation succeeded before use
- Profile with `nvprof` or Nsight for occupancy analysis
