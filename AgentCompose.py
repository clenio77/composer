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
from datetime import datetime

# Importar módulos personalizados
try:
    from calendario_liturgico import CalendarioLiturgico
    from gerador_partituras import GeradorPartituras
    from sistema_vozes import SistemaVozes
    from sistema_favoritos import SistemaFavoritos
    from mixer_audio import MixerAudio
except ImportError as e:
    st.error(f"Erro ao importar módulos: {str(e)}")
    st.stop()

# Configurando o modelo usando a classe LLM nativa do CrewAI
gpt4o = 'gpt-4o-mini'

llm = LLM(
    model="gpt-4",
    temperature=0.8
)

# Inicializar sistemas
@st.cache_resource
def inicializar_sistemas():
    """Inicializa todos os sistemas do compositor"""
    return {
        "calendario": CalendarioLiturgico(),
        "partituras": GeradorPartituras(),
        "vozes": SistemaVozes(),
        "favoritos": SistemaFavoritos(),
        "mixer": MixerAudio()
    }

# Obter sistemas
sistemas = inicializar_sistemas()

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
        # Verificar se as bibliotecas necessárias estão disponíveis
        try:
            import librosa
            import soundfile as sf
        except ImportError as e:
            st.error(f"❌ Bibliotecas necessárias não encontradas: {str(e)}")
            st.error("💡 Instale as dependências: pip install librosa soundfile")
            return None

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
            st.info("ℹ️ Os tons são iguais. Nenhuma modificação necessária.")
            return audio_bytes  # Sem mudança necessária

        st.info(f"🎵 Alterando tom: {diferenca_semitons:+d} semitons")

        # Criar arquivos temporários
        temp_input = None
        temp_output = None

        try:
            # Salvar áudio em arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_input:
                temp_input.write(audio_bytes)
                temp_input.flush()

                st.info("📁 Carregando áudio...")

                # Carregar áudio com librosa
                y, sr = librosa.load(temp_input.name, sr=None)

                st.info(f"🎼 Processando áudio: {len(y)} samples, {sr} Hz")

                # Verificar se o áudio foi carregado corretamente
                if len(y) == 0:
                    st.error("❌ Áudio vazio ou corrompido")
                    return None

                # Mudar tom preservando velocidade (pitch shifting)
                st.info("🔄 Aplicando mudança de tom...")
                y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=diferenca_semitons)

                # Salvar resultado em arquivo temporário
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_output:
                    sf.write(temp_output.name, y_shifted, sr)

                    st.info("🎵 Convertendo para MP3...")

                    # Converter de volta para AudioSegment
                    audio_modificado = AudioSegment.from_wav(temp_output.name)

                    # Converter para bytes
                    audio_bytes_novo = io.BytesIO()
                    audio_modificado.export(audio_bytes_novo, format="mp3")
                    audio_bytes_novo.seek(0)

                    return audio_bytes_novo.getvalue()

        finally:
            # Limpar arquivos temporários
            try:
                if temp_input and os.path.exists(temp_input.name):
                    os.unlink(temp_input.name)
                if temp_output and os.path.exists(temp_output.name):
                    os.unlink(temp_output.name)
            except Exception as cleanup_error:
                st.warning(f"⚠️ Erro ao limpar arquivos temporários: {str(cleanup_error)}")

    except ImportError as e:
        st.error(f"❌ Erro de importação: {str(e)}")
        st.error("💡 Algumas bibliotecas podem não estar instaladas no ambiente de produção.")
        st.info("🔄 Tentando método alternativo...")
        return mudar_tom_alternativo(audio_bytes, tom_original, tom_novo)

    except Exception as e:
        st.error(f"❌ Erro ao mudar tom da música: {str(e)}")
        st.error(f"🔍 Tipo do erro: {type(e).__name__}")
        st.info("🔄 Tentando método alternativo...")
        return mudar_tom_alternativo(audio_bytes, tom_original, tom_novo)

