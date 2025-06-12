#!/usr/bin/env python3
"""
Teste específico para verificar se st.set_page_config() está na posição correta
"""

import sys
import os
import subprocess
import time

def test_streamlit_syntax():
    """Testa se o arquivo tem sintaxe válida"""
    print("🧪 Testando sintaxe do arquivo...")
    
    try:
        with open('AgentCompose.py', 'r') as f:
            code = f.read()
        
        # Compilar código para verificar sintaxe
        compile(code, 'AgentCompose.py', 'exec')
        print("✅ Sintaxe: OK")
        return True
        
    except SyntaxError as e:
        print(f"❌ Erro de sintaxe: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_streamlit_config_position():
    """Verifica se st.set_page_config() está na posição correta"""
    print("🔍 Verificando posição de st.set_page_config()...")
    
    try:
        with open('AgentCompose.py', 'r') as f:
            lines = f.readlines()
        
        # Encontrar linha com st.set_page_config
        config_line = None
        first_streamlit_call = None
        
        for i, line in enumerate(lines):
            if 'st.set_page_config' in line:
                config_line = i + 1
                print(f"📍 st.set_page_config encontrado na linha {config_line}")
            elif line.strip().startswith('st.') and 'st.set_page_config' not in line and first_streamlit_call is None:
                first_streamlit_call = i + 1
                print(f"📍 Primeira chamada Streamlit na linha {first_streamlit_call}: {line.strip()[:50]}...")
        
        if config_line is None:
            print("❌ st.set_page_config não encontrado!")
            return False
        
        if first_streamlit_call and config_line > first_streamlit_call:
            print(f"❌ st.set_page_config (linha {config_line}) deve vir antes de outras chamadas Streamlit (linha {first_streamlit_call})")
            return False
        
        print("✅ Posição de st.set_page_config: OK")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar posição: {e}")
        return False

def test_streamlit_run():
    """Testa se o Streamlit consegue iniciar a aplicação"""
    print("🚀 Testando inicialização do Streamlit...")
    
    try:
        # Executar streamlit run com timeout
        cmd = ['streamlit', 'run', 'AgentCompose.py', '--server.headless=true', '--server.port=8502']
        
        print(f"📝 Executando: {' '.join(cmd)}")
        
        # Iniciar processo
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguardar alguns segundos para inicialização
        time.sleep(10)
        
        # Verificar se processo ainda está rodando
        if process.poll() is None:
            print("✅ Streamlit iniciou com sucesso!")
            process.terminate()
            process.wait()
            return True
        else:
            # Processo terminou, verificar saída
            stdout, stderr = process.communicate()
            print(f"❌ Streamlit falhou ao iniciar")
            print(f"📤 STDOUT: {stdout[:500]}...")
            print(f"📤 STDERR: {stderr[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar Streamlit: {e}")
        return False

def test_imports():
    """Testa se todos os imports estão funcionando"""
    print("📦 Testando imports...")
    
    try:
        # Testar imports principais
        import streamlit as st
        print("✅ streamlit: OK")
        
        import crewai
        print("✅ crewai: OK")
        
        import pydub
        print("✅ pydub: OK")
        
        import librosa
        print("✅ librosa: OK")
        
        import soundfile
        print("✅ soundfile: OK")
        
        # Testar imports dos módulos personalizados
        try:
            from calendario_liturgico import CalendarioLiturgico
            print("✅ calendario_liturgico: OK")
        except ImportError as e:
            print(f"⚠️ calendario_liturgico: {e}")
        
        try:
            from gerador_partituras import GeradorPartituras
            print("✅ gerador_partituras: OK")
        except ImportError as e:
            print(f"⚠️ gerador_partituras: {e}")
        
        try:
            from sistema_vozes import SistemaVozes
            print("✅ sistema_vozes: OK")
        except ImportError as e:
            print(f"⚠️ sistema_vozes: {e}")
        
        try:
            from sistema_favoritos import SistemaFavoritos
            print("✅ sistema_favoritos: OK")
        except ImportError as e:
            print(f"⚠️ sistema_favoritos: {e}")
        
        try:
            from mixer_audio import MixerAudio
            print("✅ mixer_audio: OK")
        except ImportError as e:
            print(f"⚠️ mixer_audio: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🎵✝️ TESTE DE CONFIGURAÇÃO STREAMLIT - Compositor de Música Católica")
    print("=" * 70)
    
    # Teste 1: Sintaxe
    if not test_streamlit_syntax():
        print("❌ Falha no teste de sintaxe")
        return False
    
    # Teste 2: Imports
    if not test_imports():
        print("❌ Falha no teste de imports")
        return False
    
    # Teste 3: Posição do st.set_page_config
    if not test_streamlit_config_position():
        print("❌ Falha no teste de posição do st.set_page_config")
        return False
    
    # Teste 4: Inicialização do Streamlit
    if not test_streamlit_run():
        print("❌ Falha no teste de inicialização do Streamlit")
        return False
    
    # Resumo
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS TESTES:")
    print("✅ Sintaxe: OK")
    print("✅ Imports: OK")
    print("✅ Posição st.set_page_config: OK")
    print("✅ Inicialização Streamlit: OK")
    print("\n🎉 TODOS OS TESTES PASSARAM!")
    print("🚀 A aplicação está pronta para deploy!")
    
    return True

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
