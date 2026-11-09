#!/usr/bin/env bash
# Empacota apenas os arquivos e assets necessários em runtime para o Pyxel Web (.pyxapp e .html),
# evitando incluir venv/, __pycache__/ ou builds anteriores.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYXEL_BIN="${ROOT_DIR}/app/venv/bin/pyxel"
if [[ ! -x "${PYXEL_BIN}" ]]; then
    PYXEL_BIN="pyxel"
fi

STAGE_DIR="$(mktemp -d)"
trap 'rm -rf "${STAGE_DIR}"' EXIT

APP_STAGE="${STAGE_DIR}/app"
mkdir -p "${APP_STAGE}/assets/CharacterIdeas" \
         "${APP_STAGE}/assets/BackGround/city1" \
         "${APP_STAGE}/assets/Audio/SoundTrack"

# 1. Módulos Python de runtime e recursos Pyxel
for pyfile in "${ROOT_DIR}"/app/*.py; do
    base="$(basename "${pyfile}")"
    if [[ "${base}" != "preview_character_concepts.py" ]]; then
        cp "${pyfile}" "${APP_STAGE}/"
    fi
done
cp "${ROOT_DIR}/app/resources.pyxres" "${APP_STAGE}/"

# 2. Spritesheets de runtime do Sir Mop
cp "${ROOT_DIR}/app/assets/CharacterIdeas/character_trenchcoat_sheet.png" "${APP_STAGE}/assets/CharacterIdeas/"
cp "${ROOT_DIR}/app/assets/CharacterIdeas/character_rope_swing_sheet.png" "${APP_STAGE}/assets/CharacterIdeas/"
cp "${ROOT_DIR}/app/assets/CharacterIdeas/character_actions_sheet.png" "${APP_STAGE}/assets/CharacterIdeas/"

# 3. Fundos de runtime (menu e paralaxe do gameplay)
cp "${ROOT_DIR}/assets/BackGround/city1/1.png" "${APP_STAGE}/assets/BackGround/city1/"
cp "${ROOT_DIR}/assets/BackGround/city1/bg_left.png" "${APP_STAGE}/assets/BackGround/city1/"
cp "${ROOT_DIR}/assets/BackGround/city1/bg_right.png" "${APP_STAGE}/assets/BackGround/city1/"

# 4. Faixas de áudio OGG otimizadas de runtime
cp "${ROOT_DIR}"/assets/Audio/SoundTrack/*.ogg "${APP_STAGE}/assets/Audio/SoundTrack/"

# 5. Gera .pyxapp e .html em dist/
mkdir -p "${ROOT_DIR}/dist"
(
    cd "${STAGE_DIR}"
    "${PYXEL_BIN}" package "${APP_STAGE}" "${APP_STAGE}/main.py"
    "${PYXEL_BIN}" app2html "${STAGE_DIR}/app.pyxapp"
    mv "${STAGE_DIR}/app.pyxapp" "${ROOT_DIR}/dist/app.pyxapp"
    mv "${STAGE_DIR}/app.html" "${ROOT_DIR}/dist/app.html"
)

echo "Build Web concluído em dist/:"
ls -lh "${ROOT_DIR}/dist/app.pyxapp" "${ROOT_DIR}/dist/app.html"
