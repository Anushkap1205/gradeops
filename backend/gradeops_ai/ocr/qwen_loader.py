import torch
from PIL import Image
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

_MODEL_NAME = "Qwen/Qwen2-VL-2B-Instruct"
_DEVICE = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
_DTYPE = torch.float16 if _DEVICE in ["cuda", "mps"] else torch.float32

_model = None
_processor = None


def _load_model():
    global _model, _processor
    if _model is None or _processor is None:
        _processor = AutoProcessor.from_pretrained(_MODEL_NAME)
        _model = Qwen2VLForConditionalGeneration.from_pretrained(
            _MODEL_NAME,
            torch_dtype=_DTYPE,
            device_map=_DEVICE,
        )
        _model.eval()
    return _model, _processor


def extract_text_from_image(image_path: str) -> str:
    model, processor = _load_model()

    image = Image.open(image_path).convert("RGB")

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": "Extract all text from this image. Return only the extracted text, preserving the original layout and line breaks where possible. Do not add explanations."},
            ],
        }
    ]

    prompt = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = processor(
        text=[prompt],
        images=[image],
        padding=True,
        return_tensors="pt",
    ).to(_DEVICE)

    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=1024,
            do_sample=False,
        )

    trimmed_ids = [
        output_ids[len(input_ids):]
        for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
    ]

    output_text = processor.batch_decode(
        trimmed_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0]

    return output_text.strip()
