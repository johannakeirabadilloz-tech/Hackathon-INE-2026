#!/usr/bin/env bash
# Reproduce todo el análisis. Uso: bash scripts/run_all.sh   (desde la raíz)
set -euo pipefail
[ -d .venv ] || { python3 -m venv .venv; .venv/bin/pip install -q pandas numpy scipy scikit-learn statsmodels matplotlib pyarrow nbformat nbconvert ipykernel; }
cd scripts
for s in 01_etl_calidad 02_cubo 03_eda 04_agrupamiento 04b_graficas_agrupamiento 05_modelo 06_territorio 07_graficas_modelo_territorio 08_notebook; do
  echo "== $s"; ../.venv/bin/python $s.py
done
