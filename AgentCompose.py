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
import tempfile
from gtts import gTTS
import librosa
import soundfile as sf
import re

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

# Função para extrair letra do texto gerado
def extrair_letra_musica(texto_completo):
    """Extrai apenas a letra da música do texto completo gerado"""
    try:
        # Procurar por seções de letra (versos, refrão, etc.)
        linhas = texto_completo.split('\n')
        letra_linhas = []

        # Palavras-chave que indicam seções de letra
        secoes_letra = ['verso', 'refrão', 'refrao', 'ponte', 'coro', 'estrofe']

        capturando_letra = False
        for linha in linhas:
            linha_limpa = linha.strip().lower()

            # Verificar se é uma seção de letra
            if any(secao in linha_limpa for secao in secoes_letra):
                capturando_letra = True
                continue

            # Parar se encontrar seções técnicas
            if any(palavra in linha_limpa for palavra in ['cifra', 'acorde', 'tom:', 'bpm', 'compasso']):
                capturando_letra = False
                continue

            # Capturar linhas de letra
            if capturando_letra and linha.strip() and not linha.startswith('#') and not linha.startswith('*'):
                # Remover marcações markdown
                linha_letra = re.sub(r'\*\*([^*]+)\*\*', r'\1', linha.strip())
                linha_letra = re.sub(r'\*([^*]+)\*', r'\1', linha_letra)
                if linha_letra:
                    letra_linhas.append(linha_letra)

        return ' '.join(letra_linhas) if letra_linhas else "Letra não encontrada no texto gerado."

    except Exception as e:
        return f"Erro ao extrair letra: {str(e)}"

# Função para gerar áudio com Text-to-Speech
def gerar_audio_com_voz(letra, tom, estilo, velocidade=1.0):
    """Gera áudio com voz cantando a letra em português"""
    try:
        # Gerar música instrumental
        audio_instrumental = gerar_audio_simples(tom, estilo)
        if not audio_instrumental:
            return None

        # Gerar voz com TTS
        tts = gTTS(text=letra, lang='pt-br', slow=False)

        # Salvar TTS em arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_tts:
            tts.save(temp_tts.name)

            # Carregar áudio da voz
            audio_voz = AudioSegment.from_mp3(temp_tts.name)

            # Carregar áudio instrumental
            audio_instrumental_seg = AudioSegment.from_file(io.BytesIO(audio_instrumental))

            # Ajustar velocidade da voz se necessário
            if velocidade != 1.0:
                # Simular mudança de velocidade alterando frame rate
                new_sample_rate = int(audio_voz.frame_rate * velocidade)
                audio_voz = audio_voz._spawn(audio_voz.raw_data, overrides={"frame_rate": new_sample_rate})
                audio_voz = audio_voz.set_frame_rate(audio_voz.frame_rate)

            # Ajustar volumes
            audio_instrumental_seg = audio_instrumental_seg - 10  # Diminuir volume instrumental
            audio_voz = audio_voz + 5  # Aumentar volume da voz

            # Repetir instrumental se necessário para cobrir toda a voz
            duracao_voz = len(audio_voz)
            duracao_instrumental = len(audio_instrumental_seg)

            if duracao_voz > duracao_instrumental:
                repeticoes = (duracao_voz // duracao_instrumental) + 1
                audio_instrumental_seg = audio_instrumental_seg * repeticoes

            # Cortar instrumental para duração da voz
            audio_instrumental_seg = audio_instrumental_seg[:duracao_voz]

            # Mixar voz e instrumental
            audio_final = audio_instrumental_seg.overlay(audio_voz)

            # Converter para bytes
            audio_bytes = io.BytesIO()
            audio_final.export(audio_bytes, format="mp3")
            audio_bytes.seek(0)

            # Limpar arquivo temporário
            os.unlink(temp_tts.name)

            return audio_bytes.getvalue()

    except Exception as e:
        st.error(f"Erro ao gerar áudio com voz: {str(e)}")
        return None

# Função para mudar tom de música existente
def mudar_tom_musica(audio_bytes, tom_original, tom_novo):
    """Muda o tom de uma música preservando a velocidade e qualidade da voz"""
    try:
        # Mapeamento de tons para semitons
        tons_semitons = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }

        # Calcular diferença em semitons
        semitom_original = tons_semitons.get(tom_original, 0)
        semitom_novo = tons_semitons.get(tom_novo, 0)
        diferenca_semitons = semitom_novo - semitom_original

        if diferenca_semitons == 0:
            return audio_bytes  # Sem mudança necessária

        # Salvar áudio em arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_input:
            temp_input.write(audio_bytes)
            temp_input.flush()

            # Carregar áudio com librosa
            y, sr = librosa.load(temp_input.name, sr=None)

            # Mudar tom preservando velocidade (pitch shifting)
            y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=diferenca_semitons)

            # Salvar resultado em arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_output:
                sf.write(temp_output.name, y_shifted, sr)

                # Converter de volta para AudioSegment
                audio_modificado = AudioSegment.from_wav(temp_output.name)

                # Converter para bytes
                audio_bytes_novo = io.BytesIO()
                audio_modificado.export(audio_bytes_novo, format="mp3")
                audio_bytes_novo.seek(0)

                # Limpar arquivos temporários
                os.unlink(temp_input.name)
                os.unlink(temp_output.name)

                return audio_bytes_novo.getvalue()

    except Exception as e:
        st.error(f"Erro ao mudar tom da música: {str(e)}")
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

