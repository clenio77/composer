__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM
import json
import numpy as np
import pygame
from pydub import AudioSegment
from pydub.generators import Sine
import io
import base64

# Configurando o modelo usando a classe LLM nativa do CrewAI
gpt4o = 'gpt-4o-mini'

llm = LLM(
    model="gpt-4",
    temperature=0.8
)

# Função para gerar áudio simples baseado no tom
def gerar_audio_simples(tom, estilo="tradicional"):
    """Gera um áudio simples baseado no tom selecionado"""
    try:
        # Mapeamento de tons para frequências (em Hz)
        tons_freq = {
            "C": 261.63, "C#": 277.18, "Db": 277.18,
            "D": 293.66, "D#": 311.13, "Eb": 311.13,
            "E": 329.63, "F": 349.23, "F#": 369.99, "Gb": 369.99,
            "G": 392.00, "G#": 415.30, "Ab": 415.30,
            "A": 440.00, "A#": 466.16, "Bb": 466.16,
            "B": 493.88
        }

        freq_base = tons_freq.get(tom, 440.00)

        # Criar uma progressão simples baseada no estilo
        if estilo == "tradicional":
            # Progressão I-V-vi-IV (muito comum em música católica)
            acordes = [freq_base, freq_base * 1.5, freq_base * 1.68, freq_base * 1.33]
        else:  # contemporâneo
            # Progressão vi-IV-I-V
            acordes = [freq_base * 1.68, freq_base * 1.33, freq_base, freq_base * 1.5]

        # Gerar áudio
        audio_final = AudioSegment.empty()

        for freq in acordes:
            # Gerar tom por 2 segundos
            tom_audio = Sine(freq).to_audio_segment(duration=2000)
            # Adicionar fade in/out para suavizar
            tom_audio = tom_audio.fade_in(100).fade_out(100)
            audio_final += tom_audio

        # Converter para bytes
        audio_bytes = io.BytesIO()
        audio_final.export(audio_bytes, format="mp3")
        audio_bytes.seek(0)

        return audio_bytes.getvalue()

    except Exception as e:
        st.error(f"Erro ao gerar áudio: {str(e)}")
        return None

