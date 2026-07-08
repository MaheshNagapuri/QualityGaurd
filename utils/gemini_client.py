# from __future__ import annotations

"""
Gemini LLM client initialization for CrewAI.

Handles Gemini API key management and LLM configuration for CrewAI agents.
Follows lang_demo project patterns with API key rotation support.
"""



# import logging
# import os
# import re
# from pathlib import Path
# from typing import Dict, Any, Optional

# logger = logging.getLogger(__name__)

# try:
#     from dotenv import load_dotenv

#     env_file = Path.cwd() / ".env"
#     if env_file.exists():
#         load_dotenv(env_file)
# except ImportError:
#     pass


# def get_all_api_keys() -> list:
#     """Return all available Gemini API keys for rotation.
#     Checks Streamlit secrets (GEMINI_API_KEY_1..4) then environment variables.
#     """
#     keys = []

#     try:
#         import streamlit as st

#         for i in range(1, 5):
#             try:
#                 key = st.secrets.get(f"GEMINI_API_KEY_{i}")
#                 if key:
#                     keys.append(key)
#             except Exception:
#                 pass
#     except ImportError:
#         pass

#     env_key = os.getenv("GEMINI_API_KEY")
#     if env_key and env_key not in keys:
#         keys.append(env_key)

#     for i in range(1, 5):
#         env_key_i = os.getenv(f"GEMINI_API_KEY_{i}")
#         if env_key_i and env_key_i not in keys:
#             keys.append(env_key_i)

#     return keys


# def get_first_api_key() -> Optional[str]:
#     """Return the first available Gemini API key."""
#     keys = get_all_api_keys()
#     return keys[0] if keys else None


# def initialize_gemini_llm():
#     """Initialize Gemini LLM for CrewAI using google-generativeai.

#     Returns:
#         LLM: Configured Gemini LLM instance

#     Raises:
#         ValueError: If API key is not found
#     """
#     try:
#         from crewai import LLM
#     except ImportError:
#         raise ImportError("CrewAI is not installed. Install with: pip install crewai")

#     api_key = get_first_api_key()
#     model_name = os.getenv("GEMINI_MODEL", "gemini/gemini-1.5-flash")

#     if not api_key:
#         raise ValueError(
#             "Gemini API key not found. Set GEMINI_API_KEY or GEMINI_API_KEY_1..4 in .env file"
#         )

#     # Use google-generativeai with CrewAI
#     llm = LLM(
#         model=model_name,
#         api_key=api_key,
#     )

#     logger.info(f"Gemini LLM initialized with model {model_name} via google-generativeai")
#     return llm


# if __name__ == "__main__":
#     llm = initialize_gemini_llm()
#     print("Gemini LLM initialized successfully")
# ---------------------------------------------------------------------------
# with switching gemini  keys
# from __future__ import annotations
# """
# Gemini LLM client initialization for CrewAI.

# Handles Gemini API key management and LLM configuration for CrewAI agents.
# Follows lang_demo project patterns with API key rotation support.
# """


# import logging
# import os
# from pathlib import Path
# from typing import Optional

# logger = logging.getLogger(__name__)

# try:
#     from dotenv import load_dotenv

#     env_file = Path.cwd() / ".env"
#     if env_file.exists():
#         load_dotenv(env_file)
# except ImportError:
#     pass

# # Global key rotation index
# _current_key_index = 0


# def get_all_api_keys() -> list:
#     """Return all available Gemini API keys for rotation.
#     Checks Streamlit secrets (GEMINI_API_KEY_1..4) then environment variables.
#     """
#     keys = []

#     try:
#         import streamlit as st

#         for i in range(1, 5):
#             try:
#                 key = st.secrets.get(f"GEMINI_API_KEY_{i}")
#                 if key:
#                     keys.append(key)
#             except Exception:
#                 pass
#     except ImportError:
#         pass

#     env_key = os.getenv("GEMINI_API_KEY")
#     if env_key and env_key not in keys:
#         keys.append(env_key)

#     for i in range(1, 5):
#         env_key_i = os.getenv(f"GEMINI_API_KEY_{i}")
#         if env_key_i and env_key_i not in keys:
#             keys.append(env_key_i)

#     return keys


# def get_first_api_key() -> Optional[str]:
#     """Return the first available Gemini API key."""
#     keys = get_all_api_keys()
#     return keys[0] if keys else None


# def get_next_api_key() -> Optional[str]:
#     """Return the next API key in rotation order.
#     Cycles through all available keys round-robin.
#     """
#     global _current_key_index
#     keys = get_all_api_keys()
#     if not keys:
#         return None
#     key = keys[_current_key_index % len(keys)]
#     _current_key_index = (_current_key_index + 1) % len(keys)
#     logger.info(f"Using API key #{(_current_key_index % len(keys)) + 1} of {len(keys)}")
#     return key


