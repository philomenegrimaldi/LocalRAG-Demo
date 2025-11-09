import json
from html.parser import HTMLParser
import json

def cleaning(json_partitioned, json_cleaned):
    print("[INFO] Début cleaning")
    input_json_path = f"{json_partitioned}.json"
    output_json_path = f"{json_cleaned}.json"


    with open(input_json_path, "r", encoding="utf-8") as f:
        elements = json.load(f)

    cleaned_elements = []
    compteur_cleaned = 0
   

    # identification des ovni (objets visuels non identifiés)
    for el in elements:
        points = el.get("metadata", {}).get("coordinates", {}).get("points", [])
        if points and points[0][1] >= 2150:
            el["type"] = "Footer"


    for el2 in elements:
        if el2.get("type", {}) not in ("Footer", "Image"):
            cleaned_elements.append(el2)
            compteur_cleaned += 1

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_elements, f, ensure_ascii=False, indent=2)

    print(f"[OK] JSON nettoyé: {output_json_path} ({compteur_cleaned} éléments)")
    return




if __name__ == "__main__":
    
    json_partitioned = "inputs/file_example-partitioned"
    json_cleaned = "inputs/file_example-partioned-cleaned"
    cleaning(json_partitioned,json_cleaned)

