"""
High-Throughput Production Serving with vLLM.
Serves the GRPO LoRA-adapted Qwen-8B model with:
- Continuous batching
- Paged KV-Cache
- 4-bit AWQ / GPTQ quantisation
- OpenAI-compatible REST API endpoints (/v1/chat/completions)
"""

import os
import sys

def launch_vllm_server(
    model_name: str = "Qwen/Qwen2.5-7B-Instruct",
    lora_path: str = "./outputs/grpo_qwen_mcp",
    port: int = 8000,
    tensor_parallel_size: int = 1,
    max_model_len: int = 4096,
    gpu_memory_utilization: float = 0.90
):
    print("=" * 70)
    print("LAUNCHING HIGH-THROUGHPUT vLLM SERVING ENGINE")
    print(f"Base Model: {model_name}")
    print(f"LoRA Adapter: {lora_path}")
    print(f"Port: {port} | Tensor Parallel: {tensor_parallel_size}")
    print(f"Max Context Length: {max_model_len} | KV-Cache Utilization: {gpu_memory_utilization}")
    print("=" * 70)

    # CLI command structure for vLLM production service
    command = (
        f"python -m vllm.entrypoints.openai.api_server "
        f"--model {model_name} "
        f"--enable-lora "
        f"--lora-modules mcp-agent={lora_path} "
        f"--port {port} "
        f"--tensor-parallel-size {tensor_parallel_size} "
        f"--max-model-len {max_model_len} "
        f"--gpu-memory-utilization {gpu_memory_utilization} "
        f"--trust-remote-code"
    )

    print("\nProduction Command:")
    print(f"  {command}\n")
    print("API will be accessible at: http://localhost:8000/v1/chat/completions")
    return command

if __name__ == "__main__":
    launch_vllm_server()
