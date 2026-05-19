import torch
from PIL import Image
from transformers import VisionEncoderDecoderModel, NougatProcessor

_MODEL_NAME = "facebook/nougat-base"
_DEVICE = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")

_model = None
_processor = None


def _load_model():
    global _model, _processor

    if _model is None or _processor is None:
        _processor = NougatProcessor.from_pretrained(_MODEL_NAME)
        _model = VisionEncoderDecoderModel.from_pretrained(_MODEL_NAME)
        _model.to(_DEVICE)
        _model.eval()

    return _model, _processor


def extract_text_from_image(image_path: str) -> str:
    model, processor = _load_model()

    image = Image.open(image_path).convert("RGB")

    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(_DEVICE)

    with torch.no_grad():
        generated_ids = model.generate(pixel_values=pixel_values, max_new_tokens=1024)

    sequence = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    text = processor.post_process_generation(sequence, fix_markdown=False)

    return text.strip()
