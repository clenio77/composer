#!/usr/bin/env python3
"""
Exemplo de uso do Compositor de Música Católica
Este arquivo demonstra como usar as funcionalidades principais do sistema.
"""

from AgentCompose import criar_musica, gerar_audio_simples
import json

def exemplo_basico():
    """Exemplo básico de geração de música católica"""
    print("🎵 Exemplo Básico - Música Católica")
    print("=" * 50)
    
    # Parâmetros de exemplo
    sentimentos = "gratidão, devoção mariana, paz interior"
    tom = "G"
    estilo = "mariano"
    
    print(f"Sentimentos: {sentimentos}")
    print(f"Tom: {tom}")
    print(f"Estilo: {estilo}")
    print("\n⏳ Gerando música...")
    
    try:
        # Gerar a música
        resultado = criar_musica(sentimentos, tom, estilo)
        
        # Processar resultado
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
        
        print("\n✅ Música gerada com sucesso!")
        print("=" * 50)
        print(texto_formatado)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar música: {str(e)}")
        return False

def exemplo_audio():
    """Exemplo de geração de áudio"""
    print("\n🔊 Exemplo de Geração de Áudio")
    print("=" * 50)
    
    tom = "C"
    estilo = "tradicional"
    
    print(f"Tom: {tom}")
    print(f"Estilo: {estilo}")
    print("\n⏳ Gerando áudio...")
    
    try:
        audio_bytes = gerar_audio_simples(tom, estilo)
        
        if audio_bytes:
            print("✅ Áudio gerado com sucesso!")
            print(f"📊 Tamanho do arquivo: {len(audio_bytes)} bytes")
            
            # Salvar arquivo de exemplo
            with open(f"exemplo_audio_{tom}_{estilo}.mp3", "wb") as f:
                f.write(audio_bytes)
            print(f"💾 Arquivo salvo como: exemplo_audio_{tom}_{estilo}.mp3")
            
            return True
        else:
            print("❌ Erro ao gerar áudio")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao gerar áudio: {str(e)}")
        return False

def exemplo_multiplos_estilos():
    """Exemplo com múltiplos estilos católicos"""
    print("\n🎨 Exemplo - Múltiplos Estilos Católicos")
    print("=" * 50)
    
    estilos = [
        ("tradicional", "C", "adoração eucarística, reverência"),
        ("contemporâneo", "D", "alegria, comunidade, louvor"),
        ("gregoriano", "F", "contemplação, silêncio, oração"),
        ("mariano", "G", "devoção mariana, proteção maternal"),
        ("litúrgico", "A", "celebração, comunhão, festa")
    ]
    
    for estilo, tom, sentimentos in estilos:
        print(f"\n🎼 Estilo: {estilo.upper()}")
        print(f"   Tom: {tom}")
        print(f"   Sentimentos: {sentimentos}")
        
        # Simular geração (sem executar para economizar tempo)
        print(f"   ✅ Configuração válida para {estilo}")

def mostrar_configuracoes():
    """Mostra as configurações disponíveis"""
    print("\n⚙️ Configurações Disponíveis")
    print("=" * 50)
    
    tons = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    estilos = [
        "tradicional - Hinos clássicos católicos",
        "contemporâneo - Música católica moderna", 
        "gregoriano - Inspiração medieval",
        "mariano - Devoção à Nossa Senhora",
        "litúrgico - Para celebrações da Missa"
    ]
    
    print("🎼 Tons Musicais Disponíveis:")
    for i, tom in enumerate(tons, 1):
        print(f"   {i:2d}. {tom}")
    
    print("\n🎨 Estilos Católicos Disponíveis:")
    for i, estilo in enumerate(estilos, 1):
        print(f"   {i}. {estilo}")
    
    print("\n💡 Exemplos de Sentimentos/Temas:")
    temas = [
        "gratidão, esperança, paz",
        "devoção mariana, proteção maternal",
        "adoração eucarística, reverência",
        "alegria, comunidade, celebração",
        "contemplação, silêncio interior",
        "perdão, misericórdia, reconciliação",
        "fé, confiança, entrega a Deus"
    ]
    
    for i, tema in enumerate(temas, 1):
        print(f"   {i}. {tema}")

def main():
    """Função principal com menu de exemplos"""
    print("🎵✝️ COMPOSITOR DE MÚSICA CATÓLICA - EXEMPLOS")
    print("=" * 60)
    print("Este arquivo demonstra as funcionalidades do sistema.")
    print("=" * 60)
    
    # Mostrar configurações
    mostrar_configuracoes()
    
    # Exemplo com múltiplos estilos
    exemplo_multiplos_estilos()
    
    # Exemplo de áudio
    exemplo_audio()
    
    print("\n" + "=" * 60)
    print("✝️ Ad Majorem Dei Gloriam - Para a Maior Glória de Deus")
    print("🎵 Que esta ferramenta sirva para elevar corações a Deus")
    print("=" * 60)

if __name__ == "__main__":
    main()
