import json


def cleaning(json_partitioned, json_cleaned):
    print("[INFO] Starting cleaning process...")
    input_json_path = f"{json_partitioned}.json"
    output_json_path = f"{json_cleaned}.json"

    # Load partitioned JSON file
    with open(input_json_path, "r", encoding="utf-8") as f:
        elements = json.load(f)

    cleaned_elements = []
    cleaned_count = 0

    # Identify "UFOs" (unidentified visual objects, e.g. unwanted visual elements)
    for el in elements:
        points = el.get("metadata", {}).get("coordinates", {}).get("points", [])
        if points and points[0][1] >= 2150:
            el["type"] = "Footer"

    # Keep only relevant elements (exclude footers and images)
    for el2 in elements:
        if el2.get("type", {}) not in ("Footer", "Image"):
            cleaned_elements.append(el2)
            cleaned_count += 1

    # Save cleaned JSON
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_elements, f, ensure_ascii=False, indent=2)

    print(f"[OK] Cleaned JSON saved: {output_json_path} ({cleaned_count} elements)")
    return


if __name__ == "__main__":
    json_partitioned = "inputs/file_example-partitioned"
    json_cleaned = "inputs/file_example-partitioned-cleaned"
    cleaning(json_partitioned, json_cleaned)
