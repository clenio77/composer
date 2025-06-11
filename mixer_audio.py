#!/usr/bin/env python3
"""
Mixer de Áudio Avançado
Controles profissionais de áudio para música católica
"""

from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range, low_pass_filter, high_pass_filter
from pydub.generators import Sine, WhiteNoise
import numpy as np
import io
import tempfile
import os

class MixerAudio:
    """Classe para mixagem avançada de áudio"""
    
    def __init__(self):
        self.presets_ambiente = {
            "capela_pequena": {
                "reverb_decay": 1.2,
                "reverb_wet": 0.15,
                "eq_low": 0,
                "eq_mid": 2,
                "eq_high": -1,
                "compressor_threshold": -18,
                "descricao": "Som intimista de capela pequena"
            },
            "igreja_grande": {
                "reverb_decay": 2.5,
                "reverb_wet": 0.25,
                "eq_low": 1,
                "eq_mid": 0,
                "eq_high": 1,
                "compressor_threshold": -20,
                "descricao": "Reverb amplo de igreja grande"
            },
            "catedral": {
                "reverb_decay": 4.0,
                "reverb_wet": 0.35,
                "eq_low": 2,
                "eq_mid": -1,
                "eq_high": 0,
                "compressor_threshold": -22,
                "descricao": "Reverb majestoso de catedral"
            },
            "sala_ensaio": {
                "reverb_decay": 0.8,
                "reverb_wet": 0.08,
                "eq_low": 0,
                "eq_mid": 1,
                "eq_high": 2,
                "compressor_threshold": -16,
                "descricao": "Som seco para ensaios"
            },
            "gravacao_estudio": {
                "reverb_decay": 0.5,
                "reverb_wet": 0.05,
                "eq_low": 0,
                "eq_mid": 0,
                "eq_high": 1,
                "compressor_threshold": -14,
                "descricao": "Som limpo de estúdio"
            }
        }
        
        self.presets_estilo = {
            "gregoriano": {
                "volume_voz": 8,
                "volume_instrumental": -15,
                "eq_voz_low": -2,
                "eq_voz_mid": 3,
                "eq_voz_high": 1,
                "ambiente": "catedral"
            },
            "tradicional": {
                "volume_voz": 5,
                "volume_instrumental": -8,
                "eq_voz_low": 0,
                "eq_voz_mid": 2,
                "eq_voz_high": 1,
                "ambiente": "igreja_grande"
            },
            "contemporâneo": {
                "volume_voz": 3,
                "volume_instrumental": -5,
                "eq_voz_low": 1,
                "eq_voz_mid": 1,
                "eq_voz_high": 2,
                "ambiente": "capela_pequena"
            },
            "mariano": {
                "volume_voz": 6,
                "volume_instrumental": -10,
                "eq_voz_low": -1,
                "eq_voz_mid": 4,
                "eq_voz_high": 0,
                "ambiente": "igreja_grande"
            },
            "litúrgico": {
                "volume_voz": 4,
                "volume_instrumental": -12,
                "eq_voz_low": 0,
                "eq_voz_mid": 3,
                "eq_voz_high": -1,
                "ambiente": "catedral"
            }
        }
    
    def aplicar_preset_estilo(self, audio_voz_bytes, audio_instrumental_bytes, estilo):
        """Aplica preset de mixagem baseado no estilo católico"""
        try:
            if estilo not in self.presets_estilo:
                estilo = "tradicional"
            
            preset = self.presets_estilo[estilo]
            
            # Carregar áudios
            seg_voz = AudioSegment.from_file(io.BytesIO(audio_voz_bytes))
            seg_instrumental = AudioSegment.from_file(io.BytesIO(audio_instrumental_bytes))
            
            # Aplicar volumes
            seg_voz = seg_voz + preset["volume_voz"]
            seg_instrumental = seg_instrumental + preset["volume_instrumental"]
            
            # Aplicar EQ na voz
            seg_voz = self._aplicar_eq_basico(
                seg_voz,
                preset["eq_voz_low"],
                preset["eq_voz_mid"],
                preset["eq_voz_high"]
            )
            
            # Aplicar ambiente
            ambiente = preset["ambiente"]
            seg_voz = self._aplicar_reverb_simulado(seg_voz, ambiente)
            seg_instrumental = self._aplicar_reverb_simulado(seg_instrumental, ambiente)
            
            # Mixar
            audio_final = self._mixar_audios(seg_voz, seg_instrumental)
            
            # Aplicar compressão final
            preset_ambiente = self.presets_ambiente[ambiente]
            audio_final = self._aplicar_compressao(audio_final, preset_ambiente["compressor_threshold"])
            
            # Normalizar
            audio_final = normalize(audio_final)
            
            # Converter para bytes
            audio_bytes = io.BytesIO()
            audio_final.export(audio_bytes, format="mp3")
            audio_bytes.seek(0)
            
            return audio_bytes.getvalue()
            
        except Exception as e:
            print(f"Erro ao aplicar preset de estilo: {str(e)}")
            return None
    
    def mixagem_personalizada(self, audio_voz_bytes, audio_instrumental_bytes,
                            volume_voz=5, volume_instrumental=-8,
                            eq_voz_low=0, eq_voz_mid=2, eq_voz_high=1,
                            eq_inst_low=0, eq_inst_mid=0, eq_inst_high=0,
                            reverb_amount=0.15, compressor_threshold=-18):
        """Mixagem com controles personalizados"""
        try:
            # Carregar áudios
            seg_voz = AudioSegment.from_file(io.BytesIO(audio_voz_bytes))
            seg_instrumental = AudioSegment.from_file(io.BytesIO(audio_instrumental_bytes))
            
            # Aplicar volumes
            seg_voz = seg_voz + volume_voz
            seg_instrumental = seg_instrumental + volume_instrumental
            
            # Aplicar EQ
            seg_voz = self._aplicar_eq_basico(seg_voz, eq_voz_low, eq_voz_mid, eq_voz_high)
            seg_instrumental = self._aplicar_eq_basico(seg_instrumental, eq_inst_low, eq_inst_mid, eq_inst_high)
            
            # Aplicar reverb
            if reverb_amount > 0:
                seg_voz = self._aplicar_reverb_personalizado(seg_voz, reverb_amount)
                seg_instrumental = self._aplicar_reverb_personalizado(seg_instrumental, reverb_amount * 0.7)
            
            # Mixar
            audio_final = self._mixar_audios(seg_voz, seg_instrumental)
            
            # Aplicar compressão
            if compressor_threshold > -30:
                audio_final = self._aplicar_compressao(audio_final, compressor_threshold)
            
            # Normalizar
            audio_final = normalize(audio_final)
            
            # Converter para bytes
            audio_bytes = io.BytesIO()
            audio_final.export(audio_bytes, format="mp3")
            audio_bytes.seek(0)
            
            return audio_bytes.getvalue()
            
        except Exception as e:
            print(f"Erro na mixagem personalizada: {str(e)}")
            return None
    
    def _aplicar_eq_basico(self, audio, low_gain, mid_gain, high_gain):
        """Aplica equalização básica de 3 bandas"""
        try:
            audio_processado = audio
            
            # EQ Low (80-250 Hz) - simulado com filtro passa-baixa
            if low_gain != 0:
                if low_gain > 0:
                    # Boost nos graves
                    audio_low = low_pass_filter(audio, 250)
                    audio_low = audio_low + (low_gain * 2)
                    audio_processado = audio_processado.overlay(audio_low - 10)
                else:
                    # Cut nos graves
                    audio_processado = high_pass_filter(audio_processado, 100)
            
            # EQ High (4kHz+) - simulado com filtro passa-alta
            if high_gain != 0:
                if high_gain > 0:
                    # Boost nos agudos
                    audio_high = high_pass_filter(audio, 4000)
                    audio_high = audio_high + (high_gain * 2)
                    audio_processado = audio_processado.overlay(audio_high - 10)
                else:
                    # Cut nos agudos
                    audio_processado = low_pass_filter(audio_processado, 8000)
            
            # Mid boost/cut (simulação básica)
            if mid_gain != 0:
                audio_processado = audio_processado + (mid_gain * 0.5)
            
            return audio_processado
            
        except Exception as e:
            print(f"Erro ao aplicar EQ: {str(e)}")
            return audio
    
    def _aplicar_reverb_simulado(self, audio, tipo_ambiente):
        """Simula reverb baseado no tipo de ambiente"""
        try:
            if tipo_ambiente not in self.presets_ambiente:
                return audio
            
            preset = self.presets_ambiente[tipo_ambiente]
            return self._aplicar_reverb_personalizado(audio, preset["reverb_wet"])
            
        except Exception as e:
            print(f"Erro ao aplicar reverb simulado: {str(e)}")
            return audio
    
    def _aplicar_reverb_personalizado(self, audio, wet_amount):
        """Aplica reverb personalizado (simulação básica)"""
        try:
            if wet_amount <= 0:
                return audio
            
            # Simular reverb com delay e feedback
            delay_ms = int(50 + (wet_amount * 200))  # 50-250ms de delay
            
            # Criar versão com delay
            audio_delay = AudioSegment.silent(duration=delay_ms) + audio
            audio_delay = audio_delay - (20 - int(wet_amount * 15))  # Reduzir volume do delay
            
            # Mixar original com delay
            duracao_maxima = max(len(audio), len(audio_delay))
            
            if len(audio) < duracao_maxima:
                audio += AudioSegment.silent(duracao_maxima - len(audio))
            if len(audio_delay) < duracao_maxima:
                audio_delay += AudioSegment.silent(duracao_maxima - len(audio_delay))
            
            audio_com_reverb = audio.overlay(audio_delay)
            
            return audio_com_reverb
            
        except Exception as e:
            print(f"Erro ao aplicar reverb personalizado: {str(e)}")
            return audio
    
    def _aplicar_compressao(self, audio, threshold_db):
        """Aplica compressão dinâmica"""
        try:
            # Usar compressão da pydub
            audio_comprimido = compress_dynamic_range(
                audio,
                threshold=threshold_db,
                ratio=4.0,
                attack=5.0,
                release=50.0
            )
            return audio_comprimido
            
        except Exception as e:
            print(f"Erro ao aplicar compressão: {str(e)}")
            return audio
    
    def _mixar_audios(self, audio_voz, audio_instrumental):
        """Mixa dois áudios ajustando durações"""
        try:
            duracao_voz = len(audio_voz)
            duracao_instrumental = len(audio_instrumental)
            
            # Ajustar duração do instrumental
            if duracao_voz > duracao_instrumental:
                # Repetir instrumental se necessário
                repeticoes = (duracao_voz // duracao_instrumental) + 1
                audio_instrumental = audio_instrumental * repeticoes
            
            # Cortar instrumental para duração da voz
            audio_instrumental = audio_instrumental[:duracao_voz]
            
            # Mixar
            audio_final = audio_instrumental.overlay(audio_voz)
            
            return audio_final
            
        except Exception as e:
            print(f"Erro ao mixar áudios: {str(e)}")
            return audio_voz
    
    def criar_fade_in_out(self, audio_bytes, fade_in_ms=1000, fade_out_ms=1000):
        """Aplica fade in e fade out"""
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            
            # Aplicar fades
            audio_com_fade = audio.fade_in(fade_in_ms).fade_out(fade_out_ms)
            
            # Converter para bytes
            audio_bytes_resultado = io.BytesIO()
            audio_com_fade.export(audio_bytes_resultado, format="mp3")
            audio_bytes_resultado.seek(0)
            
            return audio_bytes_resultado.getvalue()
            
        except Exception as e:
            print(f"Erro ao aplicar fade: {str(e)}")
            return audio_bytes
    
    def obter_presets_disponiveis(self):
        """Retorna presets disponíveis"""
        return {
            "ambientes": {
                nome: config["descricao"] 
                for nome, config in self.presets_ambiente.items()
            },
            "estilos": {
                nome: f"Preset otimizado para {nome}" 
                for nome in self.presets_estilo.keys()
            }
        }
    
    def analisar_audio(self, audio_bytes):
        """Analisa características do áudio"""
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            
            analise = {
                "duracao_segundos": len(audio) / 1000,
                "volume_medio_db": audio.dBFS,
                "pico_db": audio.max_dBFS,
                "canais": audio.channels,
                "sample_rate": audio.frame_rate,
                "formato_recomendado": "mp3" if len(audio) > 30000 else "wav"
            }
            
            # Recomendações baseadas na análise
            recomendacoes = []
            
            if analise["volume_medio_db"] < -25:
                recomendacoes.append("Áudio muito baixo - considere aumentar o volume")
            elif analise["volume_medio_db"] > -10:
                recomendacoes.append("Áudio muito alto - considere reduzir o volume")
            
            if analise["pico_db"] > -3:
                recomendacoes.append("Picos altos detectados - recomenda-se compressão")
            
            analise["recomendacoes"] = recomendacoes
            
            return analise
            
        except Exception as e:
            print(f"Erro ao analisar áudio: {str(e)}")
            return None

# Função de conveniência
def criar_mixer_audio():
    """Retorna uma instância do mixer de áudio"""
    return MixerAudio()

# Teste básico
if __name__ == "__main__":
    mixer = MixerAudio()
    
    print("🎚️ MIXER DE ÁUDIO AVANÇADO")
    print("=" * 35)
    
    # Listar presets
    presets = mixer.obter_presets_disponiveis()
    
    print("🏛️ Ambientes disponíveis:")
    for nome, descricao in presets["ambientes"].items():
        print(f"  - {nome}: {descricao}")
    
    print("\n🎵 Estilos disponíveis:")
    for nome, descricao in presets["estilos"].items():
        print(f"  - {nome}: {descricao}")
    
    print("\n✅ Mixer de áudio inicializado com sucesso!")
    print("🎛️ Funcionalidades disponíveis:")
    print("  - Presets por estilo católico")
    print("  - Mixagem personalizada")
    print("  - EQ de 3 bandas")
    print("  - Reverb simulado")
    print("  - Compressão dinâmica")
    print("  - Fade in/out")
    print("  - Análise de áudio")
