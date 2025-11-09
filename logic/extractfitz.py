import os
import fitz  # PyMuPDF

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



def extract_fitz(input_folder,output_folder):  

    os.makedirs(output_folder, exist_ok=True)
    vider_dossier(output_folder)
    j=0
    i=0

    for filename in os.listdir(input_folder):
        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(input_folder, filename)
        
        try:
            doc = fitz.open(pdf_path)
            page = doc[0]  # première page
            content_text = page.get_text("text").strip()

            output_name = os.path.splitext(filename)[0] + ".txt"
            output_path = os.path.join(output_folder, output_name)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content_text)

            # print(f"✅ Texte brut sauvegardé → {output_path}")
            i+=1

        except Exception as e:
            # print(f"❌ Erreur avec {filename} : {e}")
            j+=1
    print(f"[OK] Extraction fitz terminée. Extraits: {i} ; Erreurs: {j}")



if __name__ == "__main__":
    input_folder = f"inputs\extracts\pdf"
    output_folder = f"inputs/extracts/fitz"
    extract_fitz(input_folder,output_folder)
    

