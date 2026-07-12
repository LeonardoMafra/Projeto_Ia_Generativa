
# import das bibliotecas utilizadas para o projeto
import streamlit as st
import os
import time
import pandas as pd
import pickle
import spacy
from groq                          import Groq
from dotenv                        import load_dotenv
from langchain_groq                import ChatGroq
from langchain_core.prompts        import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages       import HumanMessage, AIMessage, SystemMessage
from langgraph.graph               import StateGraph, END
from typing                        import TypedDict, List



# Definição do titulo e icone do aplicativo.

st.set_page_config(
    page_title="Desafio Senai IA-Generativa",
    page_icon="🏆", 
    layout="wide",                    
)

# Texto de apresentação e explicação dos desafios propostos e resolvidos

st.title("Projetos e Desafios em IA Generativa")

st.write("Durante o curso de IA Generativa, foram propostos desafios práticos com o objetivo de aplicar os conhecimentos adquiridos ao longo da formação. Este aplicativo reúne as soluções desenvolvidas para esses desafios, demonstrando a utilização das ferramentas, tecnologias e metodologias apresentadas durante o curso. Os desafios propostos foram o seguites: ")

st.subheader("Desafio 1 - Utilização de IA-Generativa")

st.write("Desenvolver, até o final do curso, um projeto de categorização de produtos com IA e o Streamlit, sendo que o modelo vai se basear em uma base de dados para escolher a qual classificação o item melhor se encaixa.")
  
st.subheader("Desafio 2 - Aplicando melhorias ao modelo utilizando LangChain")

st.write("Com base no exemplo desenvolvido em aula, transforme a aplicação que estava estática em uma aplicação dinâmica utilizando input() e crie uma interface gráfica utilizando Streamlit para uma das aplicações desenvolvidas.")

st.subheader("Desafio 3 - Aplicando melhorias ao modelo utilizando LangGraph")

st.write("Com base no exemplo desenvolvido em aula, transforme a aplicação que estava estática em uma aplicação dinâmica utilizando input() e crie uma interface gráfica utilizando Streamlit para uma das aplicações desenvolvidas.") 



# 1. Inicializa o estado da página atual se não existir

if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "desafio1"

# 2. Cria o menu de navegação com colunas 

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("1️⃣ Desafio 1", use_container_width=True):
        st.session_state.pagina_atual = "desafio1"

with col2:
    if st.button("2️⃣ Desafio 2", use_container_width=True):
        st.session_state.pagina_atual = "desafio2"

with col3:
    if st.button("3️⃣ Desafio 3", use_container_width=True):
        st.session_state.pagina_atual = "desafio3"

st.divider()


#Desafio 1 - criando a chamada do modelo e a função da classificação

load_dotenv()

modelo = ChatGroq(
    api_key = os.environ.get("GROQ_API_KEY"),
    model = "openai/gpt-oss-120b",
    temperature = 0.7,
    max_tokens = 1000,
)


CATEGORIAS = [
    'Eletroportáteis',
    'Brinquedos',
    'TV e Home Theater',
    'Celulares e Smartphones',
    'Informática e Acessórios',
    'Utilidades Domésticas',
    'Beleza e Perfumaria',
    'Informática',
    'Eletrodomésticos',
    'Bebês',
]

SYSTEM_PROMPT = f"""
Você é um especialista em categorização de produtos de e-commerce brasileiro.
Sua tarefa é classificar o produto informado em exatamente UMA das categorias abaixo.

Categorias disponíveis:
{chr(10).join(f'- {c}' for c in CATEGORIAS)}

Regras obrigatórias:

1. Responda SOMENTE com o nome exato da categoria.
2. Não escreva explicações.
3. Não invente categorias.
4. Escolha apenas uma categoria.
5. Se houver dúvida, escolha a categoria mais próxima.

Exemplos:

Produto: Smartphone Samsung Galaxy A54 128GB
Categoria: Celulares e Smartphones

Produto: Panela de Pressão Tramontina 4,5L
Categoria: Utilidades Domésticas

Produto: Notebook Dell Inspiron Core i5
Categoria: Informática

Produto: Smart TV LG 55 4K
Categoria: TV e Home Theater
"""

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Função que recebe o nome do produto e utiliza o modelo para determinar a qual categoria ele pertence

