"""Throwaway server for taking deck screenshots: the real backend (mock LLM, freshly seeded) + the built frontend on one origin."""
import os

os.environ["LLM_PROVIDER"] = "mock"  # deterministic, no external calls

from fastapi.staticfiles import StaticFiles  # noqa: E402

from app.main import app  # noqa: E402

app.mount("/", StaticFiles(directory=r"C:\Golu\newSkills\GenAIKata\insurendclaim\frontend\dist", html=True), name="ui")
