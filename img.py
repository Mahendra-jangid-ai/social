from typing import List
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
import os

# ============================================================
# 🔐 LOAD API KEY
# ============================================================

# GROQ_API_KEY = "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"
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not set in environment")

# ============================================================
# 🧠 LOAD BLIP MODEL (LOCAL – FREE)
# ============================================================

device = "cuda" if torch.cuda.is_available() else "cpu"

print("Loading BLIP model...")
processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base",
).to(device)
print("BLIP model loaded on", device)

# ============================================================
# 🖼️ IMAGE → CAPTION (TRANSFORMERS)
# ============================================================

def generate_caption_from_image(image_path: str) -> str:
    image = Image.open(image_path).convert("RGB")

    inputs = processor(image, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_new_tokens=30)

    caption = processor.decode(outputs[0], skip_special_tokens=True)
    return caption.strip()

# ============================================================
# 🔥 CAPTION → TRENDING + VIRAL HASHTAGS (LANGCHAIN + GROQ)
# ============================================================

def generate_trending_hashtags(caption: str) -> List[str]:
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name="llama-3.1-8b-instant",
        temperature=0.7,
        max_tokens=120,
    )

    prompt = (
        "You are a professional social media growth expert.\n"
        "Generate EXACTLY 10 trending and viral hashtags.\n\n"
        f"Image description: {caption}\n\n"
        "Rules:\n"
        "- lowercase only\n"
        "- no emojis\n"
        "- no numbers\n"
        "- no repetition\n"
        "- mix viral + niche\n"
        "- output only space separated hashtags\n"
    )

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    hashtags = response.content.strip().split()
    return hashtags[:10]

# ============================================================
# 🚀 IMAGE → HASHTAGS (ONE CALL)
# ============================================================

def generate_hashtags_from_image(image_path: str):
    caption = generate_caption_from_image(image_path)
    hashtags = generate_trending_hashtags(caption)

    return {
        "caption": caption,
        "hashtags": hashtags
    }

# ============================================================
# 🧪 RUN
# ============================================================

if __name__ == "__main__":
    image_path = r"c:/Users/Mahendra/Downloads/a6123848-627b-4b73-99a4-5f07f7fb380a.png"

    result = generate_hashtags_from_image(image_path)

    print("\n🖼️ IMAGE CAPTION:")
    print(result["caption"])

    print("\n🔥 TRENDING & VIRAL HASHTAGS:")
    print(" ".join(result["hashtags"]))
