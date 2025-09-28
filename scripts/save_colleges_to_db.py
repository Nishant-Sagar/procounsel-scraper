import os
import re
import json
from typing import Dict, Any
from google.cloud import firestore


class FirestoreLoader:
    def __init__(self) -> None:
        # Uses Application Default Credentials (ADC)
        self.db = firestore.Client()

    @staticmethod
    def clean_content(text: str) -> str:
        """Clean scraped text by removing newlines, multiple spaces, and junk."""
        if not text:
            return ""
        # Collapse whitespace/newlines
        text = re.sub(r"\s+", " ", text)
        # Example: remove ad-like patterns
        text = re.sub(r"Get Upto.*?Explore", "", text, flags=re.IGNORECASE)
        return text.strip()

    def save_json_to_firestore(
        self,
        college_name: str,
        file_name: str,
        data: Dict[str, Any]
    ) -> None:
        """Clean JSON and store in Firestore using filename as doc ID, skip if exists."""
        # Ensure required fields exist
        data["content"] = self.clean_content(data.get("content", ""))
        data["category"] = str(data.get("category", "unknown"))
        data["scraped_at"] = str(data.get("scraped_at", ""))
        data["url"] = str(data.get("url", ""))
        data["title"] = str(data.get("title", ""))

        college_name = college_name.upper()

        # Use filename (without extension) as Firestore doc ID
        doc_id: str = file_name.replace(".json", "")

        doc_ref = (
            self.db.collection("collegeScrape")
            .document(college_name)
            .collection("data")
            .document(doc_id)
        )

        # Check if document already exists
        if doc_ref.get().exists:
            print(f"⏩ Skipped (already exists): {doc_id} for {college_name}")
            return

        # Save new doc
        doc_ref.set(data)
        print(f"Saved doc {doc_id} for {college_name}")

    def process_base_folder(self, base_path: str) -> None:
        """Iterate through college folders and upload all JSON files."""
        for college_name in os.listdir(base_path):
            college_path = os.path.join(base_path, college_name)
            if not os.path.isdir(college_path):
                continue

            for file_name in os.listdir(college_path):
                if file_name.endswith(".json"):
                    file_path = os.path.join(college_path, file_name)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            data: Dict[str, Any] = json.load(f)
                            self.save_json_to_firestore(college_name, file_name, data)
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    loader = FirestoreLoader()
    loader.process_base_folder("./scraped_data")

