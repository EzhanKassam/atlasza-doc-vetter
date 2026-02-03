import json
import requests

class LLMError(Exception):
    pass

def chat_json(base_url: str, api_key: str, model: str, system: str, user: str) -> dict:
    if not api_key:
        raise LLMError("Missing LLM_API_KEY. Put it in a .env file.")

    url = base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.0,
        "response_format": {"type": "json_object"},
    }

    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
    if r.status_code >= 400:
        raise LLMError(f"LLM HTTP {r.status_code}: {r.text[:4000]}")

    data = r.json()
    try:
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        raise LLMError(f"Bad LLM response format: {e}")
