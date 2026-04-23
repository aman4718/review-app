import os
import json
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

SYSTEM_PROMPT = """You are a senior product analyst at an AI company.
You analyse app store reviews and extract product insights.
Rules:
- Return ONLY valid JSON. No markdown, no explanation.
- Never include usernames, emails, or any PII in quotes.
- Quotes must be verbatim from the reviews provided.
- Be concise. Each summary must be 2 sentences max."""

THEME_PROMPT = """Here are {n} Play Store reviews for the ChatGPT app (India),
grouped under the theme: '{theme_label}'.

REVIEWS:
{reviews_text}

Return a JSON object with exactly these keys:
{{
  "theme_name": "string (3-5 word label)",
  "review_count": {n},
  "sentiment": "positive or negative or mixed",
  "summary": "string (2 sentences)",
  "top_quotes": ["quote1", "quote2", "quote3"],
  "action_item": "string (1 concrete PM action)"
}}"""

SUMMARY_PROMPT = """Given these 5 theme analyses for the ChatGPT India app:
{all_themes_json}

Return a JSON object:
{{
  "executive_summary": "string (3 sentences, stakeholder-ready)",
  "top_3_themes": ["theme1", "theme2", "theme3"],
  "top_3_actions": ["action1", "action2", "action3"],
  "week": "{week}"
}}"""

def analyse():
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    df = pd.read_csv(os.path.join(DATA_DIR, 'clustered_reviews.csv'))

    from datetime import date
    week = date.today().strftime('%Y-%W')
    theme_results = []

    for theme_id in sorted(df['theme_id'].unique()):
        theme_df = df[df['theme_id'] == theme_id]
        theme_label = theme_df['theme_label'].iloc[0]
        sample = theme_df['review_text'].dropna().head(10).tolist()
        reviews_text = '\n'.join(f"- {r}" for r in sample)
        n = len(sample)

        print(f"Analysing theme {theme_id}: {theme_label}...")

        prompt = THEME_PROMPT.format(
            n=n,
            theme_label=theme_label,
            reviews_text=reviews_text
        )

        response = client.chat.completions.create(
            model='llama-3.1-8b-instant',
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': prompt}
            ],
            temperature=0.3
        )

        raw = response.choices[0].message.content.strip()
        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            result = json.loads(match.group()) if match else {"theme_name": theme_label, "error": "parse failed"}

        theme_results.append(result)

    print("Generating executive summary...")
    summary_prompt = SUMMARY_PROMPT.format(
        all_themes_json=json.dumps(theme_results, indent=2),
        week=week
    )

    summary_response = client.chat.completions.create(
        model='llama-3.1-8b-instant',
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': summary_prompt}
        ],
        temperature=0.3
    )

    raw_summary = summary_response.choices[0].message.content.strip()
    try:
        summary = json.loads(raw_summary)
    except json.JSONDecodeError:
        import re
        match = re.search(r'\{.*\}', raw_summary, re.DOTALL)
        summary = json.loads(match.group()) if match else {"executive_summary": "Summary unavailable"}

    pulse = {
        'top_themes': theme_results,
        'executive_summary': summary.get('executive_summary', ''),
        'top_3_themes': summary.get('top_3_themes', []),
        'top_3_actions': summary.get('top_3_actions', []),
        'week': summary.get('week', week)
    }

    out_path = os.path.join(DATA_DIR, 'pulse.json')
    with open(out_path, 'w') as f:
        json.dump(pulse, f, indent=2)

    print(f"Saved pulse.json with {len(theme_results)} themes.")

if __name__ == '__main__':
    analyse()
