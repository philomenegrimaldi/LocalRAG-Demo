import fitz
import json
import os


def clear_folder(folder):
    """Delete all files in the given folder."""
    if not os.path.exists(folder):
        print("[ERROR] Folder does not exist.")
        return

    count = 0
    print(f"[INFO] Deleting files in {folder}...")
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                count += 1
        except Exception as e:
            print(f"[ERROR] Failed to delete {file_path}: {e}")
    print(f"[OK] {count} files deleted.")


def convert_points(points, json_width, json_height, page_width, page_height):
    """Convert points from JSON coordinates to PDF coordinates."""
    scale_x = page_width / json_width
    scale_y = page_height / json_height
    converted = [(x * scale_x, y * scale_y) for x, y in points]
    return converted


def extract_pdf_zone(pdf_path, page_num, points, json_width, json_height, output_pdf_path, margin_px=20):
    """Extract a rectangular zone from a PDF page and save as a new PDF."""
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num - 1)
    page_rect = page.rect
    page_width = page_rect.width
    page_height = page_rect.height

    conv_points = convert_points(points, json_width, json_height, page_width, page_height)
    x_coords = [p[0] for p in conv_points]
    y_coords = [p[1] for p in conv_points]
    rect = fitz.Rect(min(x_coords), min(y_coords), max(x_coords), max(y_coords))

    # Add margins
    rect = fitz.Rect(
        rect.x0 - margin_px,
        rect.y0,
        rect.x1 + margin_px,
        rect.y1 + 5.5
    )

    # Ensure rectangle is within page bounds
    if not page_rect.contains(rect):
        rect = rect & page_rect

    # Create new PDF for the extracted zone
    new_doc = fitz.open()
    clip_width = rect.width
    clip_height = rect.height
    new_page = new_doc.new_page(width=clip_width, height=clip_height)

    new_page.show_pdf_page(
        fitz.Rect(0, 0, clip_width, clip_height),
        doc,
        page_num - 1,
        clip=rect
    )

    new_doc.save(output_pdf_path)
    new_doc.close()
    doc.close()
    return 1


def isolate_pdf(pdf_file, json_cleaned, output_folder):
    """Isolate all Table elements from a PDF according to JSON coordinates."""
    pdf_file = pdf_file + ".pdf"
    json_cleaned = json_cleaned + ".json"

    with open(json_cleaned, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    clear_folder(output_folder)

    extracted_count = 0
    for element in json_data:
        if element["type"] == "Table":
            meta = element["metadata"]
            coords = meta["coordinates"]["points"]
            page = meta["page_number"]
            element_id = element["element_id"]
            json_w = meta["coordinates"]["layout_width"]
            json_h = meta["coordinates"]["layout_height"]
            output_file = os.path.join(output_folder, f"{element_id}.pdf")
            extracted_count += extract_pdf_zone(pdf_file, page, coords, json_w, json_h, output_file)

    print(f"[OK] {extracted_count} isolated PDF extracts created.")


if __name__ == "__main__":
    pdf_file = "inputs/file_example"
    json_cleaned = "inputs/file_example-partitioned-cleaned"
    output_folder = "inputs/extracts/pdf"
    isolate_pdf(pdf_file, json_cleaned, output_folder)
