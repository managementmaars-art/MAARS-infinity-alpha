---
name: ai-research-multimodal
description: "CLIP, LLaVA, Whisper, Stable Diffusion, SAM, BLIP-2, multimodal RAG, vision-language models"
---

# AI Research: Multimodal Models

Production usage of vision-language models: CLIP for zero-shot classification and similarity, LLaVA/BLIP-2 for image understanding, Whisper for speech, Stable Diffusion for generation, SAM for segmentation, and multimodal RAG pipelines.

## CLIP: Zero-Shot and Similarity

```python
import torch
import clip
from PIL import Image
import numpy as np

device = "cuda" if torch.cuda.is_available() else "cpu"

# Load CLIP model
model, preprocess = clip.load("ViT-L/14", device=device)
model.eval()

def encode_images(image_paths: list[str]) -> torch.Tensor:
    """Encode images to CLIP embeddings."""
    images = torch.stack([
        preprocess(Image.open(p).convert("RGB"))
        for p in image_paths
    ]).to(device)

    with torch.no_grad():
        features = model.encode_image(images)
        features = features / features.norm(dim=-1, keepdim=True)  # L2 normalize
    return features.cpu()

def encode_texts(texts: list[str]) -> torch.Tensor:
    """Encode texts to CLIP embeddings."""
    tokens = clip.tokenize(texts, truncate=True).to(device)
    with torch.no_grad():
        features = model.encode_text(tokens)
        features = features / features.norm(dim=-1, keepdim=True)
    return features.cpu()

def zero_shot_classify(image_path: str, categories: list[str], templates: list[str] | None = None) -> dict:
    """Zero-shot image classification with optional prompt ensembling."""
    if templates is None:
        templates = ["a photo of a {}", "an image of a {}", "a picture of a {}"]

    # Ensemble multiple prompts per class
    all_text_features = []
    for category in categories:
        category_features = encode_texts([t.format(category) for t in templates])
        all_text_features.append(category_features.mean(0))  # average over templates

    text_features = torch.stack(all_text_features)
    text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    image_features = encode_images([image_path])

    similarities = (100.0 * image_features @ text_features.T).softmax(dim=-1)
    return {cat: float(sim) for cat, sim in zip(categories, similarities[0])}

def image_text_similarity(image_paths: list[str], texts: list[str]) -> np.ndarray:
    """Compute pairwise similarity matrix between images and texts."""
    img_features = encode_images(image_paths)     # [N, D]
    txt_features = encode_texts(texts)            # [M, D]
    return (img_features @ txt_features.T).numpy()  # [N, M]

# OpenCLIP for newer models (ViT-H, SigLIP, etc.)
import open_clip

model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-H-14", pretrained="laion2b_s32b_b79k"
)
tokenizer = open_clip.get_tokenizer("ViT-H-14")
```

## LLaVA / BLIP-2: Vision-Language Understanding

```python
from transformers import LlavaNextProcessor, LlavaNextForConditionalGeneration
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import torch
from PIL import Image
import requests

# LLaVA-1.6 (LLaVA-NeXT)
processor = LlavaNextProcessor.from_pretrained("llava-hf/llava-v1.6-mistral-7b-hf")
model = LlavaNextForConditionalGeneration.from_pretrained(
    "llava-hf/llava-v1.6-mistral-7b-hf",
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
    device_map="auto",
)

def llava_inference(image: Image.Image, question: str, max_tokens: int = 512) -> str:
    """Run LLaVA inference on an image-question pair."""
    conversation = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": question},
            ],
        }
    ]
    prompt = processor.apply_chat_template(conversation, add_generation_prompt=True)
    inputs = processor(images=image, text=prompt, return_tensors="pt").to(model.device, torch.bfloat16)

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=False,
            temperature=None,
            top_p=None,
        )

    # Decode only the generated tokens
    generated = outputs[0][inputs["input_ids"].shape[1]:]
    return processor.decode(generated, skip_special_tokens=True)

def analyze_document(image_path: str) -> dict:
    """Extract structured information from a document image."""
    image = Image.open(image_path)
    result = {}

    questions = {
        "title": "What is the title or heading of this document?",
        "date": "What date appears in this document? Reply 'none' if absent.",
        "summary": "Summarize the key information in 2-3 sentences.",
        "tables": "Are there any tables? If yes, describe their content.",
    }

    for key, question in questions.items():
        result[key] = llava_inference(image, question, max_tokens=256)

    return result

# BLIP-2: Fast VQA and captioning
blip_processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-6.7b")
blip_model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-6.7b",
    torch_dtype=torch.float16,
    device_map="auto",
)

def blip2_caption(image: Image.Image) -> str:
    inputs = blip_processor(images=image, return_tensors="pt").to("cuda", torch.float16)
    with torch.inference_mode():
        ids = blip_model.generate(**inputs, max_new_tokens=100)
    return blip_processor.decode(ids[0], skip_special_tokens=True)
```

