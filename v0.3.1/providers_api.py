"""Model adapters for protocol 0.3.1. Standard library only. Keys come from environment variables and are never logged."""
import json
import os
import re
import urllib.error
import urllib.request


class ProviderError(RuntimeError):
    pass


def _post(url, headers, body, timeout):
    request = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as err:
        detail = err.read().decode(errors="replace")[:500]
        raise ProviderError("HTTP %s: %s" % (err.code, detail))
    except (urllib.error.URLError, TimeoutError, OSError) as err:
        raise ProviderError(str(err))


def _get(url, timeout):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as err:
        raise ProviderError("HTTP %s: %s" % (err.code, err.read().decode(errors="replace")[:300]))
    except (urllib.error.URLError, TimeoutError, OSError) as err:
        raise ProviderError(str(err))


def extract_json(text):
    """Return the first JSON object in text, tolerating code fences. Raises ValueError otherwise."""
    if text is None:
        raise ValueError("empty response")
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        value = json.loads(cleaned)
    except ValueError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("no JSON object")
        value = json.loads(cleaned[start:end + 1])
    if not isinstance(value, dict):
        raise ValueError("JSON object required")
    return value


class Anthropic:
    paid = True

    def __init__(self, name, cfg, timeout=180):
        self.name, self.cfg, self.timeout = name, cfg, timeout
        self.key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.key:
            raise ProviderError("ANTHROPIC_API_KEY is not set")

    def generate(self, prompt, seed):
        body = {"model": self.cfg["model"], "max_tokens": self.cfg["max_tokens"],
                "output_config": {"effort": self.cfg["effort"]},
                "messages": [{"role": "user", "content": prompt}]}
        headers = {"x-api-key": self.key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
        data = _post("https://api.anthropic.com/v1/messages", headers, body, self.timeout)
        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
        usage = data.get("usage", {})
        return {"text": text, "input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens"),
                "returned_model": data.get("model"), "stop_reason": data.get("stop_reason")}


class OpenAI:
    paid = True

    def __init__(self, name, cfg, timeout=180):
        self.name, self.cfg, self.timeout = name, cfg, timeout
        self.key = os.environ.get("OPENAI_API_KEY")
        if not self.key:
            raise ProviderError("OPENAI_API_KEY is not set")

    def generate(self, prompt, seed):
        body = {"model": self.cfg["model"], "input": prompt, "reasoning": {"effort": self.cfg["effort"]},
                "max_output_tokens": self.cfg["max_tokens"]}
        headers = {"Authorization": "Bearer " + self.key, "content-type": "application/json"}
        data = _post("https://api.openai.com/v1/responses", headers, body, self.timeout)
        text = data.get("output_text")
        if text is None:
            parts = []
            for item in data.get("output", []):
                for c in item.get("content", []) or []:
                    if c.get("type") == "output_text":
                        parts.append(c.get("text", ""))
            text = "".join(parts)
        usage = data.get("usage", {})
        return {"text": text, "input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens"),
                "returned_model": data.get("model"), "stop_reason": data.get("status")}


class Ollama:
    """Local reference arm with the exact 0.2 generation settings."""
    paid = False

    def __init__(self, name, cfg, timeout=180):
        self.name, self.cfg, self.timeout = name, cfg, timeout
        self.host = cfg.get("host", "http://127.0.0.1:11434")
        self.check_ready()

    def check_ready(self):
        """v0.4 fix: refuse to start unless the exact model (and pinned digest, if configured) is installed."""
        try:
            tags = _get(self.host + "/api/tags", 10)
        except ProviderError as err:
            raise ProviderError("ollama not reachable at %s: %s" % (self.host, err))
        found = {m.get("name"): m.get("digest") for m in tags.get("models", [])}
        if self.cfg["model"] not in found:
            raise ProviderError("ollama model %s not installed at %s" % (self.cfg["model"], self.host))
        want = self.cfg.get("digest")
        if want and found[self.cfg["model"]] != want:
            raise ProviderError("ollama model %s digest %s != pinned %s" % (self.cfg["model"], found[self.cfg["model"]], want))
        self.digest = found[self.cfg["model"]]

    def generate(self, prompt, seed):
        body = {"model": self.cfg["model"], "prompt": prompt, "stream": False, "format": "json",
                "options": {"temperature": 0.6, "top_k": 16, "num_predict": 192, "seed": seed}}
        data = _post(self.host + "/api/generate", {"content-type": "application/json"}, body, self.timeout)
        return {"text": data.get("response"), "input_tokens": data.get("prompt_eval_count"),
                "output_tokens": data.get("eval_count"), "returned_model": data.get("model"), "stop_reason": data.get("done_reason")}


ADAPTERS = {"anthropic": Anthropic, "openai": OpenAI, "ollama": Ollama}


def build(name, cfg):
    return ADAPTERS[cfg["provider"]](name, cfg)


# ---- Subscription transport on Robin's Mac, mirroring 05_tools/background_reviews_20261103/native_runner.py ----
import subprocess
import tempfile

import glob
import time

# v0.4 fix: no absolute local paths in code. Set these in local.env (git-ignored; see local.env.example).
CODEX = os.environ.get("HONEST_AGENT_CODEX_BIN", "codex")
CLAUDE = os.environ.get("HONEST_AGENT_CLAUDE_BIN", "claude")
CODEX_HOME = os.environ.get("CODEX_HOME", os.path.expanduser("~/.codex"))
SYSTEM = "Answer the request exactly as instructed. Output only what is asked."


