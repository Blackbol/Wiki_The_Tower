#!/bin/bash

# Vérifie que le fichier est passé en argument
if [ $# -ne 1 ]; then
    echo "Usage: $0 fichier"
    exit 1
fi

fichier="$1"

# Utilise awk pour supprimer les doublons, puis grep pour extraire les href
awk '!seen[$0]++' "$fichier" | grep -oP 'href="[^"]+"' | sed -E 's/href="([^"]+)"/\1/' | sort -u
