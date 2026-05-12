import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any
import httpx

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    load_dotenv = None


class CacheStore:
    def __init__(self, cache_dir: str | None = None):
        self.cache_dir = Path(cache_dir or ".link2learn_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.cache_dir / "cache.json"
        self._load()

    def _load(self) -> None:
        if self.index_file.exists():
            try:
                with self.index_file.open("r", encoding="utf-8") as handle:
                    self.store = json.load(handle)
            except (ValueError, OSError):
                self.store = {}
        else:
            self.store = {}

    def _save(self) -> None:
        with self.index_file.open("w", encoding="utf-8") as handle:
            json.dump(self.store, handle, indent=2)

    def get(self, key: str) -> Any | None:
        return self.store.get(key)

    def set(self, key: str, value: Any) -> None:
        self.store[key] = value
        self._save()


class GroqClient:
    """Lightweight Groq API client with local prompt caching."""

    def __init__(
        self,
        api_key: str | None = None,
        endpoint: str | None = None,
        model: str | None = None,
        cache_dir: str | None = None,
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.endpoint = endpoint or os.getenv("GROQ_API_URL", "https://api.groq.com/v1")
        self.model = model or os.getenv("GROQ_MODEL", "groq-llm")
        self.cache = CacheStore(cache_dir)

    def _cache_key(self, prompt: str, max_tokens: int, temperature: float) -> str:
        digest = hashlib.sha256(f"{prompt}|{max_tokens}|{temperature}".encode("utf-8")).hexdigest()
        return digest

    def request(self, prompt: str, max_tokens: int = 512, temperature: float = 0.0) -> str:
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is required for Groq API calls")

        cache_key = self._cache_key(prompt, max_tokens, temperature)
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        url = f"{self.endpoint}/models/{self.model}/invoke"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "input": prompt,
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }

        for attempt in range(1, 5):
            try:
                response = httpx.post(url, headers=headers, json=payload, timeout=30)
            except httpx.HTTPError as exc:
                raise RuntimeError(f"Groq request failed: {exc}") from exc

            if response.status_code == 429:
                time.sleep(attempt * 2)
                continue
            if response.status_code >= 500:
                time.sleep(attempt * 1.5)
                continue

            if response.status_code != 200:
                raise RuntimeError(
                    f"Groq API returned {response.status_code}: {response.text}"
                )

            try:
                data = response.json()
            except json.JSONDecodeError:
                raise RuntimeError("Groq API returned invalid JSON")

            output = self._parse_output(data)
            self.cache.set(cache_key, output)
            return output

        raise RuntimeError("Groq API rate limit or service error after retries")

    def _parse_output(self, data: dict) -> str:
        if "output" in data and isinstance(data["output"], list):
            first = data["output"][0]
            if isinstance(first, dict):
                content = first.get("content")
                if isinstance(content, list) and content:
                    if isinstance(content[0], dict):
                        return content[0].get("text", json.dumps(content))
                    return str(content[0])
                return str(content)
            return str(first)

        if "choices" in data and isinstance(data["choices"], list):
            choice = data["choices"][0]
            if isinstance(choice, dict):
                return str(choice.get("text") or choice.get("message") or json.dumps(choice))

        return json.dumps(data)
