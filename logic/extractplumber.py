import os
import pdfplumber


def clear_folder(folder):
    """Delete all files in a given folder."""
    if not os.path.exists(folder):
        print("❌ The folder does not exist.")
        return

    deleted_count = 0
    print(f"[INFO] Deleting files from {folder}...")

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                deleted_count += 1
        except Exception as e:
            print(f"❌ Error deleting {file_path}: {e}")

    print(f"[OK] {deleted_count} files deleted.")


def extract_plumber(input_folder, output_folder):
    """Extract the first table from each PDF using pdfplumber."""

    os.makedirs(output_folder, exist_ok=True)
    clear_folder(output_folder)

    extracted_count = 0
    no_table_count = 0

    for filename in os.listdir(input_folder):
        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(input_folder, filename)

        try:
            with pdfplumber.open(pdf_path) as pdf:
                page = pdf.pages[0]
                bbox = page.bbox
                crop = page.within_bbox(bbox)
                table = crop.extract_table()

                if not table:
                    # print(f"  No table detected in {filename}")
                    no_table_count += 1
                    continue

                # Prepare the extracted table content
                lines = []
                for row in table:
                    line = " | ".join(cell or "" for cell in row)
                    lines.append(line)
                content = "\n".join(lines)

                # Save extracted table as text
                output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.txt")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)

                extracted_count += 1


        except Exception as e:
            print(f"  Error processing {filename}: {e}")

    print(f"[OK] PdfPlumber extraction completed: {extracted_count} tables extracted; {no_table_count} files without tables.")


if __name__ == "__main__":
    input_folder = "inputs/extracts/pdf"
    output_folder = "inputs/extracts/plumber"
    extract_plumber(input_folder, output_folder)