# def initialize_gemini_llm():
#     """Initialize Gemini LLM for CrewAI using google-generativeai.
#     Tries all available API keys, rotating on 429 errors.

#     Returns:
#         LLM: Configured Gemini LLM instance

#     Raises:
#         ValueError: If no API key works
#     """
#     try:
#         from crewai import LLM
#     except ImportError:
#         raise ImportError("CrewAI is not installed. Install with: pip install crewai")

#     keys = get_all_api_keys()
#     if not keys:
#         raise ValueError(
#             "No Gemini API keys found. Set GEMINI_API_KEY or GEMINI_API_KEY_1..4 in .env file"
#         )

#     model_name = os.getenv("GEMINI_MODEL", "gemini/gemini-1.5-flash")
#     last_error = None

#     for i, api_key in enumerate(keys):
#         try:
#             llm = LLM(
#                 model=model_name,
#                 api_key=api_key,
#             )
#             logger.info(f"Gemini LLM initialized with key #{i + 1} of {len(keys)}, model: {model_name}")
#             return llm

#         except Exception as e:
#             error_str = str(e)
#             if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
#                 logger.warning(f"Key #{i + 1} quota exhausted (429), trying next key...")
#                 last_error = e
#                 continue
#             else:
#                 # Non-quota error (bad key, network, etc) — still try next
#                 logger.warning(f"Key #{i + 1} failed with error: {error_str}, trying next key...")
#                 last_error = e
#                 continue

#     raise ValueError(
#         f"All {len(keys)} API keys failed or exhausted. "
#         f"Last error: {last_error}. "
#         f"Add more keys or wait until midnight Pacific for quota reset."
#     )


# def initialize_gemini_llm_with_fallback() -> tuple:
#     """Returns (llm, key_index) — useful for agents that need to retry with next key on 429."""
#     global _current_key_index
#     from crewai import LLM

#     keys = get_all_api_keys()
#     if not keys:
#         raise ValueError("No Gemini API keys found.")

#     model_name = os.getenv("GEMINI_MODEL", "gemini/gemini-1.5-flash")
#     idx = _current_key_index % len(keys)
#     api_key = keys[idx]
#     _current_key_index = (idx + 1) % len(keys)

#     llm = LLM(model=model_name, api_key=api_key)
#     logger.info(f"LLM initialized with key #{idx + 1} of {len(keys)}")
#     return llm, idx


# if __name__ == "__main__":
#     keys = get_all_api_keys()
#     print(f"Found {len(keys)} API key(s)")
#     llm = initialize_gemini_llm()
#     print("Gemini LLM initialized successfully")
# ------------------------------------------------------------------------------------------
# with gorq if not gemini
from __future__ import annotations

"""
LLM client initialization for CrewAI.
Supports Groq (primary) and Gemini (fallback) with API key rotation.
"""

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

# Global key rotation index for Gemini fallback
_current_key_index = 0

# Errors that mean Groq should be skipped and Gemini tried
GROQ_FATAL_ERRORS = [
    "invalid_api_key", "invalid api key", "unauthorized",
    "401", "403", "authentication", "api key"
]

# Errors that mean quota is hit — retry or rotate
QUOTA_ERRORS = [
    "429", "rate limit", "quota", "resource exhausted", "too many"
]


def _is_groq_fatal(error: str) -> bool:
    """Returns True if error means Groq key is invalid — should fall back to Gemini."""
    err = error.lower()
    return any(k in err for k in GROQ_FATAL_ERRORS)


def _is_quota_error(error: str) -> bool:
    """Returns True if error means quota exhausted."""
    err = error.lower()
    return any(k in err for k in QUOTA_ERRORS)


def get_all_gemini_keys() -> list:
    """Return all available Gemini API keys for rotation."""
    keys = []

    try:
        import streamlit as st
        for i in range(1, 5):
            try:
                key = st.secrets.get(f"GEMINI_API_KEY_{i}")
                if key:
                    keys.append(key)
            except Exception:
                pass
    except ImportError:
        pass

    env_key = os.getenv("GEMINI_API_KEY")
    if env_key and env_key not in keys:
        keys.append(env_key)

    for i in range(1, 5):
        env_key_i = os.getenv(f"GEMINI_API_KEY_{i}")
        if env_key_i and env_key_i not in keys:
            keys.append(env_key_i)

    return keys


def get_all_api_keys() -> list:
    """Alias for backward compatibility."""
    return get_all_gemini_keys()


def get_first_api_key() -> Optional[str]:
    """Return the first available Gemini API key."""
    keys = get_all_gemini_keys()
    return keys[0] if keys else None