# Função alternativa para mudança de tom (usando apenas PyDub)
def mudar_tom_alternativo(audio_bytes, tom_original, tom_novo):
    """Método alternativo para mudança de tom usando apenas PyDub"""
    try:
        st.info("🔄 Usando método alternativo (PyDub)...")

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
            return audio_bytes

        # Carregar áudio com PyDub
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))

        # Calcular fator de mudança de pitch (aproximação)
        # Cada semitom = 2^(1/12) ≈ 1.059463
        pitch_factor = 2 ** (diferenca_semitons / 12.0)

        # Alterar sample rate para simular mudança de pitch
        new_sample_rate = int(audio.frame_rate * pitch_factor)

        # Aplicar mudança
        audio_modificado = audio._spawn(
            audio.raw_data,
            overrides={"frame_rate": new_sample_rate}
        ).set_frame_rate(audio.frame_rate)

        # Converter para bytes
        audio_bytes_novo = io.BytesIO()
        audio_modificado.export(audio_bytes_novo, format="mp3")
        audio_bytes_novo.seek(0)

        st.success("✅ Tom alterado usando método alternativo!")
        st.warning("⚠️ Nota: O método alternativo pode alterar ligeiramente a velocidade.")

        return audio_bytes_novo.getvalue()

    except Exception as e:
        st.error(f"❌ Erro no método alternativo: {str(e)}")
        st.error("💡 Tente fazer upload de um arquivo de áudio diferente.")
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
st.set_page_config(
    page_title="Compositor de Música Católica",
    page_icon="🎵✝️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎵✝️ Compositor de Música Católica")
st.markdown("*Crie e modifique músicas católicas com IA avançada*")

# Obter informações litúrgicas
info_liturgica = sistemas["calendario"].obter_informacoes_completas()

# Exibir informações litúrgicas no topo
col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.info(f"📅 **{info_liturgica['tempo']}** - Ano {info_liturgica['ano_liturgico']}")
with col_info2:
    st.success(f"🎨 **Estilo Sugerido:** {info_liturgica['estilo_sugerido'].title()}")
with col_info3:
    santo_hoje = sistemas["calendario"].obter_santos_do_dia()
    if santo_hoje:
        st.warning(f"✝️ **{santo_hoje}**")
    else:
        st.warning(f"🎵 **Temas:** {info_liturgica['temas_sugeridos']}")

# Sidebar para configurações
st.sidebar.header("⚙️ Configurações Musicais")

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

# Abas principais expandidas
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎵 Criar Nova Música",
    "🎼 Modificar Existente",
    "💾 Favoritos & Playlists",
    "🎚️ Mixer Avançado",
    "📊 Estatísticas"
])

with tab1:
    st.subheader("📝 Composição Musical")

    # Usar sugestões litúrgicas
    col_sugest1, col_sugest2 = st.columns(2)
    with col_sugest1:
        usar_sugestoes = st.checkbox(
            f"📅 Usar sugestões para {info_liturgica['tempo']}",
            value=True,
            help="Usar temas e estilo sugeridos para o tempo litúrgico atual"
        )

    with col_sugest2:
        if usar_sugestoes:
            st.info(f"🎨 Estilo: {info_liturgica['estilo_sugerido'].title()}")

    # Campo de sentimentos/temas
    if usar_sugestoes:
        sentimentos_default = info_liturgica['temas_sugeridos']
        estilo_default = info_liturgica['estilo_sugerido']
    else:
        sentimentos_default = "gratidão, esperança, paz, devoção mariana"
        estilo_default = estilo

    sentimentos = st.text_area(
        "Digite os sentimentos ou temas que deseja incluir na música:",
        sentimentos_default,
        height=100
    )

    # Configurações avançadas
    with st.expander("🔧 Configurações Avançadas"):
        col_config1, col_config2 = st.columns(2)

        with col_config1:
            incluir_partituras = st.checkbox("🎼 Gerar partituras", value=True)
            incluir_cifras_detalhadas = st.checkbox("🎸 Cifras detalhadas", value=True)

        with col_config2:
            incluir_coro_satb = st.checkbox("🎭 Arranjo para coro SATB", value=False)
            salvar_automaticamente = st.checkbox("💾 Salvar automaticamente", value=True)

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

