# AutoPiano en Debian y Ubuntu

La version Linux esta en `autopiano.py`. El archivo original `autopiano` sigue siendo la version AutoHotkey para Windows.

## Instalacion

En Debian o Ubuntu:

```bash
sudo apt update
sudo apt install python3 python3-tk python3-venv
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

## Ejecucion

```bash
. .venv/bin/activate
python autopiano.py
```

Selecciona la ventana donde deben sonar las teclas y usa F8 para iniciar. F6 pausa, F7 detiene y F5 activa o desactiva el bucle.

`pyautogui` necesita una sesion grafica X11 para enviar teclas a otra ventana. En Ubuntu con Wayland, inicia sesion con **Ubuntu on Xorg** si las teclas no llegan al juego.

## Crear paquetes

Para generar los dos formatos:

```bash
sudo apt install python3-tk python3-venv curl
chmod +x packaging/build-packages.sh
packaging/build-packages.sh
```

Los archivos apareceran en `dist-packages/`:

```bash
sudo apt install ./dist-packages/autopiano_2.0.3_amd64.deb
chmod +x dist-packages/AutoPiano-2.0.3-x86_64.AppImage
./dist-packages/AutoPiano-2.0.3-x86_64.AppImage
```

El `.deb` instala la aplicacion en el menu grafico. El `AppImage` es autocontenido y no necesita instalar Python ni las dependencias del proyecto.
sudo apt install python3 python3-tk python3-venv
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python autopiano.py