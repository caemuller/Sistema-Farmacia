# Sistema-Farmacia

## TO-DO
 - [x] gráfico de estoque feito por funcionario
 - [x] Remover refeito SS
 - [x] graficos refeitos por funcionarios
 - [x] graficos em relacao ao tempo


# 💻 Como Instalar o Python e Configurar seu Ambiente no Windows

Aqui está um guia passo a passo para instalar o Python e as bibliotecas
essenciais para o seu projeto no Windows.

## Passo 1: Baixar e Instalar o Python

-   Acesse o site oficial do Python em
    [python.org](https://www.python.org).
-   Clique no botão de download para a versão mais recente.
-   Execute o arquivo de instalação que você acabou de baixar.
-   Na primeira tela, é **CRUCIAL** que você selecione a caixa **"Add
    Python to PATH"** na parte inferior da janela. Isso permite que você
    execute os comandos `python` e `pip` de qualquer lugar no seu
    terminal.
-   Clique em **"Install Now"** e siga as instruções.

## Passo 2: Confirmar a Instalação

Após a instalação, abra o **Prompt de Comando** ou o **PowerShell** e
digite os seguintes comandos para verificar se tudo foi instalado
corretamente.

``` bash
python --version
pip --version
```

Ambos os comandos devem retornar a versão correspondente sem erros.\
Se não funcionar, o motivo mais provável é que a opção **"Add Python to
PATH"** não foi selecionada.

## Passo 3: Instalar as Bibliotecas com o Pip

Com o Python e o pip funcionando, você pode instalar as bibliotecas do
seu projeto (**requests, flask, flask-cors**) com um único comando.

``` bash
pip install requests flask flask-cors
```

O pip irá baixar e instalar automaticamente essas bibliotecas e todas as
suas dependências.

## Passo 4: Executar seu Arquivo Python

1.  Salve seu código Python em um arquivo com a extensão `.py`. Por
    exemplo: `meu_servidor.py`.

2.  Abra o **Prompt de Comando** ou **PowerShell**.

3.  Use o comando `cd` para navegar até a pasta onde você salvou o
    arquivo.\
    Exemplo, se o arquivo estiver na sua Área de Trabalho:

    ``` bash
    cd C:\Users\SeuUsuario\Desktop
    ```

4.  Execute seu arquivo com o comando `python` seguido do nome do
    arquivo:

    ``` bash
    python menu_server.py
    ```
