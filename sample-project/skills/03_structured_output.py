"""Skill 3: Structured Output Extraction

Demonstrates:
- Extracting typed, structured data from unstructured text
- JSON output parsing
- Schema-driven prompting
"""

import json
import anthropic

client = anthropic.Anthropic()

EXTRACT_PROMPT = """\
Extract structured data from the following text. Return ONLY valid JSON matching this schema:

{{
  "people": [
    {{
      "name": "string",
      "role": "string or null",
      "company": "string or null"
    }}
  ],
  "dates": ["YYYY-MM-DD"],
  "action_items": ["string"],
  "sentiment": "positive | negative | neutral"
}}

Text:
{text}
"""

SAMPLE_TEXT = """
Hey Sarah, just following up from our call with Mike Chen from Acme Corp yesterday
(March 10th). He's interested in the enterprise plan and wants a demo by Friday.
Can you loop in Jake from engineering to prep the staging environment? Also, the
contract renewal for BigCo is due next Tuesday — let's not drop the ball on that one.
Overall feeling good about Q2 pipeline.
"""


def extract(text: str) -> dict:
    """Extract structured data from unstructured text."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": EXTRACT_PROMPT.format(text=text)}],
    )
    return json.loads(response.content[0].text)


def main():
    print("Input text:")
    print(SAMPLE_TEXT.strip())
    print("\nExtracted data:")
    result = extract(SAMPLE_TEXT)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
