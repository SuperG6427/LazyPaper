#!/bin/bash
# LazyPaper Launcher - Linux / macOS
cd "$(dirname "$0")" || exit
# Verificar directorio correcto
if [ ! -d "lazypaper" ] || [ ! -f "lazypaper/lazypaper.py" ]; then
    echo "Error: Estructura de proyecto incorrecta."
    echo "Debe existir: lazypaper/lazypaper.py"
    exit 1
fi
# Activar o crear entorno virtual
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "Entorno virtual no encontrado. Creando..."
        python3 -m venv venv
        source venv/bin/activate
        echo "Instalando dependencias..."
        pip install -r requirements.txt
    fi
    else
    echo "Ya tiene entorno virtual: $VIRTUAL_ENV"
fi
# Ejecutar directamente
cd lazypaper
python3 lazypaper.py
cd ..
read -p "Presiona Enter para cerrar..."
deactivate
# --- IGNORE ---