# Aba 3: Favoritos e Playlists
with tab3:
    st.subheader("💾 Favoritos e Playlists")

    # Sub-abas para organizar
    subtab1, subtab2, subtab3 = st.tabs(["⭐ Favoritos", "📋 Playlists", "📚 Biblioteca"])

    with subtab1:
        st.write("### ⭐ Suas Músicas Favoritas")
        favoritos = sistemas["favoritos"].obter_favoritos()

        if favoritos:
            for musica in favoritos[:5]:  # Mostrar apenas 5 primeiras
                with st.expander(f"🎵 {musica['titulo']} ({musica['tom']} - {musica['estilo']})"):
                    st.write(f"**Data:** {musica['data_criacao'][:10]}")
                    st.write(f"**Reproduções:** {musica['contador_reproducoes']}")
                    if st.button(f"▶️ Reproduzir", key=f"play_{musica['id']}"):
                        musica_completa = sistemas["favoritos"].obter_musica(musica['id'])
                        if 'audio_bytes' in musica_completa:
                            st.audio(musica_completa['audio_bytes'], format='audio/mp3')
        else:
            st.info("Nenhuma música nos favoritos ainda. Crie uma música e adicione aos favoritos!")

    with subtab2:
        st.write("### 📋 Suas Playlists")

        # Criar nova playlist
        with st.expander("➕ Criar Nova Playlist"):
            nome_playlist = st.text_input("Nome da playlist:")
            desc_playlist = st.text_area("Descrição (opcional):")
            if st.button("Criar Playlist"):
                if nome_playlist:
                    playlist_id = sistemas["favoritos"].criar_playlist(nome_playlist, desc_playlist)
                    if playlist_id:
                        st.success(f"✅ Playlist '{nome_playlist}' criada com sucesso!")
                        st.rerun()

        # Listar playlists existentes
        playlists = sistemas["favoritos"].listar_playlists()
        for playlist in playlists[:3]:  # Mostrar apenas 3 primeiras
            with st.expander(f"📋 {playlist['nome']} ({playlist['quantidade_musicas']} músicas)"):
                st.write(f"**Descrição:** {playlist['descricao']}")
                st.write(f"**Criada em:** {playlist['data_criacao'][:10]}")
                st.write(f"**Reproduções:** {playlist['contador_reproducoes']}")

    with subtab3:
        st.write("### 📚 Biblioteca Completa")

        # Filtros
        col_filtro1, col_filtro2 = st.columns(2)
        with col_filtro1:
            filtro_estilo = st.selectbox("Filtrar por estilo:", ["Todos"] + list(set([m['estilo'] for m in sistemas["favoritos"].listar_musicas()])))
        with col_filtro2:
            filtro_tom = st.selectbox("Filtrar por tom:", ["Todos"] + list(set([m['tom'] for m in sistemas["favoritos"].listar_musicas()])))

        # Aplicar filtros
        filtro_estilo_real = None if filtro_estilo == "Todos" else filtro_estilo
        filtro_tom_real = None if filtro_tom == "Todos" else filtro_tom

        musicas_filtradas = sistemas["favoritos"].listar_musicas(
            filtro_estilo=filtro_estilo_real,
            filtro_tom=filtro_tom_real
        )

        st.write(f"**{len(musicas_filtradas)} música(s) encontrada(s)**")

        for musica in musicas_filtradas[:10]:  # Mostrar apenas 10 primeiras
            col_info, col_acoes = st.columns([3, 1])
            with col_info:
                st.write(f"🎵 **{musica['titulo']}** - {musica['tom']} ({musica['estilo']})")
                st.caption(f"Criada em {musica['data_criacao'][:10]} • {musica['contador_reproducoes']} reproduções")
            with col_acoes:
                if st.button("⭐", key=f"fav_{musica['id']}", help="Adicionar aos favoritos"):
                    sistemas["favoritos"].adicionar_aos_favoritos(musica['id'])
                    st.success("Adicionado aos favoritos!")

