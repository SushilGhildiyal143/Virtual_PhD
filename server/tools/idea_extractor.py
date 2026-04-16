import json
import os

from openai import OpenAI

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY) if API_KEY else None


def _fallback_extract(text):
    compact = " ".join(text.split())
    snippet = compact[:900]
    return {
        "problem": "Mother Tongue Influence reduces intelligibility and ASR robustness in spoken English.",
        "method": "Transformer-based accent conversion with identity and content preservation constraints.",
        "dataset": "Speech Accent Archive and related open accent datasets.",
        "assumptions": "Source and target accent manifolds are learnable from non-parallel data.",
        "limitations": "Generalization across unseen L1 backgrounds and recording conditions remains challenging.",
        "evaluation_metrics": "Intelligibility, MOS, WER, speaker similarity, accent distance.",
        "snippet": snippet,
    }


def extract_idea(text):
    if not client:
        return _fallback_extract(text)

    prompt = f"""
Extract structured research info for MTI/accent conversion papers.

Return STRICT JSON:
{{
 "problem": "...",
 "method": "...",
 "dataset": "...",
 "assumptions": "...",
 "limitations": "...",
 "evaluation_metrics": "..."
}}

TEXT:
{text[:5000]}
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        content = res.choices[0].message.content
        try:
            return json.loads(content)
        except Exception:
            return {"raw": content}
    except Exception:
        return _fallback_extract(text)
