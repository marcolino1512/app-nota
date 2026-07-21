"""
Extração de texto de arquivos PDF "digitais" (não escaneados).
Usa pdfplumber, que costuma dar melhores resultados que PyPDF2 para
DANFEs (o layout de tabela do PDF às vezes atrapalha a ordem do texto,
mas para achar 44 dígitos seguidos isso raramente é um problema).
"""

import pdfplumber


def extrair_texto_pdf(caminho_arquivo: str) -> str:
    """Retorna todo o texto encontrado nas páginas do PDF, concatenado."""
    texto_completo = []
    with pdfplumber.open(caminho_arquivo) as pdf:
        for pagina in pdf.pages:
            texto_pagina = pagina.extract_text() or ""
            texto_completo.append(texto_pagina)
    return "\n".join(texto_completo)