def classificar_produto(nome_produto: str) -> str:

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": nome_produto
            },
        ],
        temperature=0,
        max_tokens=10,
    )

    resposta = completion.choices[0].message.content.strip()

    for cat in CATEGORIAS:
        if resposta.lower() == cat.lower():
            return cat

    resposta_lower = resposta.lower()

    for cat in CATEGORIAS:
        if cat.lower() in resposta_lower:
            return cat

    return "Categoria não identificada"

# preparação do aplicativo para realizar a busca e a classificação

if st.session_state.pagina_atual == "desafio1":


    st.header("Classificação de Produtos com IA")

    st.write("""Esta aplicação utiliza um modelo de IA Generativa para classificar automaticamente produtos de e-commerce em categorias.
     Após realizar a classificação ele exibe a qual categoria o produto pertence e porcentagem de chance do produto pertencer a categoria.""")

    @st.cache_resource
    def load_model():
        with open("model.pkl", "rb") as  f:
            return pickle.load(f)
        

    @st.cache_resource
    def load_npl():
        return spacy.blank("pt")

    pipeline = load_model()
    nlp = load_npl()

    def preprocess (text : str) -> str:
        """Tokeniza , minuscula, e remove pontuação / espaços extras."""
        doc= nlp(str(text).lower())
        tokens = [t.text for t in doc if not t.is_punct and not t.is_space]
        return " ".join(tokens)

    produto = st.text_input("Digite o nome do produto:", placeholder="Ex: Smartphone Samsung Galaxy A54")

    if produto :
        texto = preprocess(produto)
        categoria = pipeline.predict([texto])[0]
        proba = pipeline.predict_proba([texto])[0]
        classes = pipeline.classes_

        st.success (f"**Categoria Prevista:** {categoria}")

        st.subheader("Probabilidade por categoria")
        proba_dict = dict(sorted(zip(classes, proba), key = lambda x: x[1], reverse= True))
        for cat, prob in proba_dict.items():
            st.progress(float(prob), text=f"{cat}: {prob*100:.1f}%")

# chatbot com memoria e comportamento personalizavel.

elif st.session_state.pagina_atual == "desafio2":

    st.title("Assistente Virtual Personalizável com IA")
    st.write("Chatbot interativo baseado em IA Generativa que permite personalizar o comportamento do assistente através de instruções definidas pelo usuário, proporcionando respostas adaptadas a diferentes contextos e necessidades.")


    
    # Inicializa o papel caso não exista
    if "papel_ia" not in st.session_state:
        st.session_state.papel_ia = ""

    # Inicializa o histórico
    if "historico" not in st.session_state:
        st.session_state.historico = []

    papel = st.text_area(
        "Como a IA deve pensar?",
        placeholder="Você é um tutor especialista em Python que explica conceitos de forma simples."
    )

    # Botão para salvar o papel
    if st.button("Salvar Papel da IA"):
        st.session_state.papel_ia = papel

    # Reinicia a memória quando trocar o papel
        st.session_state.historico = [
         SystemMessage(content=papel)
    ]
    
        st.success("Papel da IA salvo com sucesso!")

    st.divider()

    pergunta = st.text_input(
        "Digite sua pergunta:",
        placeholder="Ex: O que é Inteligência Artificial?"
    )

    if st.button("Enviar Pergunta"):
        

        if not st.session_state.papel_ia:
            st.warning("Primeiro defina e salve o papel da IA.")
        
        elif not pergunta:
            st.warning("Digite uma pergunta.")

        else:
             # Adiciona pergunta ao histórico
            st.session_state.historico.append(
                HumanMessage(content=pergunta)
        )

        # Envia todo o histórico para o modelo
            resposta = modelo.invoke(
                st.session_state.historico
        )

        # Adiciona resposta ao histórico
            st.session_state.historico.append(
                AIMessage(content=resposta.content)
        )

        st.success(resposta.content)

        st.divider()

        with st.expander("Histórico da Conversa"):

            for msg in st.session_state.historico:

                if isinstance(msg, HumanMessage):
                    st.write(f"Você: {msg.content}")

                elif isinstance(msg, AIMessage):
                    st.write(f"IA: {msg.content}")

