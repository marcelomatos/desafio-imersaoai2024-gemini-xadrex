# %% [markdown]
# # Desafio Alura & Google Imersão AI Gemini - 2024/05
# ## Projeto Gemini Xadrez
# Autor: **[Marcelo Matos](https://www.linkedin.com/in/marcelomatos/)**
# Github: **[Gemini Xadrez](https://github.com/marcelomatos/desafio_imersaoai2024_gemini-xadrez.git)**
#

# %%
# Instala pré-requisitos
# %pip install -qU google-generativeai matplotlib

# %%
# Resolve os imports necessários
import google.generativeai as genai
import json

# %%
# Define constantes para o jogo
PECAS = {
    "peao_branco": "♙",
    "torre_branca": "♖",
    "cavalo_branco": "♘",
    "bispo_branco": "♗",
    "rainha_branca": "♕",
    "rei_branco": "♔",
    "peao_preto": "♟",
    "torre_preta": "♜",
    "cavalo_preto": "♞",
    "bispo_preto": "♝",
    "rainha_preta": "♛",
    "rei_preto": "♚",
}

TABULEIRO_INICIAL = {
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


# %%
class JogoXadrez:
    """
    Classe para controlar o estado do jogo de xadrez.
    """

    def __init__(self, debugar:bool = False):
        """
        Inicializa o jogo com o tabuleiro na posição inicial.
        """
        self.debugar = debugar
        self.tabuleiro = TABULEIRO_INICIAL
        self.pecas_comidas_brancas = []
        self.pecas_comidas_pretas = []

    def atualizar_tabuleiro(self, novo_tabuleiro: dict) -> None:
        """
        Atualiza o tabuleiro com um novo estado e identifica as peças comidas.

        Args:
            novo_tabuleiro (dict): Um dicionário representando o novo estado do tabuleiro.
        """
        pecas_antes = [peca for peca in self.tabuleiro.values() if peca is not None]
        pecas_depois = [peca for peca in novo_tabuleiro.values() if peca is not None]

        for peca in pecas_antes:
            if peca not in pecas_depois:
                cor = 0 if "preto" in peca else 1
                self.adicionar_peca_comida(peca, cor)

        self.tabuleiro = novo_tabuleiro

    def adicionar_peca_comida(self, peca: str, cor: int) -> None:
        """
        Adiciona uma peça à lista de peças comidas.

        Args:
            peca (str): O nome da peça comida.
            cor (int): A cor da peça comida (0 para preto, 1 para branco).
        """
        if self.debugar:{print("Peca capturada: " + peca + "preto" if pcor==0 else "branco")}  # noqa: E701
        if cor == 0:
            self.pecas_comidas_pretas.append(peca)
        else:
            self.pecas_comidas_brancas.append(peca)


# %%
class GeminiAI:
    """
    Classe para interagir com o modelo Gemini.
    """

    def __init__(self, api_key: str, debugar:bool = False):
        """
        Inicializa a API do Gemini e define as configurações do modelo.

        Args:
            api_key (str): A chave da API do Gemini.
        """
        self.debugar = debugar
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-latest",
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 0,
                "max_output_tokens": 8192,
            },
            safety_settings=[
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
            ],
            system_instruction=self._gerar_instrucoes_iniciais()
        )
        self.convo = self.model.start_chat(history=[])
        self.convo.send_message("confirme que você entendeu todas as intruçoes e aguarde meu primeiro movimento")
        print(self.convo.last.text)

    def _gerar_instrucoes_iniciais(self) -> str:
        """
        Gera as instruções iniciais para o modelo Gemini.

        Returns:
            str: As instruções iniciais.
        """
        return f"Vamos jogar Xadrez. Você atuará com dois papeis: " + \
               "seu primeiro papel será validando os movimentos do usuário, " + \
               "seu segundo papel será como jogador das pedras pretas, inicialmente " + \
               "você será um jogador iniciante que possui algumas estratégias para vencer o jogo." + \
               "vou informar meu movimento, você responderá válido ou inválido de acordo com as regras do Xadrez." + \
               "se o meu movimento informar um destino que tenha uma peça sua considere que esse movimento irá comer sua peça." + \
               "após o meu movimento você informará qual será o seu movimento, " + \
               "após seu movimento retorne o tabuleiro atualizado em formato json. " + \
               "após ambos os movimentos, o ciclo recomeça com o jogador informando a próxima jogada" + \
               "o jogo termina quando for executado um check mate ou um jogador desistir" + \
               "voce deve manter a variavel tabuleiro atualizada." + \
               "se eu solicitar o tabuleiro atualizado você responderá com valor json da variavel tabuleiro." + \
               "voce deve manter mais duas variaveis uma para cada conjunto de pedras comidas pelo adversário." + \
               "quando solicitar as pecas pretas comidas você deve me informar o valor json dessa variavel." + \
               "quando solicitar as pecas brancas comidas você deve me informar o valor json dessa variavel." + \
               "o tabuleiro inicial é representado pela variavel tabuleiro com o valor json a seguir" + \
               f"tabuleiro = {json.dumps(TABULEIRO_INICIAL)}"

    def enviar_movimento(self, movimento: str) -> (str, dict):
        """
        Envia um movimento para o modelo Gemini e processa a resposta.

        Args:
            movimento (str): O movimento a ser enviado.

        Returns:
            str: A resposta do modelo Gemini referente à validade da jogada.
            dict: Um dicionário representando o estado atual do tabuleiro.
        """
        self.convo.send_message(movimento)
        resposta_completa = self.convo.last.text.lower()
        
        # Extrai o tabuleiro da resposta
        inicio_json = resposta_completa.find('{')
        fim_json = resposta_completa.rfind('}') + 1
        tabuleiro_json = resposta_completa[inicio_json:fim_json]
        if self.debugar: {print(tabuleiro_json)}  # noqa: E701
        tabuleiro = json.loads(tabuleiro_json)
        if self.debugar: {print(tabuleiro)}  # noqa: E701
        
        # Extrai a parte textual da resposta (válido/inválido)
        resposta_textual = resposta_completa[:inicio_json].strip()

        return resposta_textual, tabuleiro


