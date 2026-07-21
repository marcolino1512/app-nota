"""
Localiza a chave de acesso da NF-e (44 dígitos) dentro de um texto.

A chave de acesso pode aparecer:
- Já grudada, sem espaços: 12345678901234567890123456789012345678901234
- Separada em blocos de 4 dígitos: 1234 5678 9012 3456 7890 1234 5678 9012 3456 7890 1234
- Com outros caracteres de formatação (pontos, hífens) em alguns extratos de OCR ruim
"""

import re

# Aceita blocos de dígitos separados por espaço, ponto, hífen ou nada,
# desde que o total de dígitos "limpos" dê exatamente 44.
_CANDIDATE_PATTERN = re.compile(r"[\d][\d\s.\-]{42,80}[\d]")


def extrair_chave_acesso(texto: str) -> str | None:
    """
    Recebe o texto bruto extraído de um PDF/imagem e retorna a chave de
    acesso com exatamente 44 dígitos, sem espaços. Retorna None se não
    encontrar nenhuma sequência válida.
    """
    if not texto:
        return None

    for match in _CANDIDATE_PATTERN.finditer(texto):
        somente_digitos = re.sub(r"\D", "", match.group())
        if len(somente_digitos) == 44:
            return somente_digitos

    # Fallback: procura direto por 44 dígitos consecutivos sem nenhuma
    # formatação (caso mais comum em PDFs de texto puro). Os "(?<!\d)"
    # e "(?!\d)" garantem que não é um pedaço de um número MAIOR (como
    # o Identificador Nacional de 50+ dígitos de uma NFS-e).
    match_direto = re.search(r"(?<!\d)\d{44}(?!\d)", re.sub(r"\s", "", texto))
    if match_direto:
        return match_direto.group()

    return None
