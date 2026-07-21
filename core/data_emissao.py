"""
Localiza a data de emissão dentro do texto extraído de um PDF/imagem
de nota fiscal.

Estratégia:
1. Procura primeiro uma data (DD/MM/AAAA) que apareça logo perto da
   palavra "emissão" (é o caso mais confiável, evita confundir com
   "data de saída" ou outras datas do documento).
2. Se não achar nada perto de "emissão", cai para a primeira data no
   formato DD/MM/AAAA encontrada em qualquer lugar do texto.
"""

import re

_PADRAO_DATA = re.compile(r"\d{2}/\d{2}/\d{4}")

# Aceita "emissão", "emissao" (sem acento, comum em OCR) e alguma
# distância curta de outros caracteres/rótulo antes da data.
_PADRAO_EMISSAO = re.compile(
    r"emiss[aã]o\D{0,25}(\d{2}/\d{2}/\d{4})", re.IGNORECASE
)


def extrair_data_emissao(texto: str) -> str | None:
    """Retorna a data de emissão no formato DD/MM/AAAA, ou None se não achar."""
    if not texto:
        return None

    match_proximo = _PADRAO_EMISSAO.search(texto)
    if match_proximo:
        return match_proximo.group(1)

    match_generico = _PADRAO_DATA.search(texto)
    if match_generico:
        return match_generico.group()

    return None
