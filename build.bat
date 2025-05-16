pyinstaller ^
    --noconfirm ^
    --paths="." ^
    --paths="lib/" ^
    --hidden-import=clr ^
    --add-binary="lib/*;lib" ^
    .\eoi.py