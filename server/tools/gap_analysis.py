import os
from openai import OpenAI

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY) if API_KEY else None


def analyze_gaps(ideas):
    if not client:
        return """Research Gaps (fallback mode):
1. Scarcity of large, balanced non-parallel corpora for Indian multilingual accents in English.
2. Weak speaker-identity preservation under strong accent normalization.
3. Limited evaluation on code-switching and spontaneous conversational speech.
4. Poor robustness to microphone/channel shift and background noise.
5. Insufficient fairness auditing across gender, age, and regional L1 groups.
6. Lack of deployment-time controls for user-adjustable accent strength.
7. Limited integration with downstream ASR/voice-agent improvements.
"""

    prompt = f"""
You are a research scientist.

Given structured paper summaries:

{ideas}

Identify:
1. Hidden assumptions
2. Failure cases (real-world)
3. Dataset bias / domain gaps
4. Evaluation weaknesses
5. Scalability and deployment issues

Output:
- Numbered list of practical, testable MTI research gaps.
- Avoid generic or trivial suggestions.
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        return res.choices[0].message.content
    except Exception:
        return "Research Gaps (fallback mode):\n"
