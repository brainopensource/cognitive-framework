*`gemini-3.5-flash-lite`*, *`gemini-3.1-flash-lite`*, *`gemini-3.1-flash-live-preview`*, *`gemini-3-flash-preview`*, *`gemini-2.5-flash`*, *`gemini-2.5-flash-lite`*, *`gemini-2.5-flash-lite-preview-09-2025`*, *`gemini-3.6-flash`*




curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent" \
  -H 'Content-Type: application/json' \
  -H 'X-goog-api-key: \
  -X POST \
  -d '{
    "contents": [
      {
        "parts": [
          {
            "text": "Explain how AI works in a few words"
          }
        ]
      }
    ]
  }'



python3 -c '
import urllib.request
import json

url = "https://generativelanguage.googleapis.com/v1beta/models"
try:
    with urllib.request.urlopen(url) as response:
        result = json.loads(response.read().decode("utf-8"))
        for m in result.get("models", []):
            if "generateContent" in m.get("supportedGenerationMethods", []):
                print(m["name"], m.get("displayName"))
except Exception as e:
    print(e)
'

models/gemini-2.5-flash Gemini 2.5 Flash
models/gemini-2.5-pro Gemini 2.5 Pro
models/gemini-2.5-flash-preview-tts Gemini 2.5 Flash Preview TTS
models/gemini-2.5-pro-preview-tts Gemini 2.5 Pro Preview TTS
models/gemma-4-26b-a4b-it Gemma 4 26B A4B IT
models/gemma-4-31b-it Gemma 4 31B IT
models/gemini-flash-latest Gemini Flash Latest
models/gemini-flash-lite-latest Gemini Flash-Lite Latest
models/gemini-pro-latest Gemini Pro Latest
models/gemini-2.5-flash-lite Gemini 2.5 Flash-Lite
models/gemini-2.5-flash-image Nano Banana
models/gemini-3-flash-preview Gemini 3 Flash Preview
models/gemini-3.1-pro-preview Gemini 3.1 Pro Preview
models/gemini-3.1-pro-preview-customtools Gemini 3.1 Pro Preview Custom Tools
models/gemini-3.1-flash-lite-preview Gemini 3.1 Flash Lite Preview
models/gemini-3.1-flash-lite Gemini 3.1 Flash Lite
models/gemini-3-pro-image-preview Nano Banana Pro
models/gemini-3-pro-image Nano Banana Pro
models/nano-banana-pro-preview Nano Banana Pro
models/gemini-3.1-flash-image-preview Nano Banana 2
models/gemini-3.1-flash-image Nano Banana 2
models/gemini-3.1-flash-lite-image Nano Banana 2 Lite
models/gemini-3.5-flash Gemini 3.5 Flash
models/gemini-3.5-flash-lite Gemini 3.5 Flash Lite
models/gemini-omni-flash-preview Gemini Omni Flash Preview
models/gemini-3.6-flash Gemini 3.6 Flash
models/gemini-3.7-flash Gemini 3.7 Flash
models/lyria-3-clip-preview Lyria 3 Clip Preview
models/lyria-3-pro-preview Lyria 3 Pro Preview
models/gemini-3.1-flash-tts-preview Gemini 3.1 Flash TTS Preview
models/gemini-robotics-er-1.6-preview Gemini Robotics-ER 1.6 Preview
models/gemini-robotics-er-2-preview Gemini Robotics-ER 2 Preview
models/gemini-2.5-computer-use-preview-10-2025 Gemini 2.5 Computer Use Preview 10-2025
models/antigravity-preview-05-2026 Antigravity Agent Preview
models/deep-research-max-preview-04-2026 Deep Research Max Preview (Apr-21-2026)
models/deep-research-preview-04-2026 Deep Research Preview (Apr-21-2026)
models/deep-research-pro-preview-12-2025 Deep Research Pro Preview (Dec-12-2025)

