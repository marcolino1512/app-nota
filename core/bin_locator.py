"""
Localiza os binários externos (Poppler e Tesseract) que ficam dentro da
pasta bin/, junto do app - assim o usuário não precisa instalar nada
manualmente nem mexer no PATH do Windows.

Estrutura esperada:

    leitor_chave_nfe/
    ├── main.py
    ├── bin/
    │   ├── poppler/         <- extraia o zip do Poppler aqui dentro
    │   │   └── ... /bin/pdftoppm.exe   (em qualquer nível de subpasta)
    │   └── tesseract/       <- copie a pasta "Tesseract-OCR" instalada aqui
    │       └── tesseract.exe

Funciona tanto rodando com "python main.py" quanto já empacotado em
.exe pelo PyInstaller (desde que a pasta bin/ seja distribuída ao lado
do .exe final - veja o README.md).
"""

import os
import sys
from functools import lru_cache


def _pastas_candidatas() -> list[str]:
    """
    Lugares onde a pasta bin/ pode estar, na ordem em que devem ser
    verificados:
    - Rodando com "python main.py": ao lado do main.py
    - .exe gerado com --onefile e --add-data "bin;bin": dentro da pasta
      temporária que o PyInstaller usa em tempo de execução (_MEIPASS)
    - .exe gerado sem --add-data (ou modo --onedir): na pasta onde o
      .exe realmente está
    """
    candidatas = []
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidatas.append(meipass)
        candidatas.append(os.path.dirname(sys.executable))
    else:
        candidatas.append(
            os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
        )
    return candidatas


def _procurar_arquivo(nome_arquivo: str, subpasta: str) -> str | None:
    """Procura recursivamente por um arquivo (ex: pdftoppm.exe) dentro de bin/<subpasta>."""
    for base in _pastas_candidatas():
        pasta_raiz = os.path.join(base, "bin", subpasta)
        if not os.path.isdir(pasta_raiz):
            continue
        for raiz, _dirs, arquivos in os.walk(pasta_raiz):
            if nome_arquivo in arquivos:
                return os.path.join(raiz, nome_arquivo)
    return None


@lru_cache(maxsize=1)
def caminho_poppler_bin() -> str | None:
    """
    Retorna a pasta que contém os .exe do Poppler (pdftoppm.exe etc),
    ou None se não encontrar - nesse caso, o pdf2image tenta usar o
    Poppler do PATH do sistema, se houver algum instalado.
    """
    caminho_exe = _procurar_arquivo("pdftoppm.exe", "poppler")
    return os.path.dirname(caminho_exe) if caminho_exe else None


@lru_cache(maxsize=1)
def caminho_tesseract_exe() -> str | None:
    """
    Retorna o caminho completo do tesseract.exe empacotado, ou None se
    não encontrar - nesse caso, o pytesseract tenta usar o Tesseract do
    PATH do sistema, se houver algum instalado.
    """
    return _procurar_arquivo("tesseract.exe", "tesseract")