## Whisper: Speech Recognition

```python
import whisper
import numpy as np
from pathlib import Path

# Load Whisper model
model = whisper.load_model("large-v3", device="cuda")

def transcribe_audio(
    audio_path: str,
    language: str | None = None,
    task: str = "transcribe",  # or "translate"
    word_timestamps: bool = True,
) -> dict:
    """Transcribe audio with timestamps."""
    result = model.transcribe(
        audio_path,
        language=language,
        task=task,
        word_timestamps=word_timestamps,
        verbose=False,
        condition_on_previous_text=True,
        temperature=0.0,
    )
    return {
        "text": result["text"],
        "language": result["language"],
        "segments": result["segments"],
    }

# Using faster-whisper (CTranslate2 — 4x faster)
from faster_whisper import WhisperModel

fast_model = WhisperModel("large-v3", device="cuda", compute_type="float16")

def fast_transcribe(audio_path: str) -> str:
    segments, info = fast_model.transcribe(
        audio_path,
        beam_size=5,
        language="en",
        vad_filter=True,            # remove silence
        vad_parameters={"min_silence_duration_ms": 500},
    )
    return " ".join(seg.text for seg in segments)

# Batch transcription pipeline
def transcribe_batch(audio_dir: str, output_dir: str):
    import json
    from concurrent.futures import ThreadPoolExecutor

    audio_files = list(Path(audio_dir).glob("**/*.mp3")) + list(Path(audio_dir).glob("**/*.wav"))
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    def process_file(audio_path: Path):
        result = transcribe_audio(str(audio_path))
        output_path = Path(output_dir) / (audio_path.stem + ".json")
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        return audio_path.name

    with ThreadPoolExecutor(max_workers=4) as executor:
        for name in executor.map(process_file, audio_files):
            print(f"Transcribed: {name}")
```

## Stable Diffusion (Diffusers)

```python
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from diffusers import FluxPipeline
import torch

# SDXL with optimized scheduler
pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.bfloat16,
    variant="fp16",
)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(
    pipe.scheduler.config, use_karras_sigmas=True
)
pipe = pipe.to("cuda")
pipe.enable_model_cpu_offload()   # reduce VRAM usage

def generate_image(
    prompt: str,
    negative_prompt: str = "blurry, low quality, artifacts",
    width: int = 1024,
    height: int = 1024,
    num_steps: int = 30,
    guidance_scale: float = 7.5,
    seed: int | None = None,
) -> Image.Image:
    generator = torch.Generator("cuda").manual_seed(seed) if seed else None
    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=width,
        height=height,
        num_inference_steps=num_steps,
        guidance_scale=guidance_scale,
        generator=generator,
    )
    return result.images[0]

# FLUX.1 for state-of-the-art generation
flux_pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-schnell",
    torch_dtype=torch.bfloat16,
)
flux_pipe.enable_model_cpu_offload()
```

## SAM: Segment Anything Model

