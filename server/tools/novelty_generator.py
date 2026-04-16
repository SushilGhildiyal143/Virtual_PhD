import os
from openai import OpenAI

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY) if API_KEY else None


def generate_novel_idea(gaps_text: str) -> str:
    if not client:
        return f"""Core hypothesis:
Explicitly disentangling accent, content, and speaker embeddings in a Transformer encoder-decoder can reduce Mother Tongue Influence in spoken English while preserving identity and naturalness.

Proposed method:
Use a reference-free MTI reduction model with scheduled sampling, phoneme-aware alignment loss, and speaker-contrastive consistency. Add a controllable accent-strength token for deployment personalization.

Expected benefit:
Higher intelligibility and lower ASR error without the identity collapse often seen in accent conversion systems.

Validation plan:
1. Train on Speech Accent Archive with Spanish-accented English as source and Standard American English as target style.
2. Evaluate intelligibility, MOS, WER, speaker similarity, accent distance, and fairness slices.
3. Stress-test on spontaneous speech, noisy channels, and code-switching segments.

Input gaps:
{gaps_text}
"""
    prompt = f"""
You are a senior research scientist.

Given these research gaps, propose one concrete, novel, and testable research idea.

Requirements:
1. Practical for real-world deployment.
2. Avoid generic "combine X and Y" suggestions.
3. Clearly state:
   - core hypothesis
   - proposed method
   - expected benefit
   - validation plan

Research gaps:
{gaps_text}
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        return res.choices[0].message.content
    except Exception:
        return f"Core hypothesis:\n\nInput gaps:\n{gaps_text}\n"