#agente de IA, utlizando o LangGraph onde seguimos um fluxo de etapas antes de gerar a resposta.

elif st.session_state.pagina_atual == "desafio3":
    
    st.title("Agente Inteligente de Classificação de Perguntas com LangGraph")

    st.write("Projeto desenvolvido durante os estudos de IA Generativa para demonstrar a construção de agentes utilizando LangGraph. O sistema analisa a intenção do usuário, classifica a pergunta e adapta a resposta ao tipo identificado, proporcionando respostas mais relevantes e contextualizadas.")
   

    class Estado (TypedDict):
        pergunta:str
        categoria:str
        resposta: str
        mensagens: List


    def classificar(state:Estado) -> Estado:
        """ Nó 1: Classifica a pergunta do usuario """
        print("Classificando a pergunta...")

        prompt = f"""Classifique a pergunta abaico em UMA das categorias:
        TECNICA, CONCEITUAL ou CURIOSIDADE.
        Responda APENAS com a palavra da categoria.
        
        Pergunta: {state['pergunta']}"""

        resposta = modelo.invoke([HumanMessage(content=prompt)])
        state["categoria"] = resposta.content.strip().upper()
        print(f"Categoria: {state['categoria']}")
        return state



    def responder(state:Estado) -> Estado:
        """ Nó 2:Gera a resposta com base na categoria """

        instrucoes = {
            "TÉCNICA": "Responda com exemplos práticos de código. Não informe a categoria da resposta.",
            "CONCEITUAL": "Explique o conceito de forma simples, sem jargões. Não informe a categoria da resposta.",
            "CURIOSIDADE" : "Responda de forma divertida e curiosa. Não informe a categoria da resposta.",

        }

        estilo = instrucoes.get(state["categoria"], "Responda de forma clara.")

        mensagens = [
            HumanMessage(content=f"{estilo}\n\nPergunts: {state['pergunta']}")
        ]

        resposta = modelo.invoke(mensagens)
        state["resposta"] = resposta.content
        state["mensagens"].append(AIMessage(content = resposta.content))
        return state

    def formatar(state:Estado) -> Estado:
        """ Nó 3 : Formata a saida final. """
        state["resposta"] = (
            f"{state['resposta']}"
        )
        return state

    grafo = StateGraph(Estado)


    #adicionado nos

    grafo.add_node("classificar", classificar)
    grafo.add_node("responder", responder)
    grafo.add_node("formatar", formatar)

    #arestas

    grafo.set_entry_point("classificar")
    grafo.add_edge("classificar", "responder")
    grafo.add_edge("responder", "formatar")
    grafo.add_edge("formatar", END)

    app = grafo.compile()

    if "historico2" not in st.session_state:
        st.session_state.historico2 = []

    pergunta = st.text_input(
        "Digite sua pergunta",
        placeholder="Faça uma pergunta técnica, conceitual ou uma curiosidade."
    )

    if st.button("Enviar") and pergunta:
        
        estado_inicial = {
            "pergunta": pergunta,
            "categoria": "",
            "resposta": "",
            "mensagens": [HumanMessage(content=pergunta)],
        }

        
        resultado = app.invoke(estado_inicial)


        st.session_state.historico2.append(
            HumanMessage(content=pergunta)
        )

        st.session_state.historico2.append(
            AIMessage(content=resultado["resposta"])
        )


        
        st.info(f"Categoria: {resultado['categoria']}")

        st.subheader("Resposta")
        st.success(resultado["resposta"])

        with st.expander("Histórico da Conversa"):

            for msg in st.session_state.historico2:

                if isinstance(msg, HumanMessage):
                    st.write(f"Você: {msg.content}")

                elif isinstance(msg, AIMessage):
                    st.write(f"IA: {msg.content}")


    