# Abas principais
tab1, tab2 = st.tabs(["🎵 Criar Nova Música", "🎼 Modificar Música Existente"])

with tab1:
    st.subheader("📝 Composição")
    sentimentos = st.text_area(
        "Digite os sentimentos ou temas que deseja incluir na música:",
        "gratidão, esperança, paz, devoção mariana",
        height=100
    )

with tab2:
    st.subheader("🎼 Upload e Modificação de Música")

    # Upload de arquivo
    uploaded_file = st.file_uploader(
        "📁 Faça upload de uma música (MP3, WAV, M4A):",
        type=['mp3', 'wav', 'm4a', 'ogg'],
        help="Envie uma música para modificar o tom preservando a voz"
    )

    if uploaded_file is not None:
        # Mostrar informações do arquivo
        st.success(f"✅ Arquivo carregado: {uploaded_file.name}")

        # Player do áudio original
        st.audio(uploaded_file.getvalue(), format='audio/mp3')

        # Configurações para mudança de tom
        col_tom1, col_tom2 = st.columns(2)

        with col_tom1:
            tom_original_upload = st.selectbox(
                "🎼 Tom original da música:",
                tons_disponiveis,
                index=6,  # G como padrão
                key="tom_original"
            )

        with col_tom2:
            tom_novo_upload = st.selectbox(
                "🎯 Novo tom desejado:",
                tons_disponiveis,
                index=0,  # C como padrão
                key="tom_novo"
            )

        # Converter tons para formato simples
        tom_orig_simples = tom_map.get(tom_original_upload, tom_original_upload)
        tom_novo_simples = tom_map.get(tom_novo_upload, tom_novo_upload)

        # Botão para processar
        if st.button("🔄 Mudar Tom da Música", key="mudar_tom"):
            if tom_orig_simples != tom_novo_simples:
                with st.spinner(f"Mudando tom de {tom_original_upload} para {tom_novo_upload}..."):
                    try:
                        audio_modificado = mudar_tom_musica(
                            uploaded_file.getvalue(),
                            tom_orig_simples,
                            tom_novo_simples
                        )

                        if audio_modificado:
                            st.success(f"🎉 Tom alterado com sucesso de {tom_original_upload} para {tom_novo_upload}!")

                            # Player do áudio modificado
                            st.subheader("🎵 Resultado:")
                            st.audio(audio_modificado, format='audio/mp3')

                            # Botão de download
                            st.download_button(
                                label="⬇️ Download da Música Modificada",
                                data=audio_modificado,
                                file_name=f"musica_modificada_{tom_novo_simples}.mp3",
                                mime="audio/mp3"
                            )

                            # Salvar na sessão
                            st.session_state.musica_modificada = audio_modificado
                            st.session_state.tom_modificado = tom_novo_simples
                        else:
                            st.error("❌ Erro ao modificar a música.")

                    except Exception as e:
                        st.error(f"❌ Erro ao processar: {str(e)}")
            else:
                st.warning("⚠️ Os tons original e novo são iguais. Nenhuma modificação necessária.")

