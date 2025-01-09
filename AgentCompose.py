__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM
import json

# Configurando o modelo usando a classe LLM nativa do CrewAI
gpt4o = 'gpt-4o'

llm = LLM(
    model="gpt-4",
    temperature=0.8
)

# Função para configurar o agente e executar a composição
def criar_musica(sentimentos):
    # Definindo o agente
    agent_escritor = Agent(
        role="Compositor de Música Cristã",
        goal="Escreva uma música cristã que exalte o nome de Cristo Jesus, expressando os seguintes sentimentos: {sentimentos}.",
        verbose=True,
        memory=True,
        llm=llm,
        backstory="""
            Desde jovem, você sentiu um profundo chamado para expressar sua fé e espiritualidade através da música.
            Inspirado pelos salmos, hinos e cânticos que ecoam a essência da adoração, você dedica sua vida a compor
            melodias que tocam os corações e elevam as almas. Seu conhecimento teológico, combinado com uma habilidade
            natural para traduzir emoções em música, torna cada composição uma experiência única e transformadora.
            Você acredita que a música é uma forma de oração e comunhão com Deus, e vê suas composições como uma ferramenta
            para ajudar pessoas a se conectarem espiritualmente e encontrarem paz em meio aos desafios da vida.
            Trabalhando com letras profundas e melodias inspiradoras, você busca criar canções que ressoem em congregações
            e momentos pessoais de devoção, iluminando o caminho da fé para aqueles que ouvem sua arte.
        """
    )

    # Definindo a tarefa
    tarefa_composicao = Task(
        description="""
            Crie uma música cristã inspiradora centrada em um tema específico de adoração, como amor divino, graça, ou
            renovação espiritual. A composição deve ser adequada tanto para congregações quanto para momentos de oração
            individual. A letra deve ser profundamente tocante, teologicamente fundamentada e a melodia deve ser fácil
            de cantar e memorável.
            
            Especificações:
            - Estilo musical: Contemporâneo, com influências de worship e hinos clássicos.
            - Estrutura: Inclua versos, refrão e uma ponte.
            - Tom emocional: Esperançoso, reconfortante e espiritual.
            - Mensagem central: Transmitir uma mensagem clara e positiva, como gratidão, confiança em Deus ou celebração da fé.
            - Elementos teológicos: Incorporar passagens bíblicas.
        """,
        expected_output="""
            - A letra completa da música, formatada em versos e refrão, devidamente formatada.
            - Sugestão da melodia básica em notação musical simples e uma descrição do ritmo e tom, devidamente formatada.
            - Sugestão de cifras para acompanhamento instrumental, devidamente formatada.
            - Breve descrição da intenção por trás da música e do impacto que ela busca causar nos ouvintes.
            
            O texto formatado deve seguir as seguintes regras:
  			1. Títulos e subtítulos devem estar em negrito, utilizando markdown. Exemplo: `**Título da Música:**`.
  			2. O conteúdo após os títulos deve manter espaçamento adequado e alinhamento claro.
  			3. Listas devem ser utilizadas para itens estruturados, como informações técnicas ou descrições.
  			4. Preserve a estrutura do texto original, incluindo versos, refrões e outros elementos musicais.
  			5. O resultado deve ser apresentado em formato markdown para fácil leitura e exportação.
            6. Fontes dos textos de tamanho 14 ou 16 para facilitar a leitura.
        """,
        agent=agent_escritor
    )

    # Criando a tripulação
    equipe = Crew(
        agents=[agent_escritor],
        tasks=[tarefa_composicao],
        process=Process.sequential
    )

    # Executando a tripulação
    result = equipe.kickoff(inputs={"sentimentos": sentimentos})

    return result

# Interface do Streamlit
st.title("Compositor de Música Cristã 🎵")
st.write("Crie músicas cristãs inspiradoras com base nos sentimentos desejados.")

# Entrada do usuário
sentimentos = st.text_input(
    "Digite os sentimentos que deseja incluir na música (ex.: gratidão, esperança, perdão):",
    "gratidão, esperança, perdão"
)

# Botão para gerar a música
if st.button("Gerar Música"):
    with st.spinner("Compondo a música..."):
        try:
            resultado = criar_musica(sentimentos)

            st.success("Música composta com sucesso!")

            # Processar e exibir o texto formatado
            st.markdown("### Letra da Música:")
            if isinstance(resultado, str):
                try:
                    # Tenta converter para JSON e extrair o campo `raw`
                    resultado_json = json.loads(resultado)
                    texto_formatado = resultado_json.get("raw", resultado)
                except json.JSONDecodeError:
                    # Caso não seja JSON, trata como texto normal
                    texto_formatado = resultado
            elif isinstance(resultado, dict):
                texto_formatado = resultado.get("raw", str(resultado))
            else:
                texto_formatado = str(resultado)

            # Exibir o texto formatado diretamente
            st.markdown(texto_formatado)

        except Exception as e:
            st.error("Ocorreu um erro ao compor a música.")
            st.write(str(e))
