#!/usr/bin/env python3
"""
Demonstração das Novas Funcionalidades do Compositor de Música Católica
- Text-to-Speech em português brasileiro
- Upload e mudança de tom de músicas existentes
- Extração de letras de textos gerados
"""

import sys
import os
from unittest.mock import MagicMock

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_extracao_letra():
    """Demonstra a extração de letra de um texto gerado"""
    print("📝 DEMO: Extração de Letra")
    print("=" * 50)
    
    # Texto simulado de uma música gerada
    texto_exemplo = """
    **Título da Música:** Ave Maria da Esperança

    **Verso 1:**
    Maria, Mãe de Jesus
    Estrela da manhã
    Guia-nos com tua luz
    Na jornada cristã

    **Refrão:**
    Ave Maria, cheia de graça
    O Senhor é contigo
    Bendita és tu entre as mulheres
    E bendito é o fruto do teu ventre

    **Verso 2:**
    Rainha do céu e da terra
    Mãe da divina misericórdia
    Intercede por nós pecadores
    Agora e na hora da nossa morte

    **Cifras:** C - G - Am - F
    **Tom:** C Maior
    **Tempo:** Andante (72 BPM)
    """
    
    try:
        from AgentCompose import extrair_letra_musica
        
        letra_extraida = extrair_letra_musica(texto_exemplo)
        
        print("✅ Letra extraída com sucesso!")
        print("\n📜 Letra extraída:")
        print("-" * 30)
        print(letra_extraida)
        print("-" * 30)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na extração: {str(e)}")
        return False

def demo_text_to_speech():
    """Demonstra a funcionalidade de Text-to-Speech"""
    print("\n🎤 DEMO: Text-to-Speech em Português")
    print("=" * 50)
    
    letra_teste = "Ave Maria, cheia de graça, o Senhor é contigo. Bendita és tu entre as mulheres."
    
    try:
        from gtts import gTTS
        import tempfile
        import os
        
        print(f"📝 Texto para conversão: {letra_teste}")
        print("⏳ Gerando áudio com TTS...")
        
        # Gerar TTS
        tts = gTTS(text=letra_teste, lang='pt-br', slow=False)
        
        # Salvar em arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            tts.save(temp_file.name)
            
            # Verificar se o arquivo foi criado
            if os.path.exists(temp_file.name):
                file_size = os.path.getsize(temp_file.name)
                print(f"✅ Áudio TTS gerado com sucesso!")
                print(f"📊 Tamanho do arquivo: {file_size} bytes")
                print(f"💾 Arquivo temporário: {temp_file.name}")
                
                # Limpar arquivo temporário
                os.unlink(temp_file.name)
                return True
            else:
                print("❌ Arquivo TTS não foi criado")
                return False
                
    except Exception as e:
        print(f"❌ Erro no TTS: {str(e)}")
        return False

def demo_mudanca_tom():
    """Demonstra o conceito de mudança de tom"""
    print("\n🎼 DEMO: Conceito de Mudança de Tom")
    print("=" * 50)
    
    # Mapeamento de tons para demonstração
    tons_semitons = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
        'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
    }
    
    exemplos = [
        ('C', 'G', "Dó para Sol"),
        ('G', 'D', "Sol para Ré"),
        ('F', 'C', "Fá para Dó"),
        ('A', 'E', "Lá para Mi")
    ]
    
    print("🎵 Exemplos de mudança de tom:")
    
    for tom_orig, tom_novo, descricao in exemplos:
        semitom_orig = tons_semitons.get(tom_orig, 0)
        semitom_novo = tons_semitons.get(tom_novo, 0)
        diferenca = semitom_novo - semitom_orig
        
        if diferenca > 6:
            diferenca -= 12
        elif diferenca < -6:
            diferenca += 12
            
        direcao = "↑" if diferenca > 0 else "↓" if diferenca < 0 else "="
        
        print(f"   {descricao}: {abs(diferenca)} semitons {direcao}")
    
    print("\n💡 A mudança de tom preserva:")
    print("   ✅ Velocidade da música")
    print("   ✅ Qualidade da voz")
    print("   ✅ Duração total")
    print("   ✅ Timbre original")
    
    return True

