"""
Ponto único de entrada: recebe o caminho de um arquivo (PDF ou imagem) e
devolve os dados da nota (chave/identificador, série, número e data de
emissão).

Duas famílias de nota são tratadas:

- NF-e de produto: tem uma chave de acesso de 44 dígitos. Série e
  número vêm decompostos diretamente da própria chave.
- NFS-e de serviço: não tem essa chave, tem um "Identificador
  Nacional" em formato próprio. Nesse caso, Série sempre vem "S", e o
  Número é confirmado cruzando os números soltos do texto com o
  Identificador Nacional (ou também "S" se não for possível confirmar).
"""

import os
from dataclasses import dataclass

from core.pdf_reader import extrair_texto_pdf
from core.ocr_reader import extrair_texto_imagem, extrair_texto_pdf_escaneado
from core.chave_regex import extrair_chave_acesso
from core.chave_parser import decompor_chave
from core.data_emissao import extrair_data_emissao
from core.nfse_parser import eh_nota_de_servico, processar_nota_servico, MARCADOR_SERVICO
from core.cupom_fiscal_parser import eh_cupom_fiscal, processar_cupom_fiscal, MARCADOR_CUPOM

EXTENSOES_IMAGEM = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".gif", ".webp"}


@dataclass
class ResultadoExtracao:
    chave: str
    serie: str
    numero: str
    data_emissao: str


def _extrair_texto_do_arquivo(caminho_arquivo: str, extensao: str) -> str:
    """Retorna o texto do arquivo, tentando texto digital antes de cair para OCR."""
    if extensao == ".pdf":
        texto = extrair_texto_pdf(caminho_arquivo)
        if extrair_chave_acesso(texto):
            return texto
        # PDF sem chave no texto digital -> pode ser escaneado, tenta OCR
        return extrair_texto_pdf_escaneado(caminho_arquivo)

    # imagem
    return extrair_texto_imagem(caminho_arquivo)


def processar_arquivo(caminho_arquivo: str) -> tuple[ResultadoExtracao | None, str]:
    """
    Retorna uma tupla (resultado, mensagem):
    - Sucesso (NF-e de produto): chave/serie/numero/data preenchidos, ""
    - Sucesso (NFS-e de serviço): serie = "S", numero confirmado (ou "S"
      se não confirmado), chave = Identificador Nacional (ou em branco
      se não encontrado), data preenchida se encontrada, ""
    - Falha real (arquivo não suportado, não encontrado, erro de
      leitura): (None, mensagem_explicando_o_problema)
    """
    if not os.path.isfile(caminho_arquivo):
        return None, "Arquivo não encontrado."

    extensao = os.path.splitext(caminho_arquivo)[1].lower()
    if extensao != ".pdf" and extensao not in EXTENSOES_IMAGEM:
        return None, f"Formato não suportado: {extensao}"

    try:
        texto = _extrair_texto_do_arquivo(caminho_arquivo, extensao)
    except Exception as erro:
        return None, f"Erro ao processar o arquivo: {erro}"

    data_emissao = extrair_data_emissao(texto) or ""
    chave = extrair_chave_acesso(texto)

    if chave:
        dados_chave = decompor_chave(chave)
        if dados_chave:
            return (
                ResultadoExtracao(
                    chave=dados_chave.chave,
                    serie=dados_chave.serie,
                    numero=dados_chave.numero,
                    data_emissao=data_emissao,
                ),
                "",
            )

    # Não achou uma chave de NF-e válida -> verifica se é nota de serviço
    if eh_nota_de_servico(texto):
        dados_servico = processar_nota_servico(texto)
        return (
            ResultadoExtracao(
                chave=dados_servico.identificador,
                serie=MARCADOR_SERVICO,
                numero=dados_servico.numero,
                data_emissao=data_emissao,
            ),
            "",
        )

    # Não é NF-e nem NFS-e -> verifica se é cupom fiscal
    if eh_cupom_fiscal(texto):
        dados_cupom = processar_cupom_fiscal(texto)
        return (
            ResultadoExtracao(
                chave=dados_cupom.identificador,
                serie=MARCADOR_CUPOM,
                numero=dados_cupom.numero,
                data_emissao=data_emissao,
            ),
            "",
        )

    return None, "Não encontrei uma chave de acesso nem identifiquei uma nota de serviço ou cupom fiscal neste arquivo."
