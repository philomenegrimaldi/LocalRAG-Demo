import os, tempfile

# Crée un dossier temporaire propre
temp_dir = os.path.join(os.getcwd(), "tmp_ocr")
os.makedirs(temp_dir, exist_ok=True)

# Force pytesseract / unstructured à l'utiliser
os.environ["TMPDIR"] = temp_dir
os.environ["TEMP"] = temp_dir
os.environ["TMP"] = temp_dir

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\grima\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Users\grima\AppData\Local\Programs\Tesseract-OCR\tessdata"

from unstructured.partition.pdf import partition_pdf
from unstructured.staging.base import elements_to_json

onnx_dll_path = os.path.join(os.getcwd(), ".venv", "Lib", "site-packages", "onnxruntime")
os.environ["PATH"] = onnx_dll_path + ";" + os.environ["PATH"]


def partitioning(pdf_path, json_partitioned):
    print("[INFO] Début partition")

    elements = partition_pdf(
        filename=pdf_path + ".pdf",
        strategy="hi_res",  # “auto”, “fast”, “hi_res”, “ocr_only”
        extract_images_in_pdf=False,
        languages=["eng"],
        extract_image_block_to_payload=False,
        infer_table_structure=True,
        skip_infer_table_types=False
    )

    elements_to_json(elements=elements, filename=f"{json_partitioned}.json")

    print("[OK] Partition finished")


if __name__ == "__main__":
    pdf_path="inputs/file_example"
    json_partitioned = f"{pdf_path}-partitioned"
    partitioning(pdf_path, json_partitioned)
