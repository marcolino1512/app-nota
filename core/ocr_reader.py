"""
Extração de texto via OCR, usada para:
- Imagens (jpg, jpeg, png)
- PDFs escaneados (sem texto digital dentro)

Usa automaticamente o Tesseract e o Poppler empacotados na pasta bin/
do projeto (veja core/bin_locator.py e o README.md). Se não encontrar
nada empacotado, cai de volta para uma instalação do sistema (PATH),
caso exista.
"""

from PIL import Image
import pytesseract

from core.bin_locator import caminho_tesseract_exe, caminho_poppler_bin

_tesseract_empacotado = caminho_tesseract_exe()
if _tesseract_empacotado:
    pytesseract.pytesseract.tesseract_cmd = _tesseract_empacotado


def extrair_texto_imagem(caminho_arquivo: str) -> str:
    """Roda OCR em um arquivo de imagem (jpg/jpeg/png) e retorna o texto."""
    imagem = Image.open(caminho_arquivo)
    return pytesseract.image_to_string(imagem, lang="por")


def extrair_texto_pdf_escaneado(caminho_arquivo: str) -> str:
    """
    Converte cada página do PDF em imagem e roda OCR.
    Usa o Poppler empacotado em bin/poppler, se disponível.
    """
    from pdf2image import convert_from_path

    paginas = convert_from_path(
        caminho_arquivo, poppler_path=caminho_poppler_bin()
    )
    texto_completo = []
    for pagina in paginas:
        texto_completo.append(pytesseract.image_to_string(pagina, lang="por"))
    return "\n".join(texto_completo)
