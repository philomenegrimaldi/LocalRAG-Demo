import os
import fitz  # PyMuPDF

def clear_folder(folder):
    """Delete all files in a given folder."""
    if not os.path.exists(folder):
        print("[ERROR] Folder does not exist.")
        return
    count = 0
    print(f"[INFO] Deleting files from {folder}...")
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                count += 1
        except Exception as e:
            print(f"[ERROR] Failed to delete {file_path}: {e}")
    print(f"[OK] {count} files deleted.")


def extract_fitz(input_folder, output_folder):
    """Extract text from the first page of each PDF in input_folder using PyMuPDF (fitz)."""
    os.makedirs(output_folder, exist_ok=True)
    clear_folder(output_folder)

    extracted_count = 0
    error_count = 0

    for filename in os.listdir(input_folder):
        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(input_folder, filename)
        try:
            doc = fitz.open(pdf_path)
            page = doc[0]  # first page
            content_text = page.get_text("text").strip()

            output_name = os.path.splitext(filename)[0] + ".txt"
            output_path = os.path.join(output_folder, output_name)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content_text)

            extracted_count += 1

        except Exception as e:
            # print(f"[ERROR] Failed with {filename}: {e}")
            error_count += 1

    print(f"[OK] Fitz extraction completed. Extracted: {extracted_count} | Errors: {error_count}")



if __name__ == "__main__":
    input_folder = "inputs/extracts/pdf"
    output_folder = "inputs/extracts/fitz"
    extract_fitz(input_folder, output_folder)
