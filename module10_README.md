# Module 10: Introduction to Hugging Face Transformers

This module introduces you to Hugging Face's ecosystem and demonstrates how to run language models locally on your own machine.

## What You'll Learn

- Understanding Hugging Face's ecosystem
- Setting up the environment for local models
- Loading your first model
- Basic inference with local models
- Creating a simple interface for interacting with local models
- Comparing local models with API-based models

## Prerequisites

Before running this module, make sure you have the following installed:

```bash
pip install torch transformers gradio accelerate
```

For better performance with quantized models:

```bash
pip install bitsandbytes
```

## Hardware Requirements

Running language models locally requires significant computational resources:

- **CPU**: Any modern multi-core CPU will work, but inference will be slow
- **GPU**: NVIDIA GPU with CUDA support strongly recommended
- **RAM**: 8GB+ for small models, 16GB+ for medium models
- **VRAM**: 4GB+ for quantized models, 8GB+ for medium models, 24GB+ for large models
- **Disk Space**: At least 5GB free space for model downloads

## Model Size Categories

- **Small**: 125M-1B parameters (e.g., DistilGPT2, TinyLlama)
- **Medium**: 1B-7B parameters (e.g., Phi-2, Gemma-2B)
- **Large**: 7B+ parameters (e.g., Llama-2-7B, Mistral-7B)
- **XL**: 13B+ parameters (e.g., Llama-2-13B)
- **XXL**: 70B+ parameters (e.g., Llama-2-70B)

## Running the Module

To run this module:

```bash
python module10.py
```

This will:
1. Display information about Hugging Face's ecosystem
2. Provide guidance on setting up your environment
3. Compare local models vs. API-based models
4. Ask if you want to load a model and start the demo interface

## Using the Gradio Interface

If you choose to load a model, a Gradio interface will be launched with two tabs:

1. **Model Selection**: Choose and load a model
2. **Chat**: Interact with the loaded model

## Troubleshooting

### Common Issues

1. **Out of Memory Errors**:
   - Try a smaller model
   - Enable 4-bit quantization
   - Close other applications using GPU memory

2. **Slow Model Loading**:
   - Models are downloaded the first time you use them
   - Subsequent runs will be faster as models are cached

3. **CUDA Not Available**:
   - Make sure you have an NVIDIA GPU
   - Install the correct CUDA version for your PyTorch installation

4. **Model Not Found**:
   - Check your internet connection
   - Verify the model name is correct
   - Some models require accepting terms on the Hugging Face website

## Next Steps

After completing this module, you can:

1. Experiment with different models from the Hugging Face Hub
2. Try fine-tuning a model on your own data
3. Explore more advanced inference parameters
4. Integrate local models into your applications

## Resources

- [Hugging Face Documentation](https://huggingface.co/docs)
- [Transformers Documentation](https://huggingface.co/docs/transformers/index)
- [Model Hub](https://huggingface.co/models)
- [Hugging Face Course](https://huggingface.co/course/chapter1/1)
