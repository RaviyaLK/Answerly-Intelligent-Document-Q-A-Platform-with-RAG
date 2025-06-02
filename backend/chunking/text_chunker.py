# chunking/text_chunker.py
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        chunk = " ".join(words[start:start + chunk_size])
        token_count = len(tokenizer.encode(chunk, add_special_tokens=False))

        # Only keep chunks with meaningful length
        if token_count > 10:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks
