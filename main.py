"""
Leitor de Chave de Acesso e Dados da NF-e / NFS-e / Cupom Fiscal
------------------------------------------------------------------
App simples: você escolhe um PDF ou imagem de uma nota e ele mostra na
tela a chave de acesso (ou identificador), série, número e data de
emissão - cada campo com um botão pra copiar direto.

Como rodar:
    pip install -r requirements.txt
    python main.py

(veja o README.md para instalar o Tesseract OCR e o Poppler no Windows,
ou usar as versões já empacotadas na pasta bin/)
"""

import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QFileDialog,
    QFrame,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from core.extractor import processar_arquivo, EXTENSOES_IMAGEM

_EXTENSOES_IMAGEM_STR = " ".join(f"*{ext}" for ext in sorted(EXTENSOES_IMAGEM))
FILTRO_ARQUIVOS = f"Arquivos suportados (*.pdf {_EXTENSOES_IMAGEM_STR})"

_TEMA_ESCURO = """
QWidget {
    background-color: #1e1f26;
    color: #e8e8ec;
    font-family: "Segoe UI", sans-serif;
    font-size: 16px;
}
QLabel#titulo {
    font-size: 26px;
    font-weight: 600;
    color: #f4f4f7;
}
QLabel#subtitulo {
    color: #9a9ba8;
    font-size: 14px;
}
QLabel.rotulo {
    color: #b7b8c4;
    font-weight: 600;
    font-size: 13px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
QLineEdit {
    background-color: #2a2b34;
    border: 1px solid #3c3d4a;
    border-radius: 10px;
    padding: 14px 16px;
    color: #f4f4f7;
    font-size: 17px;
    selection-background-color: #5865f2;
}
QLineEdit:focus {
    border: 1px solid #5865f2;
}
QPushButton {
    background-color: #5865f2;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 14px 22px;
    font-weight: 600;
    font-size: 16px;
}
QPushButton:hover {
    background-color: #6875f5;
}
QPushButton:pressed {
    background-color: #4854d1;
}
QPushButton#botaoCopiar {
    background-color: #3c3d4a;
    padding: 12px 18px;
    font-weight: normal;
    font-size: 15px;
    min-width: 40px;
}
QPushButton#botaoCopiar:hover {
    background-color: #4a4b5a;
}
QFrame#linha {
    background-color: #35364280;
    max-height: 1px;
}
QLabel#status {
    color: #f28b82;
    font-size: 14px;
}
QLabel#statusOk {
    color: #81c995;
    font-size: 14px;
}
"""


def _campo_com_copia(rotulo_texto: str) -> tuple[QVBoxLayout, QLineEdit]:
    """Monta um bloco: rótulo em cima, campo + botão de copiar embaixo."""
    coluna = QVBoxLayout()
    coluna.setSpacing(8)

    rotulo = QLabel(rotulo_texto)
    rotulo.setProperty("class", "rotulo")
    rotulo.setObjectName("rotuloCampo")
    coluna.addWidget(rotulo)

    linha_campo = QHBoxLayout()
    linha_campo.setSpacing(6)

    campo = QLineEdit()
    campo.setReadOnly(True)
    linha_campo.addWidget(campo)

    botao_copiar = QPushButton("Copiar")
    botao_copiar.setObjectName("botaoCopiar")
    botao_copiar.setCursor(Qt.PointingHandCursor)
    botao_copiar.clicked.connect(lambda: _copiar_para_area_de_transferencia(campo))
    linha_campo.addWidget(botao_copiar)

    coluna.addLayout(linha_campo)
    return coluna, campo


def _copiar_para_area_de_transferencia(campo: QLineEdit):
    if campo.text():
        QApplication.clipboard().setText(campo.text())


class JanelaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Leitor de Nota Fiscal")
        self.setMinimumWidth(720)
        self.resize(900, 560)
        self.setStyleSheet(_TEMA_ESCURO)
        self._montar_interface()

    def _montar_interface(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(20)

        titulo = QLabel("Leitor de Nota Fiscal")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)

        subtitulo = QLabel(
            "PDF ou imagem de NF-e, NFS-e ou cupom fiscal - chave, série, número e data em um clique."
        )
        subtitulo.setObjectName("subtitulo")
        subtitulo.setWordWrap(True)
        layout.addWidget(subtitulo)

        linha_divisoria_topo = QFrame()
        linha_divisoria_topo.setObjectName("linha")
        linha_divisoria_topo.setFrameShape(QFrame.HLine)
        layout.addWidget(linha_divisoria_topo)

        linha_botao = QHBoxLayout()
        self.label_arquivo = QLabel("Nenhum arquivo selecionado")
        self.label_arquivo.setObjectName("subtitulo")
        self.label_arquivo.setWordWrap(True)
        botao_selecionar = QPushButton("Selecionar arquivo...")
        botao_selecionar.setCursor(Qt.PointingHandCursor)
        botao_selecionar.clicked.connect(self._selecionar_arquivo)
        linha_botao.addWidget(botao_selecionar)
        linha_botao.addStretch()
        layout.addLayout(linha_botao)
        layout.addWidget(self.label_arquivo)

        coluna_chave, self.campo_chave = _campo_com_copia("Chave de acesso / Identificador")
        self.campo_chave.setPlaceholderText("Aparece aqui depois de processar o arquivo")
        layout.addLayout(coluna_chave)

        linha_campos = QHBoxLayout()
        linha_campos.setSpacing(24)

        coluna_serie, self.campo_serie = _campo_com_copia("Série")
        linha_campos.addLayout(coluna_serie, stretch=1)

        coluna_numero, self.campo_numero = _campo_com_copia("Número")
        linha_campos.addLayout(coluna_numero, stretch=2)

        coluna_data, self.campo_data = _campo_com_copia("Data de emissão")
        linha_campos.addLayout(coluna_data, stretch=2)

        layout.addLayout(linha_campos)

        self.label_status = QLabel("")
        self.label_status.setObjectName("status")
        self.label_status.setWordWrap(True)
        layout.addWidget(self.label_status)

        self.setLayout(layout)

    def _selecionar_arquivo(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Selecionar nota fiscal", "", FILTRO_ARQUIVOS
        )
        if not caminho:
            return

        self.label_arquivo.setText(caminho)
        self.label_status.setStyleSheet(
            "color: #f4f4f7; font-size: 20px; font-weight: 600;"
        )
        self.label_status.setText("Processando...")
        self.campo_chave.clear()
        self.campo_serie.clear()
        self.campo_numero.clear()
        self.campo_data.clear()
        QApplication.processEvents()  # atualiza a tela antes de processar

        resultado, mensagem_erro = processar_arquivo(caminho)

        if resultado:
            self.campo_chave.setText(resultado.chave)
            self.campo_serie.setText(resultado.serie)
            self.campo_numero.setText(resultado.numero)
            self.campo_data.setText(resultado.data_emissao)
            self.label_status.setStyleSheet(
                "color: #81c995; font-size: 20px; font-weight: 600;"
            )
            self.label_status.setText("Processado com sucesso.")
        else:
            self.label_status.setStyleSheet(
                "color: #f28b82; font-size: 20px; font-weight: 600;"
            )
            self.label_status.setText(mensagem_erro)


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 12))
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
