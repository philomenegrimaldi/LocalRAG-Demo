import os
import pdfplumber


def vider_dossier(dossier):
    if not os.path.exists(dossier):
        print("❌ Le dossier n'existe pas.")
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
            print(f"❌ Erreur en supprimant {file_path} : {e}")
    print(f"[OK] {i} fichiers supprimés")


def extract_plumber(input_folder,output_folder):


    os.makedirs(output_folder, exist_ok=True)
    vider_dossier(output_folder)
    i=0
    j=0

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
                    # print(f"  Aucun tableau détecté dans {filename}")
                    j+=1
                    continue

                # Préparer le contenu à sauvegarder
                lines = []
                for row in table:
                    line = " | ".join(cell or "" for cell in row)
                    lines.append(line)
                content = "\n".join(lines)

                # Sauvegarder dans un fichier texte
                output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.txt")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)

                # print(f"  Tableau extrait et sauvegardé dans {output_path}")
                i+=1

        except Exception as e:
            print(f"  Erreur avec {filename} : {e}")
    print(f"Extraction plumber terminée : {i} tableaux extraits ; {j} documents ne possèdent pas de tableaux.")






if __name__ == "__main__":
    input_folder = f"inputs\extracts\pdf"
    output_folder = f"inputs\extracts\plumber"
    extract_plumber(input_folder,output_folder)
    