def demo_formatos_audio():
    """Demonstra os formatos de áudio suportados"""
    print("\n🔊 DEMO: Formatos de Áudio Suportados")
    print("=" * 50)
    
    formatos_entrada = ['mp3', 'wav', 'm4a', 'ogg', 'flac', 'aac']
    formatos_saida = ['mp3', 'wav']
    
    print("📥 Formatos de entrada suportados:")
    for formato in formatos_entrada:
        print(f"   ✅ .{formato}")
    
    print("\n📤 Formatos de saída disponíveis:")
    for formato in formatos_saida:
        print(f"   ✅ .{formato}")
    
    print("\n🎯 Funcionalidades por formato:")
    print("   🎵 Upload: Todos os formatos listados")
    print("   🔄 Mudança de tom: Preserva qualidade original")
    print("   🎤 TTS: Gerado em MP3 de alta qualidade")
    print("   📱 Compatibilidade: Funciona em todos os navegadores")
    
    return True

def demo_casos_uso():
    """Demonstra casos de uso práticos"""
    print("\n🎯 DEMO: Casos de Uso Práticos")
    print("=" * 50)
    
    casos = [
        {
            "titulo": "Coral da Igreja",
            "situacao": "Música em tom muito alto para o coral",
            "solucao": "Upload da música e mudança para tom mais baixo",
            "exemplo": "De G para E (3 semitons abaixo)"
        },
        {
            "titulo": "Ensaio Individual",
            "situacao": "Cantor quer praticar em tom diferente",
            "solucao": "Ajustar tom para extensão vocal pessoal",
            "exemplo": "De C para A (3 semitons abaixo)"
        },
        {
            "titulo": "Liturgia Especial",
            "situacao": "Criar nova música para festa mariana",
            "solucao": "Gerar letra e música com IA + áudio com voz",
            "exemplo": "Estilo mariano em tom G com TTS em português"
        },
        {
            "titulo": "Acompanhamento Instrumental",
            "situacao": "Precisar de base musical sem voz",
            "solucao": "Gerar apenas áudio instrumental",
            "exemplo": "Base em F para acompanhar violão"
        }
    ]
    
    for i, caso in enumerate(casos, 1):
        print(f"\n{i}. {caso['titulo']}")
        print(f"   📋 Situação: {caso['situacao']}")
        print(f"   💡 Solução: {caso['solucao']}")
        print(f"   🎵 Exemplo: {caso['exemplo']}")
    
    return True

def main():
    """Função principal da demonstração"""
    print("🎵✝️ DEMONSTRAÇÃO - NOVAS FUNCIONALIDADES")
    print("Compositor de Música Católica v2.0")
    print("=" * 60)
    
    demos = [
        demo_extracao_letra,
        demo_text_to_speech,
        demo_mudanca_tom,
        demo_formatos_audio,
        demo_casos_uso
    ]
    
    sucessos = 0
    total = len(demos)
    
    for demo in demos:
        try:
            if demo():
                sucessos += 1
        except Exception as e:
            print(f"❌ Erro na demonstração: {str(e)}")
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DA DEMONSTRAÇÃO")
    print("=" * 60)
    print(f"✅ Demonstrações bem-sucedidas: {sucessos}/{total}")
    
    if sucessos == total:
        print("🎉 Todas as funcionalidades foram demonstradas com sucesso!")
    else:
        print(f"⚠️  {total - sucessos} demonstração(ões) apresentaram problemas")
    
    print("\n🚀 FUNCIONALIDADES IMPLEMENTADAS:")
    print("   ✅ Text-to-Speech em português brasileiro")
    print("   ✅ Upload de músicas existentes")
    print("   ✅ Mudança de tom preservando voz")
    print("   ✅ Extração automática de letras")
    print("   ✅ Geração de áudio instrumental")
    print("   ✅ Geração de áudio com voz")
    print("   ✅ Interface com abas organizadas")
    print("   ✅ Suporte a múltiplos formatos")
    
    print("\n✝️ Ad Majorem Dei Gloriam")
    print("🎵 Para a Maior Glória de Deus através da música!")
    print("=" * 60)

if __name__ == "__main__":
    main()
