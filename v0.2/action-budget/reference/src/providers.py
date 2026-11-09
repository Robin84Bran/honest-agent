"""Only local inference. Ollama accepts an installed non-cloud model by digest lookup."""
import http.client
import json
import subprocess


def ollama(path, payload=None):
    conn = http.client.HTTPConnection("127.0.0.1", 11434, timeout=120)
    try:
        conn.request("GET" if payload is None else "POST", path,
                     body=None if payload is None else json.dumps(payload),
                     headers={"Content-Type": "application/json"})
        response = conn.getresponse()
        data = json.load(response)
        if response.status != 200:
            raise ValueError(str(data))
        return data
    finally:
        conn.close()


class Provider:
    def __init__(self, args):
        self.args = args
        self.identity = "Apple SystemLanguageModel.default (OS-managed)"
        if args.provider == "ollama":
            if not args.model or "cloud" in args.model.lower():
                raise ValueError("Select an installed local model")
            info = ollama("/api/show", {"model": args.model})
            if info.get("remote_model") or info.get("remote_host") or not info.get("model_info"):
                raise ValueError("Local model weights required")
            self.identity = next(m["digest"] for m in ollama("/api/tags")["models"]
                                 if m["name"] == args.model)

    def generate(self, prompt, seed):
        if self.args.provider == "apple":
            p = subprocess.run([self.args.apple_binary, str(seed)], input=prompt, text=True,
                               capture_output=True, timeout=120)
            if p.returncode:
                raise RuntimeError(p.stderr[:1500])
            return p.stdout, None, None
        data = ollama("/api/generate", {"model": self.args.model, "prompt": prompt,
                      "format": "json", "stream": False, "options": {"temperature": 0.6,
                      "top_k": 16, "num_predict": 192, "seed": seed}})
        return data["response"], data.get("prompt_eval_count"), data.get("eval_count")
