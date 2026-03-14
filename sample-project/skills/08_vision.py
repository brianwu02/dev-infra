"""Skill 8: Image Analysis (Vision)

Demonstrates:
- Sending images to Claude for analysis
- Base64 encoding for local images
- URL-based image input
- Combining image + text prompts
"""

import base64
import sys
import anthropic

client = anthropic.Anthropic()


def analyze_image_url(image_url: str, question: str = "Describe this image in detail.") -> str:
    """Analyze an image from a URL."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "url", "url": image_url}},
                {"type": "text", "text": question},
            ],
        }],
    )
    return response.content[0].text


def analyze_image_file(file_path: str, question: str = "Describe this image in detail.") -> str:
    """Analyze a local image file."""
    ext = file_path.rsplit(".", 1)[-1].lower()
    media_types = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "webp": "image/webp"}
    media_type = media_types.get(ext, "image/png")

    with open(file_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}},
                {"type": "text", "text": question},
            ],
        }],
    )
    return response.content[0].text


def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        question = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Describe this image in detail."
        print(f"Analyzing: {file_path}")
        print(f"Question: {question}\n")
        print(analyze_image_file(file_path, question))
    else:
        print("Usage: python 08_vision.py <image_path> [question]")
        print("       python 08_vision.py screenshot.png 'What errors are shown?'")
        print("       python 08_vision.py diagram.png 'Explain the architecture'")


if __name__ == "__main__":
    main()