# Aba 4: Mixer Avançado
with tab4:
    st.subheader("🎚️ Mixer de Áudio Avançado")

    st.info("💡 **Dica:** Primeiro gere uma música com voz e instrumental, depois use o mixer para ajustar o som.")

    # Verificar se há áudios na sessão
    if 'ultima_letra' in st.session_state and 'ultimo_tom' in st.session_state:

        # Presets de ambiente
        col_preset1, col_preset2 = st.columns(2)
        with col_preset1:
            presets_disponiveis = sistemas["mixer"].obter_presets_disponiveis()
            ambiente_selecionado = st.selectbox(
                "🏛️ Ambiente acústico:",
                list(presets_disponiveis["ambientes"].keys()),
                format_func=lambda x: presets_disponiveis["ambientes"][x]
            )

        with col_preset2:
            estilo_mixer = st.selectbox(
                "🎨 Preset de estilo:",
                list(presets_disponiveis["estilos"].keys()),
                format_func=lambda x: presets_disponiveis["estilos"][x]
            )

        # Controles manuais
        with st.expander("🎛️ Controles Manuais"):
            col_vol1, col_vol2 = st.columns(2)
            with col_vol1:
                volume_voz = st.slider("🎤 Volume da Voz", -20, 20, 5)
                eq_voz_low = st.slider("🔊 EQ Voz - Graves", -10, 10, 0)
                eq_voz_mid = st.slider("🔊 EQ Voz - Médios", -10, 10, 2)
                eq_voz_high = st.slider("🔊 EQ Voz - Agudos", -10, 10, 1)

            with col_vol2:
                volume_instrumental = st.slider("🎼 Volume Instrumental", -30, 10, -8)
                reverb_amount = st.slider("🌊 Reverb", 0.0, 1.0, 0.15)
                compressor = st.slider("🗜️ Compressor", -30, -5, -18)
                fade_duration = st.slider("⏳ Fade In/Out (ms)", 0, 5000, 1000)

        # Botão para aplicar mixagem
        if st.button("🎚️ Aplicar Mixagem Avançada", type="primary"):
            with st.spinner("Aplicando mixagem profissional..."):
                try:
                    # Gerar áudios base se não existirem
                    letra = st.session_state.get('ultima_letra', '')
                    tom_atual = st.session_state.get('ultimo_tom', 'C')
                    estilo_atual = st.session_state.get('ultimo_estilo', 'tradicional')

                    # Gerar áudio da voz
                    audio_voz = sistemas["vozes"].gerar_audio_com_voz(letra, "feminina_adulta")
                    audio_instrumental = gerar_audio_simples(tom_atual, estilo_atual)

                    if audio_voz and audio_instrumental:
                        # Aplicar mixagem personalizada
                        audio_mixado = sistemas["mixer"].mixagem_personalizada(
                            audio_voz, audio_instrumental,
                            volume_voz=volume_voz,
                            volume_instrumental=volume_instrumental,
                            eq_voz_low=eq_voz_low,
                            eq_voz_mid=eq_voz_mid,
                            eq_voz_high=eq_voz_high,
                            reverb_amount=reverb_amount,
                            compressor_threshold=compressor
                        )

                        if audio_mixado:
                            # Aplicar fade
                            if fade_duration > 0:
                                audio_final = sistemas["mixer"].criar_fade_in_out(
                                    audio_mixado, fade_duration, fade_duration
                                )
                            else:
                                audio_final = audio_mixado

                            st.success("🎉 Mixagem aplicada com sucesso!")

                            # Player
                            st.audio(audio_final, format='audio/mp3')

                            # Download
                            st.download_button(
                                label="⬇️ Download da Mixagem",
                                data=audio_final,
                                file_name=f"mixagem_{ambiente_selecionado}_{tom_atual}.mp3",
                                mime="audio/mp3"
                            )

                            # Análise do áudio
                            analise = sistemas["mixer"].analisar_audio(audio_final)
                            if analise:
                                with st.expander("📊 Análise do Áudio"):
                                    col_analise1, col_analise2 = st.columns(2)
                                    with col_analise1:
                                        st.metric("Duração", f"{analise['duracao_segundos']:.1f}s")
                                        st.metric("Volume Médio", f"{analise['volume_medio_db']:.1f} dB")
                                    with col_analise2:
                                        st.metric("Pico Máximo", f"{analise['pico_db']:.1f} dB")
                                        st.metric("Sample Rate", f"{analise['sample_rate']} Hz")

                                    if analise['recomendacoes']:
                                        st.warning("⚠️ Recomendações:")
                                        for rec in analise['recomendacoes']:
                                            st.write(f"• {rec}")
                        else:
                            st.error("❌ Erro na mixagem")
                    else:
                        st.error("❌ Erro ao gerar áudios base")

                except Exception as e:
                    st.error(f"❌ Erro na mixagem: {str(e)}")
    else:
        st.warning("⚠️ Primeiro crie uma música na aba 'Criar Nova Música' para usar o mixer.")

