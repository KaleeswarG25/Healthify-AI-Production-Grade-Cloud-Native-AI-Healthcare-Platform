import os
from typing import Optional

import requests
from dotenv import load_dotenv


load_dotenv()


OLLAMA_URL = os.getenv("OLLAMA_URL")

if not OLLAMA_URL:
    raise RuntimeError("OLLAMA_URL environment variable is required")


MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

NUM_CTX = int(
    os.getenv("OLLAMA_NUM_CTX", "4096")
)

NUM_PREDICT = int(
    os.getenv("OLLAMA_NUM_PREDICT", "256")
)


DEFAULT_SYSTEM_PROMPT = """
You are an AI assistant for a health application.

Your job is to help users understand medical report information.

Important rules:
- Do not claim to diagnose a disease.
- Do not replace a doctor or qualified medical professional.
- Explain medical terminology in simple language.
- Clearly identify abnormal values when they are present.
- Do not invent medical values or facts that are not present in the report.
- If information is insufficient, say so.
- Encourage the user to consult a qualified healthcare professional for medical decisions.
"""


def generate_ai_response(
    prompt: str,
    system_prompt: Optional[str] = None,
) -> str:
    """
    Send a prompt to Ollama and return the generated response.
    """

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_ctx": NUM_CTX,
            "num_predict": NUM_PREDICT,
        },
    }

    payload["system"] = (
        system_prompt
        if system_prompt
        else DEFAULT_SYSTEM_PROMPT
    )

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=300,
        )

        response.raise_for_status()

        data = response.json()

        result = data.get("response")

        if not result:
            raise RuntimeError(
                "Ollama returned an empty response"
            )

        return result.strip()

    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            "Ollama request timed out"
        ) from exc

    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            "Unable to connect to Ollama"
        ) from exc

    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(
            f"Ollama returned HTTP {response.status_code}"
        ) from exc

    except ValueError as exc:
        raise RuntimeError(
            "Invalid response received from Ollama"
        ) from exc


def analyze_medical_report(report_text: str) -> dict:
    """
    Analyze medical report text using Ollama.
    """

    if not report_text or not report_text.strip():
        raise ValueError(
            "Medical report text cannot be empty"
        )

    prompt = f"""
Analyze the following medical report.

Provide:

1. A simple summary.
2. Important findings.
3. Abnormal values or observations.
4. What each important finding generally means.
5. Questions the patient may want to ask their doctor.

Medical report:

{report_text}
"""

    analysis = generate_ai_response(prompt)

    summary_prompt = f"""
Create a short, easy-to-understand summary of this
medical report analysis.

Analysis:

{analysis}
"""

    summary = generate_ai_response(summary_prompt)

    return {
        "analysis": analysis,
        "summary": summary,
    }


def answer_question(
    question: str,
    report_context: str,
    report_analysis: str,
) -> str:
    """
    Answer a question using the medical report
    and its previous analysis as context.
    """

    if not question.strip():
        raise ValueError("Question cannot be empty")

    prompt = f"""
Answer the user's question using ONLY the provided
medical report and analysis as context.

Medical report:
{report_context}

Previous analysis:
{report_analysis}

User question:
{question}

Explain the answer clearly and avoid making a diagnosis.
"""

    return generate_ai_response(prompt) 