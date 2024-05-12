# %% [markdown]
# # Desafio Alura & Google Imersão AI Gemini - 2024/05
# ## Projeto Gemini Xadrex
# Autor: **[Marcelo Matos](https://www.linkedin.com/in/marcelomatos/)**
# 
# Github: **[Gemini Xadrex](https://github.com/marcelomatos/desafio_imersaoai2024_gemini-xadrex.git)**
# 

# %%
# Instala pré-requisitos
# %pip install -qU google-generativeai matplotlib

# %%
# Resolve os imports necessários
from time import sleep
import google.generativeai as genai
import matplotlib.pyplot as plt
import os, json

# %%
# Define as variaveis utilizadas no modelo
generation_config = {}
safety_settings = []
tabuleiro = {}
novo_tabuleiro = ""
pecas_comidas_brancas = []
nova_pecas_comidas_brancas = ""
pecas_comidas_pretas = []
nova_pecas_comidas_pretas = ""
cor_pecas_comidas_brancas = 1
cor_pecas_comidas_pretas = 0
pecas = {}
system_instructions = ""
prompt_inicial = ""
prompt_tabuleiro_atualizado = ""
prompt_pedras_comidas_brancas = ""
prompt_pedras_comidas_pretas = ""
cores = ""
model = object
convo = object

# %%
# Inicializa Constantes para interação com o modelo

# class gemini_xadrex:
#     # Set up the model
#     generation_config = {}
#     safety_settings = []
#     tabuleiro = {}
#     pecas = {}
#     system_instructions = ""
#     prompt_inicial = ""
#     prompt_tabuleiro_atualizado = ""
#     prompt_pedras_comidas_brancas = ""
#     prompt_pedras_comidas_pretas = ""

generation_config = {
                        "temperature": 1,
                        "top_p": 0.95,
                        "top_k": 0,
                        "max_output_tokens": 8192,
                    }

