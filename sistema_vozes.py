#!/usr/bin/env python3
"""
Sistema de Múltiplas Vozes
Gerencia diferentes tipos de voz para Text-to-Speech
"""

from gtts import gTTS
import tempfile
import os
import io
from pydub import AudioSegment
from pydub.effects import speedup, normalize
import random

class SistemaVozes:
    """Classe para gerenciar múltiplas vozes de TTS"""
    
    def __init__(self):
        self.tipos_voz = {
            "feminina_adulta": {
                "lang": "pt-br",
                "slow": False,
                "pitch_adjust": 0,
                "speed_adjust": 1.0,
                "descricao": "Voz feminina adulta padrão"
            },
            "masculina_adulta": {
                "lang": "pt-br", 
                "slow": False,
                "pitch_adjust": -3,  # Mais grave
                "speed_adjust": 0.9,  # Mais lento
                "descricao": "Voz masculina adulta"
            },
            "infantil": {
                "lang": "pt-br",
                "slow": False,
                "pitch_adjust": 4,   # Mais agudo
                "speed_adjust": 1.1, # Mais rápido
                "descricao": "Voz infantil para catequese"
            },
            "solene": {
                "lang": "pt-br",
                "slow": True,        # Mais devagar
                "pitch_adjust": -1,
                "speed_adjust": 0.8, # Bem mais lento
                "descricao": "Voz solene para liturgia"
            },
            "jovem_feminina": {
                "lang": "pt-br",
                "slow": False,
                "pitch_adjust": 2,   # Ligeiramente mais agudo
                "speed_adjust": 1.05,
                "descricao": "Voz jovem feminina"
            },
            "jovem_masculina": {
                "lang": "pt-br",
                "slow": False,
                "pitch_adjust": -1,  # Ligeiramente mais grave
                "speed_adjust": 1.0,
                "descricao": "Voz jovem masculina"
            }
        }
        
        # Configurações de coro
        self.configuracoes_coro = {
            "coro_misto": ["feminina_adulta", "masculina_adulta"],
            "coro_infantil": ["infantil"],
            "coro_jovem": ["jovem_feminina", "jovem_masculina"],
            "coro_feminino": ["feminina_adulta", "jovem_feminina"],
            "coro_masculino": ["masculina_adulta", "jovem_masculina"],
            "solista_liturgico": ["solene"]
        }
    
    def gerar_audio_com_voz(self, texto, tipo_voz="feminina_adulta", velocidade_custom=None):
        """Gera áudio com tipo de voz específico"""
        try:
            if tipo_voz not in self.tipos_voz:
                tipo_voz = "feminina_adulta"
            
            config_voz = self.tipos_voz[tipo_voz]
            
            # Gerar TTS básico
            tts = gTTS(
                text=texto,
                lang=config_voz["lang"],
                slow=config_voz["slow"]
            )
            
            # Salvar em arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                tts.save(temp_file.name)
                
                # Carregar áudio
                audio = AudioSegment.from_mp3(temp_file.name)
                
                # Aplicar ajustes de voz
                audio_processado = self._aplicar_ajustes_voz(audio, config_voz, velocidade_custom)
                
                # Converter para bytes
                audio_bytes = io.BytesIO()
                audio_processado.export(audio_bytes, format="mp3")
                audio_bytes.seek(0)
                
                # Limpar arquivo temporário
                os.unlink(temp_file.name)
                
                return audio_bytes.getvalue()
                
        except Exception as e:
            print(f"Erro ao gerar áudio com voz {tipo_voz}: {str(e)}")
            return None
    
    def _aplicar_ajustes_voz(self, audio, config_voz, velocidade_custom=None):
        """Aplica ajustes de pitch e velocidade ao áudio"""
        try:
            audio_processado = audio
            
            # Ajustar velocidade
            velocidade = velocidade_custom if velocidade_custom else config_voz["speed_adjust"]
            if velocidade != 1.0:
                # Simular mudança de velocidade alterando frame rate
                new_sample_rate = int(audio.frame_rate * velocidade)
                audio_processado = audio_processado._spawn(
                    audio_processado.raw_data,
                    overrides={"frame_rate": new_sample_rate}
                )
                audio_processado = audio_processado.set_frame_rate(audio.frame_rate)
            
            # Ajustar pitch (simulação básica através de velocidade)
            pitch_adjust = config_voz["pitch_adjust"]
            if pitch_adjust != 0:
                # Ajuste de pitch através de mudança de velocidade
                pitch_factor = 1.0 + (pitch_adjust * 0.05)  # 5% por semitom
                new_sample_rate = int(audio_processado.frame_rate * pitch_factor)
                audio_processado = audio_processado._spawn(
                    audio_processado.raw_data,
                    overrides={"frame_rate": new_sample_rate}
                )
                audio_processado = audio_processado.set_frame_rate(audio.frame_rate)
            
            # Normalizar áudio
            audio_processado = normalize(audio_processado)
            
            return audio_processado
            
        except Exception as e:
            print(f"Erro ao aplicar ajustes de voz: {str(e)}")
            return audio
    
    def gerar_coro_virtual(self, texto, tipo_coro="coro_misto", delay_entre_vozes=500):
        """Gera um coro virtual com múltiplas vozes"""
        try:
            if tipo_coro not in self.configuracoes_coro:
                tipo_coro = "coro_misto"
            
            vozes_coro = self.configuracoes_coro[tipo_coro]
            audios_vozes = []
            
            # Gerar áudio para cada voz
            for i, tipo_voz in enumerate(vozes_coro):
                # Adicionar pequenas variações para naturalidade
                velocidade_variacao = 1.0 + random.uniform(-0.05, 0.05)
                
                audio_voz = self.gerar_audio_com_voz(
                    texto, 
                    tipo_voz, 
                    velocidade_variacao
                )
                
                if audio_voz:
                    audio_seg = AudioSegment.from_file(io.BytesIO(audio_voz))
                    
                    # Adicionar delay entre vozes para efeito de coro
                    if i > 0:
                        silencio = AudioSegment.silent(duration=delay_entre_vozes * i)
                        audio_seg = silencio + audio_seg
                    
                    audios_vozes.append(audio_seg)
            
            if not audios_vozes:
                return None
            
            # Mixar todas as vozes
            audio_final = audios_vozes[0]
            for audio_voz in audios_vozes[1:]:
                # Ajustar duração para mixagem
                duracao_maxima = max(len(audio_final), len(audio_voz))
                
                # Estender áudios se necessário
                if len(audio_final) < duracao_maxima:
                    audio_final += AudioSegment.silent(duracao_maxima - len(audio_final))
                if len(audio_voz) < duracao_maxima:
                    audio_voz += AudioSegment.silent(duracao_maxima - len(audio_voz))
                
                # Mixar com volume reduzido para evitar distorção
                audio_final = audio_final.overlay(audio_voz - 3)  # -3dB por voz adicional
            
            # Normalizar resultado final
            audio_final = normalize(audio_final)
            
            # Converter para bytes
            audio_bytes = io.BytesIO()
            audio_final.export(audio_bytes, format="mp3")
            audio_bytes.seek(0)
            
            return audio_bytes.getvalue()
            
        except Exception as e:
            print(f"Erro ao gerar coro virtual: {str(e)}")
            return None
    
    def gerar_audio_responsorial(self, texto_solista, texto_assembleia, 
                                tipo_voz_solista="solene", tipo_coro="coro_misto"):
        """Gera áudio responsorial (solista + assembleia)"""
        try:
            # Gerar áudio do solista
            audio_solista = self.gerar_audio_com_voz(texto_solista, tipo_voz_solista)
            if not audio_solista:
                return None
            
            # Gerar áudio da assembleia (coro)
            audio_assembleia = self.gerar_coro_virtual(texto_assembleia, tipo_coro)
            if not audio_assembleia:
                return None
            
            # Converter para AudioSegment
            seg_solista = AudioSegment.from_file(io.BytesIO(audio_solista))
            seg_assembleia = AudioSegment.from_file(io.BytesIO(audio_assembleia))
            
            # Adicionar pausa entre solista e assembleia
            pausa = AudioSegment.silent(duration=1000)  # 1 segundo
            
            # Combinar: solista + pausa + assembleia
            audio_final = seg_solista + pausa + seg_assembleia
            
            # Converter para bytes
            audio_bytes = io.BytesIO()
            audio_final.export(audio_bytes, format="mp3")
            audio_bytes.seek(0)
            
            return audio_bytes.getvalue()
            
        except Exception as e:
            print(f"Erro ao gerar áudio responsorial: {str(e)}")
            return None
    
    def obter_tipos_voz_disponiveis(self):
        """Retorna lista de tipos de voz disponíveis"""
        return {
            tipo: config["descricao"] 
            for tipo, config in self.tipos_voz.items()
        }
    
    def obter_tipos_coro_disponiveis(self):
        """Retorna tipos de coro disponíveis"""
        descricoes_coro = {
            "coro_misto": "Coro misto (vozes femininas e masculinas)",
            "coro_infantil": "Coro infantil para catequese",
            "coro_jovem": "Coro jovem",
            "coro_feminino": "Coro feminino",
            "coro_masculino": "Coro masculino",
            "solista_liturgico": "Solista para liturgia solene"
        }
        return descricoes_coro
    
    def gerar_audio_com_instrumental(self, texto, tipo_voz, audio_instrumental_bytes, 
                                   volume_voz=5, volume_instrumental=-10):
        """Combina voz com instrumental"""
        try:
            # Gerar áudio da voz
            audio_voz = self.gerar_audio_com_voz(texto, tipo_voz)
            if not audio_voz:
                return None
            
            # Carregar áudios
            seg_voz = AudioSegment.from_file(io.BytesIO(audio_voz))
            seg_instrumental = AudioSegment.from_file(io.BytesIO(audio_instrumental_bytes))
            
            # Ajustar volumes
            seg_voz = seg_voz + volume_voz
            seg_instrumental = seg_instrumental + volume_instrumental
            
            # Ajustar durações
            duracao_voz = len(seg_voz)
            duracao_instrumental = len(seg_instrumental)
            
            # Repetir instrumental se necessário
            if duracao_voz > duracao_instrumental:
                repeticoes = (duracao_voz // duracao_instrumental) + 1
                seg_instrumental = seg_instrumental * repeticoes
            
            # Cortar instrumental para duração da voz
            seg_instrumental = seg_instrumental[:duracao_voz]
            
            # Mixar
            audio_final = seg_instrumental.overlay(seg_voz)
            
            # Converter para bytes
            audio_bytes = io.BytesIO()
            audio_final.export(audio_bytes, format="mp3")
            audio_bytes.seek(0)
            
            return audio_bytes.getvalue()
            
        except Exception as e:
            print(f"Erro ao combinar voz com instrumental: {str(e)}")
            return None

# Função de conveniência
def criar_sistema_vozes():
    """Retorna uma instância do sistema de vozes"""
    return SistemaVozes()

# Teste básico
if __name__ == "__main__":
    sistema = SistemaVozes()
    
    print("🎤 SISTEMA DE MÚLTIPLAS VOZES")
    print("=" * 35)
    
    # Listar tipos de voz
    print("Tipos de voz disponíveis:")
    for tipo, descricao in sistema.obter_tipos_voz_disponiveis().items():
        print(f"  - {tipo}: {descricao}")
    
    print("\nTipos de coro disponíveis:")
    for tipo, descricao in sistema.obter_tipos_coro_disponiveis().items():
        print(f"  - {tipo}: {descricao}")
    
    # Teste básico de geração
    texto_teste = "Ave Maria, cheia de graça"
    
    try:
        print(f"\n🎵 Testando voz feminina...")
        audio_feminino = sistema.gerar_audio_com_voz(texto_teste, "feminina_adulta")
        if audio_feminino:
            print(f"✅ Áudio feminino gerado: {len(audio_feminino)} bytes")
        
        print(f"\n🎵 Testando voz masculina...")
        audio_masculino = sistema.gerar_audio_com_voz(texto_teste, "masculina_adulta")
        if audio_masculino:
            print(f"✅ Áudio masculino gerado: {len(audio_masculino)} bytes")
            
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
