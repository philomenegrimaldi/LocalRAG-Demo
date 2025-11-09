import json
import os

def chunk_text_with_separator(
    RAD_reconstitue,
    separator="-------------------------------------------------------------",
    max_chunk_size=1000,
    overlap=100
):
    if overlap >= max_chunk_size:
        overlap = max_chunk_size // 2

    with open(RAD_reconstitue, "r", encoding="utf-8") as f:
        text = f.read()

    parts = [p.strip() for p in text.split(separator) if p.strip()]

    chunks = []
    current_chunk = ""

    for part in parts:
        part_text = f"{separator}\n{part}"

        if len(part_text) > max_chunk_size:
            # découpage avec overlap
            start = 0
            while start < len(part_text):
                end = min(start + max_chunk_size, len(part_text))
                chunk_text = part_text[start:end]
                chunks.append(chunk_text.strip())
                start += max_chunk_size - overlap
        else:
            if len(current_chunk) + len(part_text) <= max_chunk_size:
                current_chunk += "\n" + part_text
            else:
                chunks.append(current_chunk.strip())
                current_chunk = part_text

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def chunking(RAD_reconstitue, output_path):
    if not RAD_reconstitue.endswith(".txt"):
        RAD_reconstitue += ".txt"
    if not os.path.exists(RAD_reconstitue):
        raise FileNotFoundError(f"Fichier introuvable : {RAD_reconstitue}")

    if not output_path.endswith(".json"):
        output_path += ".json"

    chunks = chunk_text_with_separator(RAD_reconstitue)

    json_chunks = [
        {"chunk_id": f"chunk_{i+1:03d}", "text": chunk}
        for i, chunk in enumerate(chunks)
    ]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_chunks, f, ensure_ascii=False, indent=2)

    print(f"[OK] Sauvegarde des {len(chunks)} chunks dans {output_path}")


if __name__ == "__main__":
    chunking("inputs/file-reconstitue", "inputs/file-chunked")
