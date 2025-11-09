import json
import os
from collections import defaultdict

def charger_table(element_id, dossier):
    chemin = f"{dossier}/{element_id}.txt"
    if os.path.exists(chemin):
        try:
            with open(chemin, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"[ERREUR] Lecture {chemin}: {e}")
            return "[Erreur de chargement de la table]"
    return "[Table manquante]"

def est_titre(el):
    return el.get("type") == "Title"

def reconstituer_document(dossier_plumber,dossier_fitz, json_path):
    json_path += ".json"


    with open(json_path, 'r', encoding='utf-8') as f:
        elements = json.load(f)

    texte_final = []
    deja_traite = set()

    # Indexation des enfants par parent
    enfants_par_parent = defaultdict(list)
    for el in elements:
        parent_id = el.get("metadata", {}).get("parent_id")
        if parent_id:
            enfants_par_parent[parent_id].append(el)

    separateur_ajoute = False  # ✅ pour éviter de répéter les délimiteurs

    for i, el in enumerate(elements):
        element_id = el["element_id"]
        if element_id in deja_traite:
            continue

        type_bloc = el.get("type")
        texte = el.get("text", "")
        parent_id = el.get("metadata", {}).get("parent_id")

        # Cas : titre
        if est_titre(el):
            if not separateur_ajoute:
                texte_final.append("-------------------------------------------------------------")
                separateur_ajoute = True

            texte_final.append(texte)
            texte_final.append("")

            # Si le titre a un tableau enfant → traitement
            for enfant in enfants_par_parent.get(element_id, []):
                if enfant.get("type") == "Table":
                    contenu_plumber = charger_table(enfant["element_id"], dossier_plumber)
                    texte_final.append(f"Tableau {enfant['element_id']} (version plumber) :\n{contenu_plumber}\n")
                    contenu_fitz = charger_table(enfant["element_id"], dossier_fitz)
                    texte_final.append(f"Tableau {enfant['element_id']} (version fitz) :\n{contenu_fitz}\n")
                    texte_final.append(f"Fin tableau {enfant['element_id']} (version fitz) :")
                    texte_final.append("-------------------------------------------------------------")
                    separateur_ajoute = False
                    deja_traite.add(enfant["element_id"])

            deja_traite.add(element_id)

        # Cas : autre élément non tableau
        elif type_bloc != "Table":
            separateur_ajoute = False
            if texte.strip():
                texte_final.append(texte)
                texte_final.append("")
            for enfant in enfants_par_parent.get(element_id, []):
                if enfant["element_id"] in deja_traite:
                    continue
                if enfant.get("type") == "Table":
                    texte_final.append("-------------------------------------------------------------")
                    contenu_plumber = charger_table(enfant["element_id"], dossier_plumber)
                    texte_final.append(f"Tableau {enfant['element_id']} (version plumber) :\n{contenu_plumber}\n")
                    contenu_fitz = charger_table(enfant["element_id"], dossier_fitz)
                    texte_final.append(f"Tableau {enfant['element_id']} (version fitz) :\n{contenu_fitz}\n")
                    texte_final.append(f"Fin tableau {enfant['element_id']} (version fitz) :")
                    texte_final.append("-------------------------------------------------------------")
                else:
                    if enfant.get("text", "").strip():
                        texte_final.append(enfant["text"])
                texte_final.append("")
                deja_traite.add(enfant["element_id"])
            deja_traite.add(element_id)

        # Cas : tableau seul
        elif type_bloc == "Table" and not parent_id:
            separateur_ajoute = False
            texte_final.append("-------------------------------------------------------------")
            contenu_plumber = charger_table(element_id, dossier_plumber)
            texte_final.append(f"Tableau {element_id} (version plumber) :\n{contenu_plumber}\n")
            contenu_fitz = charger_table(element_id, dossier_fitz)
            texte_final.append(f"Tableau {element_id} (version fitz) :\n{contenu_fitz}\n")
            texte_final.append(f"Fin tableau {element_id} (version fitz)")
            texte_final.append("-------------------------------------------------------------")
            texte_final.append("")
            deja_traite.add(element_id)

    # Sauvegarde finale
    with open(f"inputs/file-reconstitue.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(texte_final))

    print("[OK] Reconstitution terminée. Titres consécutifs regroupés.")




if __name__ == "__main__":
    dossier_plumber = f"inputs\extracts\plumber"
    dossier_fitz = f"inputs\extracts/fitz"
    chemin_json = "inputs/file_example-partioned-cleaned"
   

    reconstituer_document(dossier_plumber,dossier_fitz,chemin_json)