# Aba 5: Estatísticas
with tab5:
    st.subheader("📊 Estatísticas e Análises")

    # Obter estatísticas
    stats = sistemas["favoritos"].obter_estatisticas()

    # Métricas principais
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

    with col_stat1:
        st.metric("🎵 Total de Músicas", stats['total_musicas'])

    with col_stat2:
        st.metric("⭐ Favoritos", stats['total_favoritos'])

    with col_stat3:
        st.metric("📋 Playlists", stats['total_playlists'])

    with col_stat4:
        st.metric("🎨 Estilo Favorito", stats['estilo_mais_usado'][0])

    # Informações litúrgicas
    st.write("### 📅 Informações Litúrgicas")
    col_lit1, col_lit2 = st.columns(2)

    with col_lit1:
        st.info(f"""
        **Tempo Atual:** {info_liturgica['tempo']}
        **Ano Litúrgico:** {info_liturgica['ano_liturgico']}
        **Data:** {info_liturgica['data_atual']}
        """)

    with col_lit2:
        st.success(f"""
        **Estilo Sugerido:** {info_liturgica['estilo_sugerido'].title()}
        **Temas Recomendados:** {info_liturgica['temas_sugeridos']}
        """)

    # Histórico recente
    st.write("### 📈 Atividade Recente")
    historico = sistemas["favoritos"].obter_historico(10)

    if historico:
        for entrada in historico[:5]:
            acao_emoji = {
                "criacao": "🎵",
                "reproducao": "▶️",
                "favorito_adicionado": "⭐",
                "favorito_removido": "💔"
            }
            emoji = acao_emoji.get(entrada['acao'], "📝")

            st.write(f"{emoji} **{entrada['titulo_musica']}** - {entrada['acao']} em {entrada['timestamp'][:10]}")
    else:
        st.info("Nenhuma atividade registrada ainda.")

    # Dicas e sugestões
    st.write("### 💡 Dicas e Sugestões")

    # Sugestões baseadas no tempo litúrgico
    sugestoes_liturgicas = sistemas["calendario"].obter_sugestoes_musicais_detalhadas()

    with st.expander("🎼 Sugestões para o Tempo Litúrgico Atual"):
        st.write(f"**Tons Recomendados:** {', '.join(sugestoes_liturgicas['tons_recomendados'])}")
        st.write(f"**Instrumentação:** {', '.join(sugestoes_liturgicas['instrumentacao'])}")
        if sugestoes_liturgicas['santo_do_dia']:
            st.write(f"**Santo do Dia:** {sugestoes_liturgicas['santo_do_dia']}")

# Rodapé
st.markdown("---")
st.markdown("🙏 *Que esta música possa elevar corações a Deus e honrar Nossa Senhora*")
st.markdown("✝️ *Ad Majorem Dei Gloriam*")
