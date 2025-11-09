import fitz
import json
import os


def vider_dossier(dossier):
    if not os.path.exists(dossier):
        print("[ERREUR] Dossier inexistant.")
        return
    i=0
    print(f"[INFO] Suppression des fichiers de {dossier} en cours...")
    for filename in os.listdir(dossier):
        file_path = os.path.join(dossier, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                i+=1
        except Exception as e:
            print(f"[ERREUR] Suppression {file_path}: {e}")
    print(f"[OK] {i} fichiers supprimés")


def convert_points(points, json_width, json_height, page_width, page_height):
    scale_x = page_width / json_width
    scale_y = page_height / json_height
    converted = []
    for x, y in points:
        new_x = x * scale_x
        new_y = y * scale_y
        converted.append((new_x, new_y))
    return converted

def extract_zone_pdf_vector(pdf_path, page_num, points, json_width, json_height, output_pdf_path, margin_px=20):
    doc = fitz.open(pdf_path)
    
    page = doc.load_page(page_num - 1)
    page_rect = page.rect
    page_width = page_rect.width
    page_height = page_rect.height
    
    
    conv_points = convert_points(points, json_width, json_height, page_width, page_height)
    
    x_coords = [p[0] for p in conv_points]
    y_coords = [p[1] for p in conv_points]
    rect = fitz.Rect(min(x_coords), min(y_coords), max(x_coords), max(y_coords))
    
    rect = fitz.Rect(
        rect.x0 - margin_px,
        rect.y0,
        rect.x1 + margin_px,
        rect.y1 + 5.5
    )
    
    
    if not page_rect.contains(rect):
        
        rect = rect & page_rect


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
    
    

def isoler_pdf(rad_pdf_reduit, json_cleaned , dossier_pdf_isoles):
    rad_pdf_reduit = rad_pdf_reduit + ".pdf"
    json_cleaned = json_cleaned + ".json"
    with open(json_cleaned, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    vider_dossier(dossier_pdf_isoles)
    i=0
    for element in json_data:
        if element["type"] == "Table":
            meta = element["metadata"]
            coords = meta["coordinates"]["points"]
            page = meta["page_number"]
            element_id = element["element_id"]
            json_w = meta["coordinates"]["layout_width"]
            json_h = meta["coordinates"]["layout_height"]
            output_file = f"{dossier_pdf_isoles}/{element_id}.pdf"
            i+=extract_zone_pdf_vector(rad_pdf_reduit, page, coords, json_w, json_h, output_file)
    print(f"[OK] {i} extraits pdf isolés")
    return



if __name__ == "__main__":
    file = "inputs/file_example"
    json_cleaned = "inputs/file_example-partioned-cleaned"
    dossier_pdf_isoles = "inputs/extracts/pdf"
    isoler_pdf(file, json_cleaned, dossier_pdf_isoles)