# %%
class InterfaceUsuario:
    """
    Classe para interagir com o usuário e apresentar informações.
    """

    def __init__(self, jogo: JogoXadrez, debugar:bool = False ):
        """
        Inicializa a interface do usuário.

        Args:
            jogo (JogoXadrez): Uma instância do jogo de xadrez.
        """
        self.jogo = jogo
        self.debugar = debugar

    def apresent_tabuleiro(self) -> None:
        """
        Apresenta o tabuleiro no console.
        """
        for i in range(8):
            linha = str(i) + "\t"
            for j in range(8):
                posicao = chr(j + 97) + str(8 - i)
                peca = self.jogo.tabuleiro.get(posicao)
                if peca:
                    linha += PECAS.get(peca) + "\t"
                else:
                    linha += "  \t"
            print(linha)
        print("\tA\tB\tC\tD\tE\tF\tG\tH")

    def apresent_pecas_comidas(self, cor: int) -> None:
        """
        Apresenta as peças comidas de uma determinada cor.

        Args:
            cor (int): A cor das peças (0 para preto, 1 para branco).
        """
        pecas = "Pretas" if cor == 0 else "Brancas"
        pecas_comidas = self.jogo.pecas_comidas_pretas if cor == 0 else self.jogo.pecas_comidas_brancas
        print(f"Peças {pecas} capturadas: {', '.join(pecas_comidas)}")

    def obter_movimento_usuario(self) -> str:
        """
        Obtém um movimento do usuário.

        Returns:
            str: O movimento informado pelo usuário.
        """
        print("Informe 'peças' para a lista de peças, 'fim' ou '' para finalizar o jogo.")
        print("Informe sua jogada no formato 'peça' de 'origem' para 'destino'.")
        print("Exemplo: peão de b2 para b3. \n")
        prompt = " "
        while prompt != "":
            prompt = input("Qual a sua jogada ou comando : ").lower()
            if prompt == "peças" or prompt == "pecas":
                print("\n\nLista de Peças:\n♙ => Peao,\n♖ => Torre,\n♘ => Cavalo,\n♗ => Bispo,\n♕ => Rainha,\n♔ => Rei")
            elif prompt == "fim" or prompt == "termino":
                exit(0)
            else:
                return prompt


# %%
def main():
    """
    Função principal para executar o jogo de xadrez.
    """
    debugar = True
    # Substitua 'SUA_API_KEY' pela sua chave de API do Gemini
    api_key = input("Informe sua GEMINI API_KEY : ")  
    ai = GeminiAI(api_key, debugar=debugar)
    jogo = JogoXadrez(debugar=debugar)
    interface = InterfaceUsuario(jogo, debugar=debugar)

    while True:
        interface.apresent_pecas_comidas(1)
        interface.apresent_tabuleiro()
        interface.apresent_pecas_comidas(0)
        movimento = interface.obter_movimento_usuario()

        resposta_textual, tabuleiro = ai.enviar_movimento(movimento)
        print(resposta_textual)

        if "válido" in resposta_textual or "valido" in resposta_textual:
            jogo.atualizar_tabuleiro(tabuleiro)


# %%
if __name__ == "__main__":
    main()
# %%
