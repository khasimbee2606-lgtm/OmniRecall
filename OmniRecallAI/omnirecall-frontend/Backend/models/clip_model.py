import torch
import open_clip
from PIL import Image
import numpy as np
class CLIPModel:

    def __init__(self):

        # Use GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load pretrained CLIP model
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            "ViT-B-32",
            pretrained="laion2b_s34b_b79k"
        )

        self.model.to(self.device)
        self.model.eval()

        self.tokenizer = open_clip.get_tokenizer("ViT-B-32")

    # ----------------------------------------

    def encode_image(self, image_path):

        image = self.preprocess(
            Image.open(image_path).convert("RGB")
        ).unsqueeze(0).to(self.device)

        with torch.no_grad():

            image_features = self.model.encode_image(image)

            image_features /= image_features.norm(dim=-1, keepdim=True)

        return image_features.cpu().numpy()[0]

    # ----------------------------------------

    def encode_text(self, text):

        text_tokens = self.tokenizer([text]).to(self.device)

        with torch.no_grad():

            text_features = self.model.encode_text(text_tokens)

            text_features /= text_features.norm(dim=-1, keepdim=True)

        return text_features.cpu().numpy()[0]

    # ----------------------------------------

    def cosine_similarity(self, image_embedding, text_embedding):

        return float(np.dot(image_embedding, text_embedding))


# -------------------------------------------------------------

if __name__ == "__main__":

    clip = CLIPModel()

    image_path = "../uploads/test.jpg"

    image_embedding = clip.encode_image(image_path)

    text_embedding = clip.encode_text("person")

    similarity = clip.cosine_similarity(
        image_embedding,
        text_embedding
    )

    print("\nImage Embedding Shape :", image_embedding.shape)
    print("Text Embedding Shape  :", text_embedding.shape)
    print("Similarity Score      :", round(similarity, 4))