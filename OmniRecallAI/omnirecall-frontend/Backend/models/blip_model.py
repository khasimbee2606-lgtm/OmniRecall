from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch


class BLIPModel:

    def __init__(self):

        print("Loading BLIP Model...")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )

        self.model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        ).to(self.device)

        self.model.eval()

        print("BLIP Loaded Successfully")

    # =====================================================

    def generate_caption(self, image_path):

        image = Image.open(image_path).convert("RGB")

        inputs = self.processor(
            images=image,
            return_tensors="pt"
        )

        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():

            output = self.model.generate(

                **inputs,

                max_new_tokens=25,

                min_new_tokens=5,

                num_beams=5,

                early_stopping=True,

                no_repeat_ngram_size=2,

                repetition_penalty=1.5,

                length_penalty=1.0

            )

        caption = self.processor.decode(

            output[0],

            skip_special_tokens=True

        ).strip()

        return caption


# =====================================================

if __name__ == "__main__":

    blip = BLIPModel()

    image_path = "../uploads/test.jpg"

    caption = blip.generate_caption(image_path)

    print("\nCaption :", caption)