def clean_env():
    env = os.environ.copy()
    for k in list(env):
        if any(x in k for x in ("API_KEY", "ACCESS_TOKEN", "AUTH_TOKEN")) or k in ("OPENAI_BASE_URL", "ANTHROPIC_BASE_URL", "CLAUDE_CODE_OAUTH_TOKEN"):
            env.pop(k, None)
    env["PATH"] = "/opt/homebrew/bin:/usr/bin:/bin"
    return env


class ClaudeCLI:
    """claude -p with tools disabled and the default system prompt replaced. Subscription sign-in only."""
    paid = True  # tracked at API-equivalent price against the cap

    def __init__(self, name, cfg, timeout=420):
        self.name, self.cfg, self.timeout, self.env = name, cfg, timeout, clean_env()
        status = json.loads(subprocess.check_output([CLAUDE, "auth", "status"], env=self.env, text=True, timeout=30))
        if not status.get("loggedIn") or status.get("authMethod") != "claude.ai":
            raise ProviderError("Claude subscription login required")

    def generate(self, prompt, seed):
        cmd = [CLAUDE, "-p", "--safe-mode", "--restricted", "--strict-mcp-config", "--tools", "", "--disable-slash-commands",
               "--no-chrome", "--output-format", "json", "--model", self.cfg["model"], "--effort", self.cfg["effort"],
               "--system-prompt", SYSTEM]
        with tempfile.TemporaryDirectory() as d:
            p = subprocess.run(cmd, input=prompt, text=True, capture_output=True, env=self.env, cwd=d, timeout=self.timeout)
        if p.returncode:
            raise ProviderError("claude exit %d: %s" % (p.returncode, p.stderr[-300:]))
        data = json.loads(p.stdout)
        if data.get("is_error") or data.get("num_turns", 1) != 1:
            raise ProviderError("claude error or unexpected turns")
        usage = data.get("usage", {}) or {}
        tin = (usage.get("input_tokens") or 0) + (usage.get("cache_read_input_tokens") or 0) + (usage.get("cache_creation_input_tokens") or 0)
        return {"text": data.get("result", ""), "input_tokens": tin, "output_tokens": usage.get("output_tokens"),
                "returned_model": ",".join(data.get("modelUsage", {}) or []) or None, "stop_reason": data.get("subtype")}


class CodexCLI:
    """codex exec, read-only sandbox, shell and web disabled, no user config. ChatGPT subscription sign-in only."""
    paid = True

    def __init__(self, name, cfg, timeout=420):
        self.name, self.cfg, self.timeout, self.env = name, cfg, timeout, clean_env()
        a = subprocess.run([CODEX, "login", "status"], env=self.env, capture_output=True, text=True, timeout=30)
        if a.returncode or "ChatGPT" not in a.stdout + a.stderr:
            raise ProviderError("ChatGPT subscription login required")

    def generate(self, prompt, seed):
        started = time.time()
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "response.md")
            cmd = [CODEX, "--no-daemon", "exec", "--ignore-user-config", "--skip-git-repo-check", "--json",
                   "-m", self.cfg["model"], "-c", 'model_reasoning_effort="%s"' % self.cfg["effort"], "-c", 'sandbox_mode="read-only"',
                   "-c", "features.shell_tool=false", "-c", 'web_search="disabled"', "-c", "project_doc_max_bytes=0",
                   "-c", "developer_instructions=" + json.dumps(SYSTEM), "-o", out, "-"]
            p = subprocess.run(cmd, input=prompt, text=True, capture_output=True, env=self.env, cwd=d, timeout=self.timeout)
            events = [json.loads(x) for x in p.stdout.splitlines() if x.strip().startswith("{")]
            text = open(out).read() if os.path.exists(out) else ""
        if p.returncode or any(e.get("type") in ("error", "turn.failed") for e in events):
            raise ProviderError("codex failed: %s" % p.stderr[-300:])
        if any(isinstance(e.get("item"), dict) and e["item"].get("type") not in ("agent_message", "reasoning") for e in events):
            raise ProviderError("unexpected tool activity")
        usage = next((e.get("usage") for e in events if e.get("type") == "turn.completed"), None) or {}
        tout = usage.get("output_tokens")
        if tout is not None and usage.get("reasoning_output_tokens"):
            tout += usage["reasoning_output_tokens"]
        # v0.4 fix: report the model Codex actually ran (its own session log), never the config value.
        # None means unverified; the caller records it as such.
        model, effort = codex_session_model(d, started)
        return {"text": text, "input_tokens": usage.get("input_tokens"), "output_tokens": tout,
                "returned_model": model, "returned_effort": effort, "stop_reason": "completed"}


def codex_session_model(cwd, since, home=None):
    """Find the Codex session log written for a `codex exec` run in `cwd` (a unique temp dir) and return
    (model, effort) from its first turn_context, or (None, None) if no matching log exists."""
    home = home or CODEX_HOME
    want = os.path.realpath(cwd)
    days = {time.strftime("%Y/%m/%d", time.localtime(t)) for t in (since - 86400, since, time.time())}
    for day in sorted(days):
        for f in glob.glob(os.path.join(home, "sessions", day, "rollout-*.jsonl")):
            try:
                if os.path.getmtime(f) < since - 5:
                    continue
                meta = tc = None
                with open(f) as fh:
                    for line in fh:
                        e = json.loads(line)
                        if e.get("type") == "session_meta":
                            meta = e.get("payload", {})
                            if os.path.realpath(meta.get("cwd") or "") != want:
                                break
                        elif e.get("type") == "turn_context" and meta is not None:
                            tc = e.get("payload", {})
                            return tc.get("model"), tc.get("effort")
            except (OSError, ValueError):
                continue
    return None, None


ADAPTERS.update({"claude_cli": ClaudeCLI, "codex_cli": CodexCLI})
