#!/bin/bash

# Vérifier si mutool est installé
if ! command -v mutool &> /dev/null; then
    echo "Erreur : mutool n'est pas installé. Installez-le avec 'sudo apt install mupdf-tools' (Debian/Ubuntu) ou 'brew install mupdf' (Mac)."
    exit 1
fi

# Vérifier si un dossier est fourni en argument
if [ -z "$1" ]; then
    echo "Utilisation : $0 <dossier>"
    exit 1
fi

# Vérifier si le dossier existe
if [ ! -d "$1" ]; then
    echo "Erreur : le dossier '$1' n'existe pas."
    exit 1
fi

# Parcourir tous les fichiers PDF du dossier
for pdf in "$1"/*.pdf; do
    # Vérifier si des fichiers PDF existent
    [ -e "$pdf" ] || continue

    # Nom de sortie avec .txt au lieu de .pdf
    txt_file="${pdf%.pdf}.txt"

    echo "Conversion de '$pdf' → '$txt_file'..."
    
    # Exécuter mutool pour extraire le texte
    mutool draw -F txt -o "$txt_file" "$pdf"

    if [ $? -eq 0 ]; then
        echo "✅ Conversion réussie : '$txt_file'"
    else
        echo "❌ Échec de la conversion : '$pdf'"
    fi
done

echo "🎉 Conversion terminée !"
