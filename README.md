# Leitor de Chave de Acesso - NF-e

App simples pra Windows: você seleciona o PDF ou a imagem (jpg/jpeg/png)
de uma nota fiscal e ele te mostra na tela a chave de acesso (44 dígitos,
sem espaços) pronta pra copiar.

## 1. Instalar o Python

Se ainda não tiver, baixe em https://www.python.org/downloads/ (marque
a opção "Add Python to PATH" durante a instalação).

## 2. Instalar as dependências do projeto

Abra o terminal (cmd, PowerShell ou o terminal do PyCharm) na pasta do
projeto e rode:

```
pip install -r requirements.txt
```

## 3. Colocar o Poppler e o Tesseract DENTRO do projeto (sem precisar instalar nem mexer no PATH)

O app já vem preparado pra procurar esses dois programas sozinho dentro
de uma pasta `bin/`, junto do `main.py`. Assim ninguém precisa instalar
nada manualmente nem configurar variável de ambiente - só extrair os
arquivos no lugar certo.

Estrutura final que o projeto precisa ter:

```
leitor_chave_nfe/
├── main.py
├── requirements.txt
├── core/
└── bin/
    ├── poppler/          <- extraia o zip do Poppler aqui dentro
    │   └── poppler-26.02.0/Library/bin/pdftoppm.exe (etc.)
    └── tesseract/        <- copie a instalação do Tesseract aqui dentro
        └── tesseract.exe (e a pasta tessdata do lado)
```

### Poppler (necessário só se você for ler PDF escaneado ou imagem)

1. Baixe o arquivo **"Release-..."** (não o "Source code") em:
   https://github.com/oschwartz10612/poppler-windows/releases
2. Extraia o zip inteiro dentro da pasta `bin/poppler/` do projeto
3. Não precisa reorganizar nada - o app procura o `pdftoppm.exe` em
   qualquer subpasta dentro de `bin/poppler/` automaticamente

### Tesseract OCR (necessário pra ler imagens e PDFs escaneados)

1. Baixe e instale normalmente: https://github.com/UB-Mannheim/tesseract/wiki
   (na tela de idiomas, marque **Portuguese**)
2. Depois de instalado, ele fica em algo como
   `C:\Program Files\Tesseract-OCR`
3. **Copie essa pasta inteira** (com o `tesseract.exe` e a pasta
   `tessdata` dentro) para dentro de `bin/tesseract/` do projeto
4. Pode desinstalar o Tesseract do Windows depois, se quiser - o app
   vai usar só a cópia dentro de `bin/tesseract/`

Se você preferir deixar o Tesseract/Poppler instalados normalmente no
Windows (com PATH configurado, como fizemos antes) em vez de copiar pra
dentro do projeto, o app também funciona - ele só usa a pasta `bin/`
como primeira opção e cai pro que estiver instalado no sistema se não
achar nada ali dentro.

## 4. Rodar o app

```
python main.py
```

Vai abrir uma janela: clique em "Selecionar arquivo...", escolha o PDF
ou imagem da nota, e a chave aparece no campo de texto, já selecionada
pra você copiar (Ctrl+C).

## 5. Gerar um .exe único (já com tudo embutido)

Depois que tudo estiver funcionando com `python main.py`:

```
pip install pyinstaller
pyinstaller --onefile --windowed --name LeitorChaveNFe --add-data "bin;bin" main.py
```

O `--add-data "bin;bin"` é o que garante que a pasta `bin/` (com o
Poppler e o Tesseract) vá junto dentro do `.exe`. O executável final
fica em `dist\LeitorChaveNFe.exe` - é só esse arquivo, dá pra levar pra
qualquer Windows e rodar sem instalar Python, Poppler ou Tesseract
separadamente.

## Melhorias futuras (ainda não implementadas)

Ideias já discutidas pra próximas versões do app:

- **Suporte a mais tipos de nota**: além de NF-e, NFS-e e cupom fiscal,
  ir adicionando novos formatos conforme aparecerem (a estrutura atual
  já foi pensada pra isso - cada tipo tem seu próprio módulo em `core/`)
- **Histórico de processamentos**: guardar registro de cada nota lida
  (arquivo, chave/identificador, série, número, data de emissão, data
  em que foi processada)
- **Banco de dados local (SQLite)**: usar um banco de dados local para
  guardar esse histórico, sem precisar de servidor externo - encaixa
  bem com o app rodando 100% offline
- **Login e senha por usuário**: identificar qual usuário processou
  cada nota, associando ao histórico acima. Se o objetivo for só
  rastreabilidade (saber quem fez o quê), um login simples local
  resolve; se for também controle de acesso/segurança, precisa de mais
  cuidado (senha com hash, controle de sessão etc.) - decidir o nível
  necessário quando for implementar


- PDF com texto digital → extração direta via `pdfplumber` (rápido, não usa OCR)
- PDF escaneado (sem texto) → convertido em imagem via Poppler e lido via OCR (Tesseract)
- Imagem (jpg/jpeg/png) → lida diretamente via OCR (Tesseract)
- Em qualquer um dos casos, o texto extraído é varrido por uma expressão
  regular procurando uma sequência de 44 dígitos (aceita a chave tanto
  grudada quanto separada em blocos de 4, como aparece no DANFE)