```python
from segment_anything import sam_model_registry, SamPredictor, SamAutomaticMaskGenerator
import cv2
import numpy as np

sam = sam_model_registry["vit_h"](checkpoint="sam_vit_h_4b8939.pth")
sam.to("cuda")

# Point-prompted segmentation
predictor = SamPredictor(sam)

def segment_from_points(
    image: np.ndarray,
    point_coords: np.ndarray,   # [[x, y], ...]
    point_labels: np.ndarray,   # 1=foreground, 0=background
) -> tuple[np.ndarray, float]:
    """Segment an object given point prompts."""
    predictor.set_image(image)
    masks, scores, logits = predictor.predict(
        point_coords=point_coords,
        point_labels=point_labels,
        multimask_output=True,
    )
    best_idx = np.argmax(scores)
    return masks[best_idx], scores[best_idx]

# Automatic everything segmentation
mask_generator = SamAutomaticMaskGenerator(
    sam,
    points_per_side=32,
    pred_iou_thresh=0.88,
    stability_score_thresh=0.95,
    crop_n_layers=1,
    crop_n_points_downscale_factor=2,
    min_mask_region_area=100,
)

def segment_all(image: np.ndarray) -> list[dict]:
    """Automatically generate masks for all objects in image."""
    masks = mask_generator.generate(image)
    return sorted(masks, key=lambda x: x["area"], reverse=True)
```

## Multimodal RAG Pipeline

```python
from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import base64
from io import BytesIO

class MultimodalRAG:
    """RAG pipeline that retrieves both text and images."""

    def __init__(self, collection_name: str):
        self.text_store = Chroma(
            collection_name=f"{collection_name}_text",
            embedding_function=OpenAIEmbeddings(model="text-embedding-3-large"),
        )
        self.clip_model, self.clip_preprocess = clip.load("ViT-L/14")

    def index_document(self, doc_path: str, doc_id: str):
        """Index a PDF document with both text and image content."""
        import fitz  # PyMuPDF

        pdf = fitz.open(doc_path)
        for page_num, page in enumerate(pdf):
            # Extract and index text
            text = page.get_text()
            if text.strip():
                self.text_store.add_texts(
                    texts=[text],
                    metadatas=[{"doc_id": doc_id, "page": page_num, "type": "text"}],
                    ids=[f"{doc_id}_p{page_num}_text"],
                )

            # Extract and index page image via CLIP
            pix = page.get_pixmap(dpi=150)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_embedding = encode_images_pil([img])[0].tolist()
            self.image_store.add_embeddings(
                embeddings=[img_embedding],
                metadatas=[{"doc_id": doc_id, "page": page_num, "type": "image"}],
            )

    def query(self, question: str, k: int = 4) -> str:
        """Retrieve relevant context and generate answer."""
        text_docs = self.text_store.similarity_search(question, k=k)

        # Build multimodal context
        context_parts = []
        images_b64 = []

        for doc in text_docs:
            context_parts.append(f"[Page {doc.metadata['page']}]: {doc.page_content}")

        # Query LLaVA with retrieved images
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": f"Context:\n{'---'.join(context_parts)}\n\nQuestion: {question}"},
                *[{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}}
                  for img in images_b64[:2]],
            ]
        }]

        response = openai_client.chat.completions.create(
            model="gpt-4o", messages=messages, max_tokens=1024
        )
        return response.choices[0].message.content
```

## Best Practices

- Use `torch.inference_mode()` (not `torch.no_grad()`) for inference — slightly faster, prevents grad computation
- For CLIP: always L2-normalize embeddings before computing similarity
- Use prompt ensembling for zero-shot CLIP classification: average embeddings from 80 ImageNet templates
- For LLaVA/BLIP-2: batch multiple images when possible; use Flash Attention 2 for long contexts
- For Whisper: use `faster-whisper` in production — 4x faster with identical accuracy
- For SD/FLUX: use `enable_model_cpu_offload()` to fit large models on consumer GPUs
- For SAM: `SamPredictor` is faster when you have point/box prompts; `SamAutomaticMaskGenerator` for everything
- Store CLIP image embeddings in a vector DB (pgvector, Qdrant, Chroma) for scalable image search
- Use `quantize_model()` (BitsAndBytes INT4) for LLaVA to reduce VRAM from 14GB to ~6GB
- In multimodal RAG, always retrieve both text passages and relevant images — image context often has information missing from text

## Models to Use

- **Default**: `claude-sonnet-4-5` — multimodal pipelines, CLIP usage, Whisper, diffusers
- **Research / novel architectures**: `claude-opus-4-5` — custom VLM training, multimodal RAG design, RLHF for vision
- **Quick inference code**: `claude-haiku-3-5` — simple image classification, caption generation, audio transcription
