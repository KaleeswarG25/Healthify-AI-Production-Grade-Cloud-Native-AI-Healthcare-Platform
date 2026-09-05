# ai-service/app/ai_engine.py
import requests
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.getenv("OLLAMA_MODEL", "llama2")
NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "4096"))
NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "256"))

def generate_ai_response(prompt: str, system_prompt: str = None) -> str:
    """
    Generate AI response using Ollama
    """
    try:
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": NUM_CTX,
                "num_predict": NUM_PREDICT,
            },
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        print(f"📤 Sending to Ollama with model: {MODEL}")
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        response.raise_for_status()
        
        data = response.json()
        return data.get("response", "Sorry, I couldn't generate a response.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Make sure it's running: 'ollama serve'")
        return "⚠️ AI service unavailable. Please ensure Ollama is running."
    except Exception as e:
        print(f"❌ AI Engine Error: {str(e)}")
        raise RuntimeError(f"Ollama generation failed: {str(e)}") from e

def analyze_medical_report(report_text: str) -> Dict[str, Any]:
    """
    Analyze medical report and extract key information
    """
    system_prompt = """You are a medical AI assistant. Analyze the medical report and provide:
    
    📊 KEY FINDINGS
    - Important values and observations
    
    ⚠️ ABNORMAL VALUES
    - Anything outside normal range
    
    📝 SUMMARY
    - Brief overview of the report
    
    💡 RECOMMENDATIONS
    - Any follow-up suggestions or what to discuss with doctor
    
    Be clear, concise, and use bullet points. Explain medical terms in simple language."""
    
    prompt = f"""Please analyze this medical report:

{report_text}

Provide your analysis in the format described above."""
    
    analysis = generate_ai_response(prompt, system_prompt)
    
    # Create a brief summary (first 200 chars)
    summary = analysis[:200] + "..." if len(analysis) > 200 else analysis
    
    return {
        "analysis": analysis,
        "summary": summary
    }

def answer_question(question: str, report_context: str, report_analysis: str) -> str:
    """
    Answer question based on report context and analysis
    """
    system_prompt = """You are a helpful medical AI assistant. 
Answer questions based on:
1. The patient's actual report (if relevant)
2. Your previous analysis of the report
3. General medical knowledge (if general question)

Guidelines:
- Be clear, concise, and structured.
- Use bullet points instead of long paragraphs.
- Explain medical terms simply.
- If unsure, say so and recommend consulting a doctor.
"""

    prompt = f"""PATIENT'S REPORT:
    {report_context}

    PREVIOUS ANALYSIS:
    {report_analysis}

    USER QUESTION:
    {question}

    Answer the question:
    - If it's about the report, refer directly to the report data.
    - If it's general, provide short, clear medical info.
    - Format the answer in bullet points, no greetings or filler text.
    """
    return generate_ai_response(prompt, system_prompt)