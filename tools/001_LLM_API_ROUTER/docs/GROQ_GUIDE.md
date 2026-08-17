# Groq Provider Guide

## Quick Start

The Groq provider is integrated into the LLM Router. Use it with:

```bash
python3 tools/001_LLM_API_ROUTER/llm_switch.py -p groq -m fast -msg "your prompt"
```

## Available Models

### 1. **llama-3.1-8b-instant** (Fast & Cheap)
- **Alias**: `fast`, `llama`, `llama-fast`, `llama-3.1`
- **Speed**: Ultra-fast (200-300ms)
- **Cost**: ~5 µUSD per 1k prompt tokens, 8 µUSD per 1k completion tokens
- **Best for**: Quick responses, low latency, cost-sensitive tasks

Example:
```bash
python3 tools/001_LLM_API_ROUTER/llm_switch.py -p groq -m fast -msg "What is 2+2?"
```

### 2. **openai/gpt-oss-120b** (Powerful + Automatic Caching)
- **Alias**: `120b`, `gpt-oss`, `gpt-oss-120b`, `powerful`
- **Speed**: Moderate (300-500ms)
- **Cost**: ~100 µUSD per 1k prompt tokens, 300 µUSD per 1k completion tokens
- **Features**: Automatic prompt caching (50% discount on cached tokens)
- **Best for**: Complex reasoning, detailed responses, repeated prompts

Example:
```bash
python3 tools/001_LLM_API_ROUTER/llm_switch.py -p groq -m 120b -msg "Explain quantum computing"
```

## Automatic Prompt Caching

The **openai/gpt-oss-120b** model automatically supports prompt caching. This means:

### How It Works

1. **First Request**: System processes your prompt normally
   - Caches the prefix of your prompt for 2 hours
   - You pay full price for prompt tokens

2. **Subsequent Requests** (within 2 hours with the same prefix):
   - Groq detects the matching prefix
   - Reuses cached computation
   - **You get 50% discount on cached tokens**
   - Much faster response times

### Example: Multi-Turn Conversation

```python
# First turn - full cost
prompt_1 = "You are a helpful AI assistant. What is quantum computing?"

# Second turn - cached prefix, 50% discount
prompt_2 = "You are a helpful AI assistant. What is quantum entanglement?"

# The system prompt and instructions are cached, so you save ~50% on prompt tokens
```

### Optimal Structure for Caching

To maximize cache hits, place **static content first**, then **dynamic content last**:

```
[SYSTEM PROMPT] ← Static (cached)
[INSTRUCTIONS] ← Static (cached)  
[EXAMPLES] ← Static (cached)
[USER QUERY] ← Dynamic (new processing)
```

### Tracking Cache Usage

Check the output metadata to see cache performance:

```json
{
  "usage": {
    "prompt_tokens": 4641,
    "cached_tokens": 4608,     ← Tokens served from cache
    "completion_tokens": 1817,
    "total_tokens": 6458
  }
}
```

**Cache Hit Rate = cached_tokens / prompt_tokens × 100%**

In this example: 4608 / 4641 = 99.3% cache hit!

## Usage Tips

### Cost Comparison
```
Fast model (llama):    $0.000003 per request (typical)
120B model (first):    $0.000262 per request
120B model (cached):   ~$0.000131 per request (50% off)
```

### When to Use Each Model

| Task | Model | Reason |
|------|-------|--------|
| Quick facts | `fast` | Ultra-low latency, minimal cost |
| Complex reasoning | `120b` | More powerful, better quality |
| Repeated questions | `120b` | Caching provides 50% discount |
| Real-time chat | `fast` | Best response time |
| Detailed analysis | `120b` | Superior reasoning capability |

## API Key Setup

Your `GROQ_API_KEY` is automatically loaded from the `.env` file:

```bash
# In .env
GROQ_API_KEY=your_api_key_here
```

Get your key: https://console.groq.com/keys

## Examples

### Simple Math
```bash
python3 tools/001_LLM_API_ROUTER/llm_switch.py -p groq -m fast -msg "What is the square root of 144?"
```

### Detailed Explanation with Caching
```bash
python3 tools/001_LLM_API_ROUTER/llm_switch.py -p groq -m 120b -msg "Explain AI in 100 words"
```

### With Streaming
```bash
python3 tools/001_LLM_API_ROUTER/llm_switch.py -p groq -m 120b -msg "Write a poem about AI" --stream
```

## Limitations & Notes

- **Temperature**: If set to 0, Groq converts it to 1e-8 (use 0.2 for deterministic results)
- **Cache Lifetime**: 2 hours of inactivity, then expires
- **Cache Matching**: Requires exact prefix match (even whitespace matters)
- **Rate Limits**: Cached tokens don't count toward rate limits

## References

- Groq API Docs: https://console.groq.com/docs/
- Prompt Caching Guide: https://console.groq.com/docs/prompt-caching
- Available Models: https://console.groq.com/docs/models
