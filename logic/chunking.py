import json
import os

def chunk_text_with_separator(
    input_file,
    separator="-------------------------------------------------------------",
    max_chunk_size=1000,
    overlap=100
):
    # Prevent invalid overlap configuration
    if overlap >= max_chunk_size:
        overlap = max_chunk_size // 2

    # Read full text
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    # Split text using the separator and clean empty parts
    parts = [p.strip() for p in text.split(separator) if p.strip()]

    chunks = []
    current_chunk = ""

    for part in parts:
        part_text = f"{separator}\n{part}"

        # If part is larger than max_chunk_size, split it with overlap
        if len(part_text) > max_chunk_size:
            start = 0
            while start < len(part_text):
                end = min(start + max_chunk_size, len(part_text))
                chunk_text = part_text[start:end]
                chunks.append(chunk_text.strip())
                start += max_chunk_size - overlap
        else:
            # Add smaller parts to the current chunk
            if len(current_chunk) + len(part_text) <= max_chunk_size:
                current_chunk += "\n" + part_text
            else:
                chunks.append(current_chunk.strip())
                current_chunk = part_text

    # Add any remaining text
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def chunking(input_path, output_path):
    # Ensure correct file extensions
    if not input_path.endswith(".txt"):
        input_path += ".txt"
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    if not output_path.endswith(".json"):
        output_path += ".json"

    # Perform chunking
    chunks = chunk_text_with_separator(input_path)


    # Create JSON structure
    json_chunks = [
        {"chunk_id": f"chunk_{i+1:03d}", "text": chunk}
        for i, chunk in enumerate(chunks)
    ]

    # Save as JSON file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_chunks, f, ensure_ascii=False, indent=2)

    print(f"[OK] Saved {len(chunks)} chunks to {output_path}")


if __name__ == "__main__":
    chunking("inputs/file-reconstituted", "inputs/file-chunked")
