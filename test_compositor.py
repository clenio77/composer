#!/usr/bin/env python3
"""
Testes para o Compositor de Música Católica
Este arquivo contém testes unitários para verificar as funcionalidades.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestCompositorCatolico(unittest.TestCase):
    """Testes para as funcionalidades do compositor católico"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.tons_validos = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        self.estilos_validos = ["tradicional", "contemporâneo", "gregoriano", "mariano", "litúrgico"]
    
    def test_tons_musicais_validos(self):
        """Testa se os tons musicais são válidos"""
        from config import TONS_MUSICAIS
        
        for tom in self.tons_validos:
            if tom in TONS_MUSICAIS:
                self.assertIn("freq", TONS_MUSICAIS[tom])
                self.assertIn("nome", TONS_MUSICAIS[tom])
                self.assertIsInstance(TONS_MUSICAIS[tom]["freq"], float)
                self.assertIsInstance(TONS_MUSICAIS[tom]["nome"], str)
    
    def test_estilos_catolicos_validos(self):
        """Testa se os estilos católicos são válidos"""
        from config import ESTILOS_CATOLICOS
        
        for estilo in self.estilos_validos:
            if estilo in ESTILOS_CATOLICOS:
                self.assertIn("nome", ESTILOS_CATOLICOS[estilo])
                self.assertIn("descricao", ESTILOS_CATOLICOS[estilo])
                self.assertIn("progressao", ESTILOS_CATOLICOS[estilo])
                self.assertIn("tempo", ESTILOS_CATOLICOS[estilo])
    
    def test_frequencias_tons(self):
        """Testa se as frequências dos tons estão corretas"""
        from config import TONS_MUSICAIS
        
        # Testa algumas frequências conhecidas
        frequencias_esperadas = {
            "A": 440.00,  # Lá padrão
            "C": 261.63,  # Dó central
            "G": 392.00   # Sol
        }
        
        for tom, freq_esperada in frequencias_esperadas.items():
            if tom in TONS_MUSICAIS:
                self.assertAlmostEqual(
                    TONS_MUSICAIS[tom]["freq"], 
                    freq_esperada, 
                    places=2,
                    msg=f"Frequência do tom {tom} incorreta"
                )
    
    @patch('AgentCompose.AudioSegment')
    @patch('AgentCompose.Sine')
    def test_geracao_audio_simples(self, mock_sine, mock_audio_segment):
        """Testa a geração de áudio simples"""
        # Mock dos objetos de áudio
        mock_audio = MagicMock()
        mock_audio.fade_in.return_value = mock_audio
        mock_audio.fade_out.return_value = mock_audio
        mock_sine.return_value.to_audio_segment.return_value = mock_audio
        
        mock_audio_final = MagicMock()
        mock_audio_final.__add__ = MagicMock(return_value=mock_audio_final)
        mock_audio_segment.empty.return_value = mock_audio_final
        
        # Mock do export
        mock_audio_final.export = MagicMock()
        
        try:
            from AgentCompose import gerar_audio_simples
            
            # Testa geração com parâmetros válidos
            resultado = gerar_audio_simples("C", "tradicional")
            
            # Verifica se as funções foram chamadas
            mock_sine.assert_called()
            mock_audio_segment.empty.assert_called()
            
        except ImportError:
            self.skipTest("Módulo AgentCompose não disponível para teste")
    
    def test_parametros_invalidos(self):
        """Testa comportamento com parâmetros inválidos"""
        try:
            from AgentCompose import gerar_audio_simples
            
            # Testa com tom inválido
            resultado = gerar_audio_simples("X", "tradicional")
            # Deve usar frequência padrão (440.00)
            
            # Testa com estilo inválido
            resultado = gerar_audio_simples("C", "inexistente")
            # Deve usar estilo padrão
            
        except ImportError:
            self.skipTest("Módulo AgentCompose não disponível para teste")
    
    def test_configuracoes_arquivo(self):
        """Testa se o arquivo de configurações está correto"""
        try:
            import config
            
            # Verifica se as constantes existem
            self.assertTrue(hasattr(config, 'TONS_MUSICAIS'))
            self.assertTrue(hasattr(config, 'ESTILOS_CATOLICOS'))
            self.assertTrue(hasattr(config, 'TEMAS_CATOLICOS'))
            self.assertTrue(hasattr(config, 'TEMPOS_LITURGICOS'))
            
            # Verifica se não estão vazios
            self.assertGreater(len(config.TONS_MUSICAIS), 0)
            self.assertGreater(len(config.ESTILOS_CATOLICOS), 0)
            self.assertGreater(len(config.TEMAS_CATOLICOS), 0)
            self.assertGreater(len(config.TEMPOS_LITURGICOS), 0)
            
        except ImportError:
            self.skipTest("Módulo config não disponível para teste")
    
    def test_temas_catolicos(self):
        """Testa se os temas católicos são apropriados"""
        try:
            from config import TEMAS_CATOLICOS
            
            # Verifica se contém temas essenciais
            temas_essenciais = [
                "Santíssima Trindade",
                "Virgem Maria", 
                "Eucaristia",
                "Santos e Santas"
            ]
            
            for tema in temas_essenciais:
                self.assertIn(tema, TEMAS_CATOLICOS, 
                            f"Tema essencial '{tema}' não encontrado")
                            
        except ImportError:
            self.skipTest("Módulo config não disponível para teste")
    
    def test_tempos_liturgicos(self):
        """Testa se os tempos litúrgicos estão corretos"""
        try:
            from config import TEMPOS_LITURGICOS
            
            # Verifica se contém os tempos principais
            tempos_principais = [
                "Advento",
                "Natal", 
                "Quaresma",
                "Páscoa",
                "Tempo Comum"
            ]
            
            for tempo in tempos_principais:
                self.assertIn(tempo, TEMPOS_LITURGICOS,
                            f"Tempo litúrgico '{tempo}' não encontrado")
                            
        except ImportError:
            self.skipTest("Módulo config não disponível para teste")

class TestIntegracaoStreamlit(unittest.TestCase):
    """Testes de integração com Streamlit"""
    
    def test_importacao_streamlit(self):
        """Testa se o Streamlit pode ser importado"""
        try:
            import streamlit as st
            self.assertTrue(True, "Streamlit importado com sucesso")
        except ImportError:
            self.fail("Streamlit não pode ser importado")
    
    def test_importacao_crewai(self):
        """Testa se o CrewAI pode ser importado"""
        try:
            from crewai import Agent, Task, Crew, Process, LLM
            self.assertTrue(True, "CrewAI importado com sucesso")
        except ImportError:
            self.fail("CrewAI não pode ser importado")

def executar_testes():
    """Executa todos os testes"""
    print("🧪 Executando Testes do Compositor de Música Católica")
    print("=" * 60)
    
    # Criar suite de testes
    suite = unittest.TestSuite()
    
    # Adicionar testes
    suite.addTest(unittest.makeSuite(TestCompositorCatolico))
    suite.addTest(unittest.makeSuite(TestIntegracaoStreamlit))
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    
    # Resumo
    print("\n" + "=" * 60)
    if resultado.wasSuccessful():
        print("✅ Todos os testes passaram com sucesso!")
    else:
        print(f"❌ {len(resultado.failures)} teste(s) falharam")
        print(f"⚠️  {len(resultado.errors)} erro(s) encontrado(s)")
    
    print("=" * 60)
    return resultado.wasSuccessful()

if __name__ == "__main__":
    executar_testes()