def get_next_api_key() -> Optional[str]:
    """Return the next Gemini API key in rotation order."""
    global _current_key_index
    keys = get_all_gemini_keys()
    if not keys:
        return None
    key = keys[_current_key_index % len(keys)]
    _current_key_index = (_current_key_index + 1) % len(keys)
    return key


def _try_gemini_fallback() -> object:
    """Try all Gemini keys in rotation. Returns LLM or raises ValueError."""
    from crewai import LLM

    gemini_keys = get_all_gemini_keys()
    if not gemini_keys:
        raise ValueError(
            "No Gemini keys found. Set GEMINI_API_KEY_1..4 in .env as fallback."
        )

    gemini_model = os.getenv("GEMINI_MODEL", "gemini/gemini-flash-lite-latest")
    last_error = None

    for i, api_key in enumerate(gemini_keys):
        try:
            llm = LLM(model=gemini_model, api_key=api_key)
            logger.info(f"✅ Gemini fallback: key #{i + 1} of {len(gemini_keys)}, model: {gemini_model}")
            return llm
        except Exception as e:
            error_str = str(e)
            if _is_quota_error(error_str):
                logger.warning(f"Gemini key #{i + 1} quota exhausted, trying next...")
            else:
                logger.warning(f"Gemini key #{i + 1} failed: {error_str}, trying next...")
            last_error = e
            continue

    raise ValueError(
        f"All Gemini keys also failed. Last error: {last_error}. "
        "Wait until midnight Pacific for quota reset or add more keys."
    )


def initialize_gemini_llm() -> object:
    """Initialize LLM for CrewAI.

    Priority:
    1. Groq (if GROQ_API_KEY is set and valid)
    2. Gemini key rotation (fallback if Groq fails for any reason)

    Returns:
        LLM: Configured LLM instance

    Raises:
        ValueError: If no working API key found anywhere
    """
    try:
        from crewai import LLM
    except ImportError:
        raise ImportError("CrewAI is not installed. Install with: pip install crewai")

    # ── PRIMARY: Groq ──────────────────────────────────────────────
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        groq_model = os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile")
        # Enforce groq/ prefix — without it CrewAI's LLM router falls back to OpenAI
        # and sends the Groq key (gsk_...) to api.openai.com → 401.
        if not groq_model.startswith("groq/"):
            groq_model = f"groq/{groq_model}"
        try:
            llm = LLM(model=groq_model, api_key=groq_key)
            logger.info(f"✅ Groq LLM initialized: {groq_model}")
            return llm
        except Exception as e:
            error_str = str(e)
            if _is_groq_fatal(error_str):
                logger.warning(
                    f"⚠️ Groq key invalid/unauthorized: {error_str}\n"
                    f"→ Falling back to Gemini..."
                )
            elif _is_quota_error(error_str):
                logger.warning(
                    f"⚠️ Groq quota exhausted: {error_str}\n"
                    f"→ Falling back to Gemini..."
                )
            else:
                logger.warning(
                    f"⚠️ Groq failed ({error_str})\n"
                    f"→ Falling back to Gemini..."
                )
            # Always fall through to Gemini on any Groq error
            return _try_gemini_fallback()
    else:
        logger.info("No GROQ_API_KEY found — using Gemini directly.")

    # ── FALLBACK: Gemini key rotation ──────────────────────────────
    return _try_gemini_fallback()


def initialize_gemini_llm_with_fallback() -> tuple:
    """Returns (llm, key_index) for agents that need per-call retry."""
    global _current_key_index

    # Try Groq first
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        groq_model = os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile")
        if not groq_model.startswith("groq/"):
            groq_model = f"groq/{groq_model}"
        try:
            from crewai import LLM
            llm = LLM(model=groq_model, api_key=groq_key)
            logger.info(f"✅ Groq LLM initialized (with_fallback): {groq_model}")
            return llm, 0
        except Exception as e:
            logger.warning(f"⚠️ Groq failed in with_fallback: {e} → trying Gemini...")

    # Fallback to Gemini rotation
    from crewai import LLM
    keys = get_all_gemini_keys()
    if not keys:
        raise ValueError("No API keys found — set GROQ_API_KEY or GEMINI_API_KEY_1..4 in .env")

    gemini_model = os.getenv("GEMINI_MODEL", "gemini/gemini-1.5-flash")
    idx = _current_key_index % len(keys)
    api_key = keys[idx]
    _current_key_index = (idx + 1) % len(keys)

    llm = LLM(model=gemini_model, api_key=api_key)
    logger.info(f"✅ Gemini LLM initialized: key #{idx + 1} of {len(keys)}")
    return llm, idx


