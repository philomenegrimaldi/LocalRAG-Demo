import json
import os
from collections import defaultdict


def load_table(element_id, folder):
    """Load the content of a table file by element_id."""
    path = os.path.join(folder, f"{element_id}.txt")
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"[ERROR] Failed to read {path}: {e}")
            return "[Error loading table]"
    return "[Table missing]"


def is_title(element):
    """Check if an element is a title."""
    return element.get("type") == "Title"


def reconstruct_document(plumber_folder, fitz_folder, json_path):
    """Reconstruct a full document from elements and associated tables."""
    json_path += ".json"

    with open(json_path, 'r', encoding='utf-8') as f:
        elements = json.load(f)

    final_text = []
    processed_ids = set()

    # Index children by parent
    children_by_parent = defaultdict(list)
    for el in elements:
        parent_id = el.get("metadata", {}).get("parent_id")
        if parent_id:
            children_by_parent[parent_id].append(el)

    separator_added = False  # Prevent repeating separators

    for el in elements:
        element_id = el["element_id"]
        if element_id in processed_ids:
            continue

        block_type = el.get("type")
        text = el.get("text", "")
        parent_id = el.get("metadata", {}).get("parent_id")

        # Case: title
        if is_title(el):
            if not separator_added:
                final_text.append("-------------------------------------------------------------")
                separator_added = True

            final_text.append(text)
            final_text.append("")

            # If the title has child tables → add them
            for child in children_by_parent.get(element_id, []):
                if child.get("type") == "Table":
                    plumber_content = load_table(child["element_id"], plumber_folder)
                    final_text.append(f"Table {child['element_id']} (plumber version):\n{plumber_content}\n")
                    fitz_content = load_table(child["element_id"], fitz_folder)
                    final_text.append(f"Table {child['element_id']} (fitz version):\n{fitz_content}\n")
                    final_text.append(f"End of Table {child['element_id']} (fitz version)")
                    final_text.append("-------------------------------------------------------------")
                    separator_added = False
                    processed_ids.add(child["element_id"])

            processed_ids.add(element_id)

        # Case: other non-table elements
        elif block_type != "Table":
            separator_added = False
            if text.strip():
                final_text.append(text)
                final_text.append("")
            for child in children_by_parent.get(element_id, []):
                if child["element_id"] in processed_ids:
                    continue
                if child.get("type") == "Table":
                    final_text.append("-------------------------------------------------------------")
                    plumber_content = load_table(child["element_id"], plumber_folder)
                    final_text.append(f"Table {child['element_id']} (plumber version):\n{plumber_content}\n")
                    fitz_content = load_table(child["element_id"], fitz_folder)
                    final_text.append(f"Table {child['element_id']} (fitz version):\n{fitz_content}\n")
                    final_text.append(f"End of Table {child['element_id']} (fitz version)")
                    final_text.append("-------------------------------------------------------------")
                else:
                    if child.get("text", "").strip():
                        final_text.append(child["text"])
                final_text.append("")
                processed_ids.add(child["element_id"])
            processed_ids.add(element_id)

        # Case: standalone table
        elif block_type == "Table" and not parent_id:
            separator_added = False
            final_text.append("-------------------------------------------------------------")
            plumber_content = load_table(element_id, plumber_folder)
            final_text.append(f"Table {element_id} (plumber version):\n{plumber_content}\n")
            fitz_content = load_table(element_id, fitz_folder)
            final_text.append(f"Table {element_id} (fitz version):\n{fitz_content}\n")
            final_text.append(f"End of Table {element_id} (fitz version)")
            final_text.append("-------------------------------------------------------------")
            final_text.append("")
            processed_ids.add(element_id)

    # Save final reconstructed document
    with open("inputs/file-reconstituted.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(final_text))

    print("[OK] Reconstruction complete. Consecutive titles have been grouped.")


if __name__ == "__main__":
    plumber_folder = "inputs/extracts/plumber"
    fitz_folder = "inputs/extracts/fitz"
    json_file = "inputs/file_example-partitioned-cleaned"

    reconstruct_document(plumber_folder, fitz_folder, json_file)
