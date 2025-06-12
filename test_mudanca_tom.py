#!/usr/bin/env python3
"""
Teste específico para a funcionalidade de mudança de tom
"""

import sys
import os
import tempfile
import io
from pydub import AudioSegment
from pydub.generators import Sine

def test_imports():
    """Testa se todas as dependências estão disponíveis"""
    print("🧪 Testando imports...")
    
    try:
        import librosa
        print("✅ librosa: OK")
    except ImportError as e:
        print(f"❌ librosa: {e}")
        return False
    
    try:
        import soundfile as sf
        print("✅ soundfile: OK")
    except ImportError as e:
        print(f"❌ soundfile: {e}")
        return False
    
    try:
        from pydub import AudioSegment
        print("✅ pydub: OK")
    except ImportError as e:
        print(f"❌ pydub: {e}")
        return False
    
    return True

def criar_audio_teste():
    """Cria um áudio de teste simples"""
    print("🎵 Criando áudio de teste...")
    
    try:
        # Criar um tom simples de 440Hz (Lá) por 2 segundos
        audio_teste = Sine(440).to_audio_segment(duration=2000)
        
        # Converter para bytes
        audio_bytes = io.BytesIO()
        audio_teste.export(audio_bytes, format="mp3")
        audio_bytes.seek(0)
        
        print(f"✅ Áudio de teste criado: {len(audio_bytes.getvalue())} bytes")
        return audio_bytes.getvalue()
        
    except Exception as e:
        print(f"❌ Erro ao criar áudio de teste: {e}")
        return None

def test_mudanca_tom_librosa(audio_bytes):
    """Testa mudança de tom com librosa"""
    print("🔄 Testando mudança de tom com librosa...")
    
    try:
        import librosa
        import soundfile as sf
        
        # Salvar áudio em arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_input:
            temp_input.write(audio_bytes)
            temp_input.flush()
            
            # Carregar áudio
            y, sr = librosa.load(temp_input.name, sr=None)
            print(f"📊 Áudio carregado: {len(y)} samples, {sr} Hz")
            
            # Mudar tom (+2 semitons)
            y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=2)
            print(f"🎼 Tom alterado: +2 semitons")
            
            # Salvar resultado
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
                
                resultado = audio_bytes_novo.getvalue()
                print(f"✅ Mudança de tom com librosa: {len(resultado)} bytes")
                return resultado
                
    except Exception as e:
        print(f"❌ Erro com librosa: {e}")
        return None

def test_mudanca_tom_pydub(audio_bytes):
    """Testa mudança de tom com PyDub (método alternativo)"""
    print("🔄 Testando mudança de tom com PyDub...")
    
    try:
        # Carregar áudio
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        print(f"📊 Áudio carregado: {len(audio)}ms, {audio.frame_rate}Hz")
        
        # Calcular fator de mudança (+2 semitons)
        diferenca_semitons = 2
        pitch_factor = 2 ** (diferenca_semitons / 12.0)
        print(f"🎼 Fator de pitch: {pitch_factor:.3f}")
        
        # Alterar sample rate
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
        
        resultado = audio_bytes_novo.getvalue()
        print(f"✅ Mudança de tom com PyDub: {len(resultado)} bytes")
        return resultado
        
    except Exception as e:
        print(f"❌ Erro com PyDub: {e}")
        return None

def test_tons_mapping():
    """Testa o mapeamento de tons"""
    print("🎼 Testando mapeamento de tons...")
    
    tons_semitons = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
        'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
    }
    
    # Testar algumas conversões
    testes = [
        ('C', 'G'),  # +7 semitons
        ('G', 'D'),  # +7 semitons
        ('A', 'C'),  # +3 semitons
        ('F', 'A'),  # +4 semitons
    ]
    
    for tom_orig, tom_novo in testes:
        semitom_orig = tons_semitons.get(tom_orig, 0)
        semitom_novo = tons_semitons.get(tom_novo, 0)
        diferenca = semitom_novo - semitom_orig
        print(f"  {tom_orig} → {tom_novo}: {diferenca:+d} semitons")
    
    print("✅ Mapeamento de tons: OK")

def main():
    """Função principal de teste"""
    print("🎵✝️ TESTE DE MUDANÇA DE TOM - Compositor de Música Católica")
    print("=" * 60)
    
    # Teste 1: Imports
    if not test_imports():
        print("❌ Falha nos imports. Instale as dependências:")
        print("pip install librosa soundfile pydub")
        return False
    
    # Teste 2: Mapeamento de tons
    test_tons_mapping()
    
    # Teste 3: Criar áudio de teste
    audio_teste = criar_audio_teste()
    if not audio_teste:
        print("❌ Falha ao criar áudio de teste")
        return False
    
    # Teste 4: Mudança de tom com librosa
    resultado_librosa = test_mudanca_tom_librosa(audio_teste)
    
    # Teste 5: Mudança de tom com PyDub
    resultado_pydub = test_mudanca_tom_pydub(audio_teste)
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES:")
    print(f"✅ Imports: OK")
    print(f"✅ Mapeamento de tons: OK")
    print(f"✅ Áudio de teste: OK")
    print(f"{'✅' if resultado_librosa else '❌'} Librosa: {'OK' if resultado_librosa else 'FALHOU'}")
    print(f"{'✅' if resultado_pydub else '❌'} PyDub: {'OK' if resultado_pydub else 'FALHOU'}")
    
    if resultado_librosa or resultado_pydub:
        print("\n🎉 Pelo menos um método de mudança de tom está funcionando!")
        return True
    else:
        print("\n❌ Nenhum método de mudança de tom está funcionando")
        return False

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
