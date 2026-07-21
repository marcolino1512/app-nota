"""
Decompõe a chave de acesso de 44 dígitos da NF-e em seus campos.

Estrutura oficial da chave (sempre 44 dígitos, nesta ordem):

    cUF (2) + AAMM (4) + CNPJ (14) + mod (2) + serie (3) + nNF (9)
    + tpEmis (1) + cNF (8) + cDV (1)

Fonte: Manual de Orientação do Contribuinte da NF-e (SEFAZ).
"""

from dataclasses import dataclass


@dataclass
class DadosChaveNFe:
    chave: str
    uf_codigo: str
    ano_mes_emissao: str  # formato AAMM
    cnpj_emitente: str
    modelo: str
    serie: str
    numero: str
    tipo_emissao: str
    codigo_numerico: str
    digito_verificador: str


def decompor_chave(chave: str) -> DadosChaveNFe | None:
    """Recebe a chave de 44 dígitos (sem espaços) e devolve seus campos."""
    if not chave or len(chave) != 44 or not chave.isdigit():
        return None

    return DadosChaveNFe(
        chave=chave,
        uf_codigo=chave[0:2],
        ano_mes_emissao=chave[2:6],
        cnpj_emitente=chave[6:20],
        modelo=chave[20:22],
        serie=str(int(chave[22:25])),  # remove zeros à esquerda (ex: "001" -> "1")
        numero=str(int(chave[25:34])),  # remove zeros à esquerda
        tipo_emissao=chave[34:35],
        codigo_numerico=chave[35:43],
        digito_verificador=chave[43:44],
    )