# Informações adicionais (fora das abas)
with st.expander("ℹ️ Informações sobre os estilos e funcionalidades"):
    st.markdown("""
    ### 🎨 Estilos Musicais:
    **Tradicional**: Hinos clássicos católicos com harmonias tradicionais
    **Contemporâneo**: Música católica moderna com instrumentação atual
    **Gregoriano**: Inspirado no canto gregoriano medieval
    **Mariano**: Focado na devoção à Virgem Maria
    **Litúrgico**: Apropriado para uso durante a Santa Missa

    ### 🔧 Funcionalidades:
    **Criar Nova Música**: Gera letra e música católica com IA
    **Modificar Música Existente**: Altera o tom de músicas já prontas preservando a voz
    **Áudio com Voz**: Gera áudio com Text-to-Speech em português brasileiro
    **Áudio Instrumental**: Gera apenas a base musical sem voz
    """)

# Botões de ação (apenas na aba de criação)
with tab1:
    # Botões de ação
    col1, col2, col3 = st.columns(3)

    with col1:
        gerar_musica = st.button("🎵 Gerar Música", type="primary", use_container_width=True)

    with col2:
        gerar_audio_instrumental = st.button("🎼 Áudio Instrumental", use_container_width=True)

    with col3:
        gerar_audio_com_letra = st.button("🎤 Áudio com Voz", use_container_width=True)

# Geração da música (aba 1)
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

            # Extrair letra para uso posterior
            letra_extraida = extrair_letra_musica(texto_formatado)

            # Salvar resultado na sessão para uso posterior
            st.session_state.ultima_musica = texto_formatado
            st.session_state.ultima_letra = letra_extraida
            st.session_state.ultimo_tom = tom
            st.session_state.ultimo_estilo = estilo

        except Exception as e:
            st.error("❌ Ocorreu um erro ao compor a música.")
            st.error(f"Detalhes do erro: {str(e)}")

# Geração de áudio instrumental (aba 1)
if gerar_audio_instrumental:
    if 'ultima_musica' not in st.session_state:
        st.warning("⚠️ Primeiro gere uma música antes de criar o áudio!")
    else:
        with st.spinner("Gerando áudio instrumental..."):
            try:
                audio_bytes = gerar_audio_simples(
                    st.session_state.get('ultimo_tom', tom),
                    st.session_state.get('ultimo_estilo', estilo)
                )

                if audio_bytes:
                    st.success("🎶 Áudio instrumental gerado com sucesso!")

                    # Player de áudio
                    st.audio(audio_bytes, format='audio/mp3')

                    # Botão de download
                    st.download_button(
                        label="⬇️ Download do Áudio Instrumental",
                        data=audio_bytes,
                        file_name=f"instrumental_{tom}_{estilo}.mp3",
                        mime="audio/mp3"
                    )
                else:
                    st.error("❌ Erro ao gerar o áudio instrumental.")

            except Exception as e:
                st.error("❌ Ocorreu um erro ao gerar o áudio instrumental.")
                st.error(f"Detalhes do erro: {str(e)}")

# Geração de áudio com voz (aba 1)
if gerar_audio_com_letra:
    if 'ultima_letra' not in st.session_state:
        st.warning("⚠️ Primeiro gere uma música antes de criar o áudio com voz!")
    else:
        with st.spinner("Gerando áudio com voz em português..."):
            try:
                letra = st.session_state.get('ultima_letra', '')

                if not letra or letra == "Letra não encontrada no texto gerado.":
                    st.error("❌ Letra não encontrada. Tente gerar a música novamente.")
                else:
                    # Mostrar letra que será cantada
                    with st.expander("📝 Letra que será cantada:"):
                        st.write(letra)

                    audio_bytes = gerar_audio_com_voz(
                        letra,
                        st.session_state.get('ultimo_tom', tom),
                        st.session_state.get('ultimo_estilo', estilo)
                    )

                    if audio_bytes:
                        st.success("🎤 Áudio com voz gerado com sucesso!")

                        # Player de áudio
                        st.audio(audio_bytes, format='audio/mp3')

                        # Botão de download
                        st.download_button(
                            label="⬇️ Download do Áudio com Voz",
                            data=audio_bytes,
                            file_name=f"musica_com_voz_{tom}_{estilo}.mp3",
                            mime="audio/mp3"
                        )
                    else:
                        st.error("❌ Erro ao gerar o áudio com voz.")

            except Exception as e:
                st.error("❌ Ocorreu um erro ao gerar o áudio com voz.")
                st.error(f"Detalhes do erro: {str(e)}")

# Rodapé
st.markdown("---")
st.markdown("🙏 *Que esta música possa elevar corações a Deus e honrar Nossa Senhora*")
st.markdown("✝️ *Ad Majorem Dei Gloriam*")
