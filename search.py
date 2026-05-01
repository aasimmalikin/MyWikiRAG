from datasets import load_dataset

# Load latest processed Wikipedia (already cleaned!)
dataset = load_dataset("wikimedia/wikipedia", "20231101.en", split="train")

# Example: save first 10k articles as JSON for your RAG
dataset.select(range(10000)).to_json("wikipedia_sample.jsonl")