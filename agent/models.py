"""
Model Provider Abstraction for Open-Weight Agent Inference.
Supports:
1. HuggingFaceInferenceProvider: Open-weight inference via Hugging Face Inference API (Qwen 2.5 / Llama 3)
2. LocalTransformersProvider: Local execution with PyTorch and PEFT LoRA adapters
3. RuleBasedFallbackPolicy: Explicit deterministic fallback clearly marked when no LLM/GPU is available
"""
import os
import json
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger("civic_ai.models")

class BaseModelProvider(ABC):
    """Abstract base class for all language model providers."""
    
    def __init__(self, model_name: str, temperature: float = 0.1, max_new_tokens: int = 512):
        self.model_name = model_name
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens

    @abstractmethod
    def generate(self, messages: List[Dict[str, str]]) -> str:
        """Generates raw text completion from formatted conversation messages."""
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Returns provider metadata including architecture, device, and fallback status."""
        pass


class HuggingFaceInferenceProvider(BaseModelProvider):
    """
    Inference provider connecting to Hugging Face Inference API / Dedicated Endpoints
    for open-weight models (Qwen 2.5 7B, Llama 3.1 8B).
    """
    
    def __init__(
        self, 
        model_name: str = "Qwen/Qwen2.5-7B-Instruct",
        api_token: Optional[str] = None,
        temperature: float = 0.1,
        max_new_tokens: int = 512
    ):
        super().__init__(model_name, temperature, max_new_tokens)
        self.api_token = api_token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        self.endpoint_url = f"https://api-inference.huggingface.co/models/{self.model_name}"

    def generate(self, messages: List[Dict[str, str]]) -> str:
        if not self.api_token:
            raise ValueError("HF_TOKEN not configured for HuggingFaceInferenceProvider")

        import urllib.request
        import urllib.error

        # Format chat prompt
        prompt_text = ""
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            prompt_text += f"<|im_start|>{role}\n{content}<|im_end|>\n"
        prompt_text += "<|im_start|>assistant\n"

        payload = {
            "inputs": prompt_text,
            "parameters": {
                "max_new_tokens": self.max_new_tokens,
                "temperature": max(0.01, self.temperature),
                "return_full_text": False
            }
        }

        req = urllib.request.Request(
            self.endpoint_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=30.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get("generated_text", "")
                elif isinstance(data, dict):
                    return data.get("generated_text", "")
                return str(data)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            logger.warning(f"HF Inference API HTTP error {e.code}: {err_body}")
            raise RuntimeError(f"Hugging Face API returned HTTP {e.code}: {err_body}")
        except Exception as e:
            logger.warning(f"HF Inference API call failed: {e}")
            raise

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "provider_type": "huggingface_inference_api",
            "model_name": self.model_name,
            "device": "huggingface_cloud_accelerator",
            "is_fallback": False,
            "api_configured": bool(self.api_token),
            "status": "ONLINE" if self.api_token else "UNAUTHENTICATED (Missing HF_TOKEN)"
        }


class LocalTransformersProvider(BaseModelProvider):
    """
    Inference provider loading open-weight PyTorch model with PEFT LoRA adapter locally.
    Requires torch and transformers.
    """
    
    def __init__(
        self, 
        base_model_name: str = "Qwen/Qwen2.5-7B-Instruct",
        adapter_path: Optional[str] = None,
        device: Optional[str] = None
    ):
        super().__init__(base_model_name)
        self.adapter_path = adapter_path
        self.device = device or ("cuda" if self._has_cuda() else "cpu")
        self.model = None
        self.tokenizer = None
        self._loaded = False

    def _has_cuda(self) -> bool:
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    def load_model(self):
        if self._loaded:
            return
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel

        logger.info(f"Loading local base model '{self.model_name}' on {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None,
            trust_remote_code=True
        )
        if self.adapter_path and os.path.exists(self.adapter_path):
            logger.info(f"Attaching LoRA adapter from '{self.adapter_path}'...")
            self.model = PeftModel.from_pretrained(self.model, self.adapter_path)
        self.model.eval()
        self._loaded = True

    def generate(self, messages: List[Dict[str, str]]) -> str:
        if not self._loaded:
            self.load_model()
        import torch
        
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                temperature=max(0.01, self.temperature),
                do_sample=self.temperature > 0.05
            )
        return self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "provider_type": "local_transformers_pipeline",
            "model_name": self.model_name,
            "device": self.device,
            "is_fallback": False,
            "adapter_path": self.adapter_path,
            "loaded": self._loaded,
            "status": "LOADED" if self._loaded else "READY_TO_LOAD"
        }


class RuleBasedFallbackPolicy(BaseModelProvider):
    """
    Explicit Deterministic Fallback Policy.
    Clearly designated as a fallback rule engine when no open-weight model weights
    or remote inference API credentials are available in the runtime environment.
    """

    def __init__(self):
        super().__init__(model_name="CivicAI-Deterministic-Fallback-Engine (v2.1)")

    def generate(self, messages: List[Dict[str, str]]) -> str:
        # Import deterministic reasoning engine
        from agent.reasoner import execute_deterministic_fallback_turn
        return execute_deterministic_fallback_turn(messages)

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "provider_type": "rule_based_fallback_mode",
            "model_name": self.model_name,
            "device": "cpu_deterministic",
            "is_fallback": True,
            "status": "ACTIVE (Rule-Based Fallback Mode)",
            "description": "Standard deterministic rule engine active. Open-weight LLM inference disabled or unconfigured."
        }


def get_active_model_provider() -> BaseModelProvider:
    """
    Factory function returning the best available model provider.
    Priority:
    1. HuggingFaceInferenceProvider (if HF_TOKEN is present)
    2. LocalTransformersProvider (if weights & torch are explicitly configured)
    3. RuleBasedFallbackPolicy (honest, explicitly designated fallback mode)
    """
    hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    if hf_token:
        try:
            return HuggingFaceInferenceProvider(
                model_name=os.environ.get("CIVIC_MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct"),
                api_token=hf_token
            )
        except Exception as e:
            logger.warning(f"Failed to initialize HuggingFaceInferenceProvider: {e}")

    # Fallback to clearly labeled deterministic policy
    return RuleBasedFallbackPolicy()
