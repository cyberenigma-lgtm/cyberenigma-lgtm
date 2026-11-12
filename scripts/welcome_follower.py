#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 NOXFERION FOLLOWER WELCOME BOT (BILINGUAL ES / EN)
Automatically detects new followers of cyberenigma-lgtm and thanks them in README.md.
"""

import json
import os
import re
import urllib.request
from pathlib import Path

USERNAME = "cyberenigma-lgtm"
API_URL = f"https://api.github.com/users/{USERNAME}/followers?per_page=100"

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_DIR / "followers.json"
README_FILE = REPO_DIR / "README.md"

def get_followers():
    try:
        headers = {"User-Agent": "GitHub-Action-Follower-Bot"}
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"token {token}"
            
        req = urllib.request.Request(API_URL, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            return [user["login"] for user in data if isinstance(user, dict) and "login" in user]
    except Exception as e:
        print(f"Error al obtener seguidores de la API: {e}")
        return []

def main():
    current_followers = get_followers()
    if not current_followers:
        print("No se pudieron obtener seguidores o la lista está vacía.")
        return

    # Cargar lista anterior si existe
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                saved_followers = json.load(f)
        except Exception:
            saved_followers = []
    else:
        saved_followers = []

    # Detectar nuevos seguidores
    new_followers = [u for u in current_followers if u not in saved_followers]

    # Si no hay nuevos y ya existía historial previo, no hacemos cambios
    if not new_followers and DATA_FILE.exists():
        print("No hay seguidores nuevos / No new followers.")
        return

    # Tomar el seguidor más reciente
    latest_user = new_followers[-1] if new_followers else current_followers[-1]
    profile_url = f"https://github.com/{latest_user}"
    avatar_url = f"https://github.com/{latest_user}.png?size=64"

    # Guardar lista actualizada en followers.json
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(current_followers, f, indent=2, ensure_ascii=False)

    # Leer el README actual
    if not README_FILE.exists():
        print("README.md no encontrado.")
        return

    with open(README_FILE, "r", encoding="utf-8") as f:
        readme_content = f.read()

    # Mensaje bilingüe con estilo de diseño Noxferion
    new_message = (
        f"<!-- START_FOLLOWER -->\n"
        f'<div align="center">\n\n'
        f'> <img src="{avatar_url}" width="32" height="32" style="border-radius: 50%; vertical-align: middle;"/> '
        f'🇪🇸 **¡Gracias por seguirme, [@{latest_user}]({profile_url})!** 🤝<br>\n'
        f'> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
        f'🇬🇧 **Thank you for following me, [@{latest_user}]({profile_url})!** 🤝\n\n'
        f'</div>\n'
        f"<!-- END_FOLLOWER -->"
    )

    pattern = r"<!-- START_FOLLOWER -->.*?<!-- END_FOLLOWER -->"
    if re.search(pattern, readme_content, flags=re.DOTALL):
        updated_readme = re.sub(pattern, new_message, readme_content, flags=re.DOTALL)
        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(updated_readme)
        print(f"README actualizado con éxito. Último seguidor: {latest_user}")
    else:
        print("Marcadores <!-- START_FOLLOWER --> no encontrados en README.md")

if __name__ == "__main__":
    main()
