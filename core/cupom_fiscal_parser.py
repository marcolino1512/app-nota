"""
Trata o caso de CUPOM FISCAL (nota simplificada, geralmente emitida por
impressora fiscal/PDV, sem o padrão de chave de acesso da NF-e nem o
Identificador Nacional da NFS-e).

IMPORTANTE: como ainda não tivemos um cupom fiscal real pra testar (ao
contrário da NF-e e da NFS-e, que já validamos com documentos reais),
os rótulos abaixo foram escolhidos com base nos nomes mais comuns
usados em cupons fiscais/NFC-e/SAT. Pode ser necessário ajustar assim
que você tiver um cupom de verdade pra testar - me manda um exemplo
(ou um print) que a gente refina os padrões junto.

Regra combinada com você:
- Série do cupom = sempre "C"
- Número = o número do cupom, se encontrado por algum dos rótulos abaixo
- Chave/Identificador = algum código de autenticação/chave, se encontrado
  (bem comum em SAT/NFC-e ter um código desses); em branco se não achar
"""

import re
from dataclasses import dataclass

MARCADOR_CUPOM = "C"

# Rótulos mais comuns para o número do cupom fiscal, em ordem de
# prioridade. Cada um vem com um pequeno trecho até o número.
_PADROES_NUMERO = [
    re.compile(r"cupom\s+fiscal\s*n[ºo°]?\s*[:\-]?\s*(\d{1,9})", re.IGNORECASE),
    re.compile(r"n[úu]mero\s+do\s+cupom\s*[:\-]?\s*(\d{1,9})", re.IGNORECASE),
    re.compile(r"\bcoo\b\s*[:\-]?\s*(\d{1,9})", re.IGNORECASE),
    re.compile(r"\bccf\b\s*[:\-]?\s*(\d{1,9})", re.IGNORECASE),
    re.compile(r"extrato\s+n[ºo°]?\s*[:\-]?\s*(\d{1,9})", re.IGNORECASE),
]

# Rótulos comuns pra um código de autenticação/chave, quando existir
# (varia bastante - alguns cupons trazem, outros não trazem nada disso).
_PADROES_CHAVE = [
    re.compile(r"c[óo]digo\s+de\s+autentica[cç][aã]o\s*[:\-]?\s*([A-Za-z0-9]{10,60})", re.IGNORECASE),
    re.compile(r"chave\s+de\s+acesso\s*[:\-]?\s*([\d\s]{30,80}?\d)", re.IGNORECASE),
]


@dataclass
class DadosCupomFiscal:
    identificador: str  # pode vir em branco, se não achar nenhum código
    numero: str  # número do cupom, ou "" se não encontrado


def eh_cupom_fiscal(texto: str) -> bool:
    """Indica se o texto parece ser de um cupom fiscal."""
    if not texto:
        return False
    return "cupom fiscal" in texto.lower()


def _tentar_padroes(texto: str, padroes: list[re.Pattern]) -> str | None:
    for padrao in padroes:
        match = padrao.search(texto)
        if match:
            valor = match.group(1).strip()
            if valor:
                return valor
    return None


def processar_cupom_fiscal(texto: str) -> DadosCupomFiscal:
    """Recebe o texto já extraído (OCR) do cupom e devolve número e identificador, se achar."""
    numero = _tentar_padroes(texto, _PADROES_NUMERO) or ""

    identificador_bruto = _tentar_padroes(texto, _PADROES_CHAVE) or ""
    identificador = re.sub(r"\s", "", identificador_bruto)

    return DadosCupomFiscal(identificador=identificador, numero=numero)