# Função para configurar o agente e executar a composição
def criar_musica(sentimentos, tom, estilo):
    # Definindo o agente
    agent_escritor = Agent(
        role="Compositor de Música Católica",
        goal="Escreva uma música católica que honre a Santíssima Trindade, a Virgem Maria e os Santos, expressando os seguintes sentimentos: {sentimentos}. A música deve estar no tom {tom} e seguir o estilo {estilo}.",
        verbose=True,
        memory=True,
        llm=llm,
        backstory="""
            Você é um compositor católico devoto, formado em música sacra e teologia. Desde a juventude, você se dedica
            à composição de música litúrgica e devocional, inspirado pela rica tradição musical da Igreja Católica.
            Seu conhecimento abrange desde o canto gregoriano até a música católica contemporânea, passando pelos grandes
            mestres como Palestrina, Bach e os compositores de música sacra moderna.

            Você compreende profundamente a liturgia católica, os tempos litúrgicos, as devoções marianas e a veneração
            aos santos. Suas composições refletem a doutrina católica, incorporando elementos da Escritura Sagrada,
            da Tradição da Igreja e do Magistério. Você busca criar música que eleve as almas a Deus, honre Nossa Senhora
            e inspire os fiéis em sua jornada de fé.

            Sua especialidade inclui hinos marianos, cantos litúrgicos, música para adoração eucarística e canções
            devocionais que respeitem a tradição católica enquanto tocam o coração dos fiéis contemporâneos.
        """
    )

    # Definindo a tarefa
    tarefa_composicao = Task(
        description=f"""
            Crie uma música católica inspiradora que honre a tradição da Igreja Católica. A composição deve ser adequada
            para uso litúrgico, devocional ou em momentos de oração pessoal. A letra deve ser teologicamente sólida,
            respeitando a doutrina católica, e a melodia deve ser adequada para o canto congregacional.

            Especificações:
            - Tom musical: {tom} (todas as cifras devem estar neste tom)
            - Estilo musical: {estilo}
            - Estrutura: Inclua versos, refrão e uma ponte (se apropriado para o estilo)
            - Tom emocional: Reverente, esperançoso e espiritualmente edificante
            - Elementos católicos: Incorporar referências à Santíssima Trindade, Virgem Maria, Santos, Eucaristia ou liturgia
            - Tradição: Respeitar a rica tradição musical católica
            - Sentimentos a expressar: {sentimentos}
        """,
        expected_output=f"""
            - Responder, obrigatoriamente, no idioma Português Brasileiro.
            - A letra completa da música católica, formatada em versos e refrão.
            - Todas as cifras devem estar no tom {tom} especificado.
            - Sugestão da melodia básica adequada ao estilo {estilo}.
            - Cifras completas para acompanhamento instrumental no tom {tom}.
            - Indicação de tempo litúrgico apropriado (se aplicável).
            - Referências bíblicas ou doutrinais utilizadas.
            - Breve descrição da intenção espiritual e uso litúrgico recomendado.

            O texto formatado deve seguir as seguintes regras:
  			1. Títulos e subtítulos devem estar em negrito, utilizando markdown.
  			2. O conteúdo deve manter espaçamento adequado e alinhamento claro.
  			3. Listas devem ser utilizadas para informações estruturadas.
  			4. Preserve a estrutura musical (versos, refrões, ponte).
  			5. O resultado deve ser apresentado em formato markdown.
            6. Incluir seção específica com as cifras no tom {tom}.
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
    result = equipe.kickoff(inputs={
        "sentimentos": sentimentos,
        "tom": tom,
        "estilo": estilo
    })

    return result

# Interface do Streamlit
st.title("Compositor de Música Católica 🎵✝️")
st.write("Crie músicas católicas inspiradoras para liturgia, devoção e oração.")

# Sidebar para configurações
st.sidebar.header("⚙️ Configurações da Música")

# Seleção de tom
tons_disponiveis = [
    "C", "C#/Db", "D", "D#/Eb", "E", "F",
    "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"
]
tom_selecionado = st.sidebar.selectbox(
    "🎼 Selecione o tom da música:",
    tons_disponiveis,
    index=6  # G como padrão
)

# Converter tom para formato simples
tom_map = {
    "C#/Db": "C#", "D#/Eb": "D#", "F#/Gb": "F#", "G#/Ab": "G#", "A#/Bb": "A#"
}
tom = tom_map.get(tom_selecionado, tom_selecionado)

# Seleção de estilo
estilos_disponiveis = [
    "Tradicional (Hinos Clássicos)",
    "Contemporâneo (Música Católica Moderna)",
    "Gregoriano (Inspiração Medieval)",
    "Mariano (Devoção à Nossa Senhora)",
    "Litúrgico (Para Missa)"
]
estilo_selecionado = st.sidebar.selectbox(
    "🎨 Selecione o estilo musical:",
    estilos_disponiveis,
    index=0
)

# Mapear estilo para formato simples
estilo_map = {
    "Tradicional (Hinos Clássicos)": "tradicional",
    "Contemporâneo (Música Católica Moderna)": "contemporâneo",
    "Gregoriano (Inspiração Medieval)": "gregoriano",
    "Mariano (Devoção à Nossa Senhora)": "mariano",
    "Litúrgico (Para Missa)": "litúrgico"
}
estilo = estilo_map[estilo_selecionado]

# Entrada principal
st.subheader("📝 Composição")
sentimentos = st.text_area(
    "Digite os sentimentos ou temas que deseja incluir na música:",
    "gratidão, esperança, paz, devoção mariana",
    height=100
)

# Informações adicionais
with st.expander("ℹ️ Informações sobre os estilos"):
    st.markdown("""
    **Tradicional**: Hinos clássicos católicos com harmonias tradicionais
    **Contemporâneo**: Música católica moderna com instrumentação atual
    **Gregoriano**: Inspirado no canto gregoriano medieval
    **Mariano**: Focado na devoção à Virgem Maria
    **Litúrgico**: Apropriado para uso durante a Santa Missa
    """)

# Botões de ação
col1, col2 = st.columns(2)

with col1:
    gerar_musica = st.button("🎵 Gerar Música", type="primary", use_container_width=True)

with col2:
    gerar_audio = st.button("🔊 Gerar Áudio", use_container_width=True)

# Geração da música
if gerar_musica:
    with st.spinner("Compondo a música católica..."):
        try:
            resultado = criar_musica(sentimentos, tom, estilo)

            st.success("🎉 Música católica composta com sucesso!")

            # Processar e exibir o texto formatado
            st.markdown("### 📜 Composição Musical")
            if isinstance(resultado, str):
                try:
                    resultado_json = json.loads(resultado)
                    texto_formatado = resultado_json.get("raw", resultado)
                except json.JSONDecodeError:
                    texto_formatado = resultado
            elif isinstance(resultado, dict):
                texto_formatado = resultado.get("raw", str(resultado))
            else:
                texto_formatado = str(resultado)

            # Exibir o texto formatado
            st.markdown(texto_formatado)

            # Salvar resultado na sessão para uso posterior
            st.session_state.ultima_musica = texto_formatado
            st.session_state.ultimo_tom = tom
            st.session_state.ultimo_estilo = estilo

        except Exception as e:
            st.error("❌ Ocorreu um erro ao compor a música.")
            st.error(f"Detalhes do erro: {str(e)}")

# Geração de áudio
if gerar_audio:
    if 'ultima_musica' not in st.session_state:
        st.warning("⚠️ Primeiro gere uma música antes de criar o áudio!")
    else:
        with st.spinner("Gerando áudio da música..."):
            try:
                audio_bytes = gerar_audio_simples(
                    st.session_state.get('ultimo_tom', tom),
                    st.session_state.get('ultimo_estilo', estilo)
                )

                if audio_bytes:
                    st.success("🎶 Áudio gerado com sucesso!")

                    # Player de áudio
                    st.audio(audio_bytes, format='audio/mp3')

                    # Botão de download
                    st.download_button(
                        label="⬇️ Download do Áudio",
                        data=audio_bytes,
                        file_name=f"musica_catolica_{tom}_{estilo}.mp3",
                        mime="audio/mp3"
                    )
                else:
                    st.error("❌ Erro ao gerar o áudio.")

            except Exception as e:
                st.error("❌ Ocorreu um erro ao gerar o áudio.")
                st.error(f"Detalhes do erro: {str(e)}")

# Rodapé
st.markdown("---")
st.markdown("🙏 *Que esta música possa elevar corações a Deus e honrar Nossa Senhora*")
st.markdown("✝️ *Ad Majorem Dei Gloriam*")