safety_settings =   [
                        {
                            "category": "HARM_CATEGORY_HARASSMENT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_HATE_SPEECH",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                    ]

tabuleiro = {
            'a8': 'torre_preta', 'b8': 'cavalo_preto', 'c8': 'bispo_preto', 'd8': 'rainha_preta', 
            'e8': 'rei_preto', 'f8': 'bispo_preto', 'g8': 'cavalo_preto', 'h8': 'torre_preta',
            'a7': 'peao_preto', 'b7': 'peao_preto', 'c7': 'peao_preto', 'd7': 'peao_preto',
            'e7': 'peao_preto', 'f7': 'peao_preto', 'g7': 'peao_preto', 'h7': 'peao_preto',
            'a6': None, 'b6': None, 'c6': None, 'd6': None, 'e6': None, 'f6': None, 'g6': None, 'h6': None,
            'a5': None, 'b5': None, 'c5': None, 'd5': None, 'e5': None, 'f5': None, 'g5': None, 'h5': None,
            'a4': None, 'b4': None, 'c4': None, 'd4': None, 'e4': None, 'f4': None, 'g4': None, 'h4': None,
            'a3': None, 'b3': None, 'c3': None, 'd3': None, 'e3': None, 'f3': None, 'g3': None, 'h3': None,
            'a2': 'peao_branco', 'b2': 'peao_branco', 'c2': 'peao_branco', 'd2': 'peao_branco',
            'e2': 'peao_branco', 'f2': 'peao_branco', 'g2': 'peao_branco', 'h2': 'peao_branco',
            'a1': 'torre_branca', 'b1': 'cavalo_branco', 'c1': 'bispo_branco', 'd1': 'rainha_branca',
            'e1': 'rei_branco', 'f1': 'bispo_branco', 'g1': 'cavalo_branco', 'h1': 'torre_branca'
            }

pecas = {
            "peao_branco"   : "♙",
            "torre_branca"  : "♖",
            "cavalo_branco" : "♘", 
            "bispo_branco"  : "♗",
            "rainha_branca" : "♕",
            "rei_branco"    : "♔",
            "peao_preto"    : "♟",
            "torre_preta"   : "♜",
            "cavalo_preto"  : "♞", 
            "bispo_preto"   : "♝",
            "rainha_preta"  : "♛",
            "rei_preto"     : "♚"
        }

system_instructions =  f"Vamos jogar Xadrex. Você atuará com dois papeis, " + \
                        "seu primeiro papel será validando os movimentos do usuário,  " + \
                        "seu segundo papel será como jogador das pedras pretas, inicialmente " +\
                        "você será um jogador iniciante que possui algumas estratégias para vencer o jogo." + \
                        "vou informar meu movimento, você responderá válido ou inválido de acordo com as regras do xadrex." + \
                        "se o meu movimento informar um destino que tenha uma peça sua considere que esse movimento irá comer sua peça." + \
                        "após o meu movimento você informará qual será o seu movimento." + \
                        "após ambos os movimentos, o ciclo recomeça com o jogador informando a próxima jogada" + \
                        "o jogo termina quando for executado um check mate ou um jogador desistir" + \
                        "voce deve manter a variavel tabuleiro atualizada." + \
                        "se eu solicitar o tabuleiro atualizado você responderá com valor json da variavel tabuleiro." + \
                        "voce deve manter mais duas variaveis uma para cada conjunto de pedras comidas pelo adversário." + \
                        "quando solicitar as pecas pretas comidas você deve me informar o valor json dessa variavel." + \
                        "quando solicitar as pecas brancas comidas você deve me informar o valor json dessa variavel." + \
                        "o tabuleiro inicial é representado pela variavel tabuleiro com o valor json a seguir" + \
                        "tabuleiro = {" + \
                                        "'a8': 'torre_preta', 'b8': 'cavalo_preto', 'c8': 'bispo_preto', 'd8': 'rainha_preta', " + \
                                        "'e8': 'rei_preto', 'f8': 'bispo_preto', 'g8': 'cavalo_preto', 'h8': 'torre_preta'," + \
                                        "'a7': 'peao_preto', 'b7': 'peao_preto', 'c7': 'peao_preto', 'd7': 'peao_preto', " + \
                                        "'e7': 'peao_preto', 'f7': 'peao_preto', 'g7': 'peao_preto', 'h7': 'peao_preto'," + \
                                        "'a6': None, 'b6': None, 'c6': None, 'd6': None, 'e6': None, 'f6': None, 'g6': None, 'h6': None," + \
                                        "'a5': None, 'b5': None, 'c5': None, 'd5': None, 'e5': None, 'f5': None, 'g5': None, 'h5': None," + \
                                        "'a4': None, 'b4': None, 'c4': None, 'd4': None, 'e4': None, 'f4': None, 'g4': None, 'h4': None," + \
                                        "'a3': None, 'b3': None, 'c3': None, 'd3': None, 'e3': None, 'f3': None, 'g3': None, 'h3': None," + \
                                        "'a2': 'peao_branco', 'b2': 'peao_branco', 'c2': 'peao_branco', 'd2': 'peao_branco'," + \
                                        "'e2': 'peao_branco', 'f2': 'peao_branco', 'g2': 'peao_branco', 'h2': 'peao_branco'," + \
                                        "'a1': 'torre_branca', 'b1': 'cavalo_branco', 'c1': 'bispo_branco', 'd1': 'rainha_branca', " + \
                                        "'e1': 'rei_branco', 'f1': 'bispo_branco', 'g1': 'cavalo_branco', 'h1': 'torre_branca'" + \
                                        "}"                         

prompt_inicial = "confirme que você entendeu todas as intruçoes e aguarde meu primeiro movimento"
prompt_tabuleiro_atualizado = "responda apenas o valor da variavel da variavel tabuleiro com os movimentos atualizados"
prompt_pedras_comidas_brancas = "responda apenas o valor da variavel das pedras brancas comidas pelo adversário."
prompt_pedras_comidas_pretas = "responda apenas o valor da variavel das pedras pretas comidas pelo adversário."

cores = {True: '#DDB88C', False: '#A9A9A9'}

# %%
def apresenta_tabuleiro_txt(tabuleiro):
    linha = ""
    for i in range(8):
        linha = str(i) + "\t"
        for j in range(8):
            # Obtendo a posição e a peça (se houver)
            posicao = chr(j + 97) + str(8 - i)
            peca = tabuleiro.get(posicao)
            # Adicionando o nome da peça no centro do quadrado (se houver)
            if peca:
                linha = linha + pecas.get(peca) + "\t"
            else:
                linha = linha + "  \t"
        print(linha)
    linha = "\tA\tB\tC\tD\tE\tF\tG\tH"
    print(linha)

# %%
def apresenta_pecas_comidas_txt(cor_pecas, pecas_comidas):

    peca = ""
    pecas = "Pretas" if cor_pecas == 0 else "Brancas"
    pecas = f"Peças {pecas} capturadas: "
    # Iterando sobre as linhas e colunas do tabuleiro
    for i in range(15):
        peca = "" if peca == "" else ", " + \
               pecas.get(pecas_comidas[i]) if i < len(pecas_comidas) else None
        if peca:
            pecas =+ peca
            
    print(pecas)

# %%
def jogada_usuario() -> str:

    print("Informe 'peças' para a lista de peças, 'fim' ou '' para finalizar o jogo.")
    print("Informe sua jogada no formato 'peça' de 'origem' para 'destino'.")
    print("Exemplo: peão de b2 para b3. \n")
    
    prompt = " "
    novo_tabuleiro = ""
    while prompt != "":
        prompt = input("Qual a sua jogada ou comando : ")
        prompt = prompt.lower()
        print(prompt)

        if (prompt == "peças") or (prompt == "pecas"):
            print ("\n\nLista de Peças:\n♙ => Peao,\n♖ => Torre,\n♘ => Cavalo,\n♗ => Bispo,\n♕ => Rainha,\n♔ => Rei")
        elif (prompt == "fim") or (prompt == "termino"):
            prompt = ""
            os._exit(0)
        else:
            convo.send_message(prompt)
            # print(prompt + "\n")
            resposta = convo.last.text.lower()
            print(resposta)
            if ("válido" in resposta) or (("valido" in resposta)):
                print("Resposta Válida")
                prompt = ""
                if "json" in resposta:
                    novo_tabuleiro = resposta[resposta.find("json"):]

    return novo_tabuleiro


# %%
def atualiza_status_jogo(novo_tabuleiro,debugar = False) -> [str]:

    #Atualiza variaveis de controle do Jogo
    texto_temporario = ""

    ##### >>>> Processa TABULEIRO atualizado
    if novo_tabuleiro == "":
        if debugar: 
            print("tabuleiro")
        convo.send_message(prompt_tabuleiro_atualizado)
        texto_temporario = convo.last.text
        if debugar: 
            print(texto_temporario)
        texto_temporario = convo.last.text.replace("json","").replace("```","").replace("\n","")
        if debugar: 
            print(texto_temporario)
        tabuleiro = json.loads(texto_temporario)
    else:
        if type(novo_tabuleiro) == str:
            tabuleiro = json.loads(novo_tabuleiro.replace("json","").replace("`","").replace("\n","").replace(" ",""))
        else:
            tabuleiro = novo_tabuleiro
    if debugar: 
        print(tabuleiro)
    return dict(tabuleiro)

# %%
def atualiza_status_jogo_pecas(tabuleiro,cor_pecas,debugar = False) -> []:

    # ##### >>>> Processa pedras BRANCAS comidas
    # sleep(2)
    # if debugar: 
    #     print("pecas comidas brancas")
    # convo.send_message(prompt_pedras_comidas_brancas)
    # texto_temporario = convo.last.text
    # if debugar: 
    #     print(texto_temporario)
    # texto_temporario = convo.last.text.replace("json","").replace("```","").replace("\n","").replace("[","").replace("]","").replace(" ","")
    # if debugar: 
    #     print(texto_temporario)
    # pecas_comidas_brancas = list(texto_temporario)
    # if debugar: 
    #     print(pecas_comidas_brancas)

    # ##### >>>> Processa pedras PRETAS comidas
    # sleep(2)
    # if debugar: 
    #     print("pecas comidas pretas")
    # convo.send_message(prompt_pedras_comidas_pretas)
    # texto_temporario = convo.last.text
    # if debugar: 
    #     print(texto_temporario)
    # texto_temporario = convo.last.text.replace("json","").replace("```","").replace("\n","").replace("[","").replace("]","").replace(" ","")
    # if debugar: 
    #     print(texto_temporario)
    # pecas_comidas_brancas = list(texto_temporario)
    # if debugar: 
    #     print(pecas_comidas_pretas)

    return []

# %%
# print(convo.last.text)
# print(convo.last.text.replace("json","").replace("```","").replace("\n",""))
# tabuleiro = convo.last.text.replace("json","").replace("```","").replace("\n","")
# print(tabuleiro)

# atualiza_status_jogo(True)

# %%
# Inicializa o modelo para atuar como Jogo de Xadrex e Jogador Autonamo das Peças Pretas

# def inicializar_ai():

# API_KEY = "SUA_API_KEY"

if API_KEY == None:
    API_KEY = input("Informe sua GEMINI API_KEY : ")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(  model_name="gemini-1.5-pro-latest",
                                generation_config=generation_config,
                                safety_settings=safety_settings,
                                system_instruction=system_instructions)

convo = model.start_chat(history=[])

convo.send_message(prompt_inicial)
print(convo.last.text)

# %%
# Controle do Jogo
debugar = True
jogo_ativo = True
novo_tabuleiro = tabuleiro

# inicializar_ai()

while jogo_ativo:
    if debugar:
        print("Início do laço")
    tabuleiro = atualiza_status_jogo(novo_tabuleiro)
    apresenta_pecas_comidas_txt(cor_pecas_comidas_brancas, pecas_comidas_brancas)
    apresenta_tabuleiro_txt(tabuleiro)
    apresenta_pecas_comidas_txt(cor_pecas_comidas_pretas, pecas_comidas_pretas)
    if debugar:
        print("Vai iniciar a jogada do usuário")
    novo_tabuleiro = jogada_usuario()
    if debugar:
        print("Fim da jogada do usuário")




# %%
