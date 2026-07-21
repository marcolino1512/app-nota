"""
Trata o caso de notas de PRESTAÇÃO DE SERVIÇO (NFS-e), que não seguem o
padrão de chave de acesso de 44 dígitos da NF-e de produto. Em vez
disso, costumam ter um "Identificador Nacional" (uma sequência longa
de dígitos, formato e tamanho variam por município).

Estratégia para achar o número da nota sem depender do rótulo exato
"Número da Nota" (o OCR nem sempre lê esse rótulo direito, já que ele
costuma ficar dentro de uma caixa isolada no canto do documento):

1. Localiza o Identificador Nacional pelo rótulo (esse rótulo é lido
   de forma mais confiável pelo OCR, por vir em texto corrido).
2. Lista todos os números "soltos" do texto (isolados, não colados em
   outros dígitos - exclui automaticamente pedaços de CNPJ, que vêm
   sempre com pontuação no meio).
3. Verifica qual desses números aparece como subsequência dentro do
   Identificador Nacional - já que ele é formado concatenando vários
   campos da nota (código do município, inscrição, número da nota
   etc), o número da nota aparece embutido nele.
4. O primeiro número que bater é considerado o número da nota.
"""

import re
from dataclasses import dataclass

_PADRAO_IDENTIFICADOR = re.compile(
    r"identificador\s+nacional\s*[:\-]?\s*([\d\s]{30,80})", re.IGNORECASE
)

# Números soltos no texto, com 5 a 9 dígitos (faixa comum para número de
# nota fiscal). Os "(?<!\d)" e "(?!\d)" garantem que não é um pedaço de
# uma sequência maior colada (como o próprio Identificador Nacional).
_PADRAO_NUMERO_SOLTO = re.compile(r"(?<!\d)\d{5,9}(?!\d)")

MARCADOR_SERVICO = "S"


@dataclass
class DadosNFSe:
    identificador: str
    numero: str  # número real encontrado, ou "S" se não confirmado


def eh_nota_de_servico(texto: str) -> bool:
    """Indica se o texto parece ser de uma NFS-e (nota de serviço)."""
    if not texto:
        return False
    texto_lower = texto.lower()
    return "nfs-e" in texto_lower or "identificador nacional" in texto_lower


def _extrair_identificador(texto: str) -> str | None:
    match = _PADRAO_IDENTIFICADOR.search(texto)
    if not match:
        return None
    digitos = re.sub(r"\D", "", match.group(1))
    return digitos if digitos else None


def _extrair_numero_confirmado(texto: str, identificador: str) -> str | None:
    """Procura, entre os números soltos do texto, um que esteja embutido no identificador."""
    candidatos = _PADRAO_NUMERO_SOLTO.findall(texto)
    for candidato in candidatos:
        if candidato and candidato in identificador:
            return candidato
    return None


def processar_nota_servico(texto: str) -> DadosNFSe:
    """
    Recebe o texto já extraído (OCR ou PDF) de uma nota de serviço e
    devolve o identificador nacional (se achar) e o número confirmado
    (ou "S" se não conseguir confirmar nenhum).
    """
    identificador = _extrair_identificador(texto) or ""

    numero = None
    if identificador:
        numero = _extrair_numero_confirmado(texto, identificador)

    return DadosNFSe(
        identificador=identificador,
        numero=numero or MARCADOR_SERVICO,
    )
