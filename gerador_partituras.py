#!/usr/bin/env python3
"""
Módulo de Geração de Partituras
Cria partituras em PDF e MIDI usando music21
"""

from music21 import stream, note, meter, key, tempo, duration, bar, pitch, scale
from music21 import metadata, layout, spanner
import tempfile
import os
import io

class GeradorPartituras:
    """Classe para gerar partituras musicais"""
    
    def __init__(self):
        self.progressoes_acordes = {
            "tradicional": ["I", "V", "vi", "IV"],
            "contemporâneo": ["vi", "IV", "I", "V"], 
            "gregoriano": ["I", "ii", "iii", "I"],
            "mariano": ["I", "IV", "V", "I"],
            "litúrgico": ["I", "iii", "V", "IV"]
        }
        
        # Mapeamento de graus para notas
        self.graus_para_notas = {
            "I": [0, 2, 4],    # Tônica
            "ii": [1, 3, 5],   # Supertônica
            "iii": [2, 4, 6],  # Mediante
            "IV": [3, 5, 0],   # Subdominante
            "V": [4, 6, 1],    # Dominante
            "vi": [5, 0, 2],   # Superdominante
            "vii": [6, 1, 3]   # Sensível
        }
    
    def criar_partitura_basica(self, tom, estilo, letra="", titulo="Música Católica"):
        """Cria uma partitura básica com melodia e acordes"""
        
        # Criar stream principal
        partitura = stream.Score()
        
        # Metadados
        partitura.metadata = metadata.Metadata()
        partitura.metadata.title = titulo
        partitura.metadata.composer = "Compositor de Música Católica"
        
        # Configurações básicas
        partitura.append(meter.TimeSignature('4/4'))
        partitura.append(key.KeySignature(self._obter_armadura(tom)))
        partitura.append(tempo.TempoIndication(number=80))
        
        # Criar parte da melodia
        parte_melodia = stream.Part()
        parte_melodia.partName = "Melodia"
        
        # Criar parte dos acordes
        parte_acordes = stream.Part()
        parte_acordes.partName = "Acordes"
        
        # Gerar melodia baseada no estilo
        melodia = self._gerar_melodia(tom, estilo)
        acordes = self._gerar_acordes(tom, estilo)
        
        # Adicionar notas à melodia
        for nota_info in melodia:
            n = note.Note(nota_info['pitch'], quarterLength=nota_info['duration'])
            parte_melodia.append(n)
        
        # Adicionar acordes
        for acorde_info in acordes:
            acorde = self._criar_acorde(acorde_info['grau'], tom)
            acorde.quarterLength = acorde_info['duration']
            parte_acordes.append(acorde)
        
        # Adicionar partes à partitura
        partitura.append(parte_melodia)
        partitura.append(parte_acordes)
        
        return partitura
    
    def _obter_armadura(self, tom):
        """Retorna a armadura de clave para o tom"""
        armaduras = {
            'C': 0, 'G': 1, 'D': 2, 'A': 3, 'E': 4, 'B': 5, 'F#': 6,
            'F': -1, 'Bb': -2, 'Eb': -3, 'Ab': -4, 'Db': -5, 'Gb': -6,
            'C#': 7, 'Cb': -7
        }
        return armaduras.get(tom, 0)
    
    def _gerar_melodia(self, tom, estilo):
        """Gera uma melodia simples baseada no tom e estilo"""
        escala = scale.MajorScale(tom)
        notas_escala = [str(n) for n in escala.pitches[:8]]
        
        # Padrões melódicos por estilo
        padroes = {
            "tradicional": [0, 2, 4, 2, 0, 4, 2, 0],
            "contemporâneo": [0, 4, 2, 4, 0, 2, 4, 0],
            "gregoriano": [0, 1, 2, 1, 0, 2, 1, 0],
            "mariano": [0, 2, 4, 5, 4, 2, 0, 0],
            "litúrgico": [0, 2, 4, 2, 4, 2, 0, 0]
        }
        
        padrao = padroes.get(estilo, padroes["tradicional"])
        melodia = []
        
        for grau in padrao:
            if grau < len(notas_escala):
                melodia.append({
                    'pitch': notas_escala[grau],
                    'duration': 1.0  # Semínima
                })
        
        return melodia
    
    def _gerar_acordes(self, tom, estilo):
        """Gera progressão de acordes baseada no estilo"""
        progressao = self.progressoes_acordes.get(estilo, self.progressoes_acordes["tradicional"])
        
        acordes = []
        for grau in progressao:
            acordes.append({
                'grau': grau,
                'duration': 4.0  # Semibreve
            })
        
        return acordes
    
    def _criar_acorde(self, grau_romano, tom):
        """Cria um acorde baseado no grau romano e tom"""
        from music21 import chord
        
        escala = scale.MajorScale(tom)
        notas_escala = escala.pitches
        
        # Mapear grau romano para índices
        mapeamento_graus = {
            "I": 0, "ii": 1, "iii": 2, "IV": 3, 
            "V": 4, "vi": 5, "vii": 6
        }
        
        indice_base = mapeamento_graus.get(grau_romano, 0)
        
        # Criar tríade
        notas_acorde = [
            notas_escala[indice_base % 7],
            notas_escala[(indice_base + 2) % 7], 
            notas_escala[(indice_base + 4) % 7]
        ]
        
        return chord.Chord(notas_acorde)
    
    def gerar_cifras_simplificadas(self, tom, estilo):
        """Gera cifras simplificadas para violão"""
        progressao = self.progressoes_acordes.get(estilo, self.progressoes_acordes["tradicional"])
        
        # Mapeamento de graus para cifras
        cifras_por_tom = {
            'C': {'I': 'C', 'ii': 'Dm', 'iii': 'Em', 'IV': 'F', 'V': 'G', 'vi': 'Am', 'vii': 'Bº'},
            'G': {'I': 'G', 'ii': 'Am', 'iii': 'Bm', 'IV': 'C', 'V': 'D', 'vi': 'Em', 'vii': 'F#º'},
            'D': {'I': 'D', 'ii': 'Em', 'iii': 'F#m', 'IV': 'G', 'V': 'A', 'vi': 'Bm', 'vii': 'C#º'},
            'A': {'I': 'A', 'ii': 'Bm', 'iii': 'C#m', 'IV': 'D', 'V': 'E', 'vi': 'F#m', 'vii': 'G#º'},
            'E': {'I': 'E', 'ii': 'F#m', 'iii': 'G#m', 'IV': 'A', 'V': 'B', 'vi': 'C#m', 'vii': 'D#º'},
            'F': {'I': 'F', 'ii': 'Gm', 'iii': 'Am', 'IV': 'Bb', 'V': 'C', 'vi': 'Dm', 'vii': 'Eº'}
        }
        
        cifras_tom = cifras_por_tom.get(tom, cifras_por_tom['C'])
        cifras_resultado = []
        
        for grau in progressao:
            cifra = cifras_tom.get(grau, 'C')
            cifras_resultado.append(cifra)
        
        return cifras_resultado
    
    def exportar_para_pdf(self, partitura, nome_arquivo="partitura"):
        """Exporta partitura para PDF"""
        try:
            # Criar arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                # Configurar layout
                partitura.write('musicxml.pdf', fp=temp_file.name)
                
                # Ler bytes do arquivo
                with open(temp_file.name, 'rb') as pdf_file:
                    pdf_bytes = pdf_file.read()
                
                # Limpar arquivo temporário
                os.unlink(temp_file.name)
                
                return pdf_bytes
                
        except Exception as e:
            print(f"Erro ao exportar PDF: {str(e)}")
            return None
    
    def exportar_para_midi(self, partitura, nome_arquivo="partitura"):
        """Exporta partitura para MIDI"""
        try:
            # Criar arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mid') as temp_file:
                partitura.write('midi', fp=temp_file.name)
                
                # Ler bytes do arquivo
                with open(temp_file.name, 'rb') as midi_file:
                    midi_bytes = midi_file.read()
                
                # Limpar arquivo temporário
                os.unlink(temp_file.name)
                
                return midi_bytes
                
        except Exception as e:
            print(f"Erro ao exportar MIDI: {str(e)}")
            return None
    
    def gerar_partitura_completa(self, tom, estilo, titulo="Música Católica", letra=""):
        """Gera partitura completa com todas as informações"""
        
        # Criar partitura
        partitura = self.criar_partitura_basica(tom, estilo, letra, titulo)
        
        # Gerar cifras
        cifras = self.gerar_cifras_simplificadas(tom, estilo)
        
        # Informações adicionais
        info = {
            "titulo": titulo,
            "tom": tom,
            "estilo": estilo,
            "cifras": " - ".join(cifras),
            "progressao": " - ".join(self.progressoes_acordes.get(estilo, [])),
            "compasso": "4/4",
            "andamento": "80 BPM"
        }
        
        return {
            "partitura": partitura,
            "cifras": cifras,
            "info": info
        }
    
    def criar_partitura_coral_satb(self, tom, estilo, titulo="Música Católica"):
        """Cria partitura para coral SATB (Soprano, Alto, Tenor, Baixo)"""
        
        partitura = stream.Score()
        
        # Metadados
        partitura.metadata = metadata.Metadata()
        partitura.metadata.title = titulo + " (SATB)"
        partitura.metadata.composer = "Compositor de Música Católica"
        
        # Configurações
        partitura.append(meter.TimeSignature('4/4'))
        partitura.append(key.KeySignature(self._obter_armadura(tom)))
        partitura.append(tempo.TempoIndication(number=80))
        
        # Criar partes SATB
        soprano = stream.Part()
        soprano.partName = "Soprano"
        
        alto = stream.Part()
        alto.partName = "Alto"
        
        tenor = stream.Part()
        tenor.partName = "Tenor"
        
        baixo = stream.Part()
        baixo.partName = "Baixo"
        
        # Gerar vozes (implementação básica)
        melodia_base = self._gerar_melodia(tom, estilo)
        
        # Soprano (melodia principal)
        for nota_info in melodia_base:
            n = note.Note(nota_info['pitch'], quarterLength=nota_info['duration'])
            soprano.append(n)
        
        # Alto (terça abaixo)
        for nota_info in melodia_base:
            pitch_original = pitch.Pitch(nota_info['pitch'])
            pitch_alto = pitch_original.transpose(-3)  # Terça menor abaixo
            n = note.Note(pitch_alto, quarterLength=nota_info['duration'])
            alto.append(n)
        
        # Tenor (oitava abaixo do soprano)
        for nota_info in melodia_base:
            pitch_original = pitch.Pitch(nota_info['pitch'])
            pitch_tenor = pitch_original.transpose(-12)  # Oitava abaixo
            n = note.Note(pitch_tenor, quarterLength=nota_info['duration'])
            tenor.append(n)
        
        # Baixo (fundamental dos acordes)
        acordes = self._gerar_acordes(tom, estilo)
        for acorde_info in acordes:
            # Usar a fundamental do acorde
            escala = scale.MajorScale(tom)
            nota_baixo = escala.pitches[0].transpose(-24)  # Duas oitavas abaixo
            n = note.Note(nota_baixo, quarterLength=acorde_info['duration'])
            baixo.append(n)
        
        # Adicionar partes
        partitura.append(soprano)
        partitura.append(alto)
        partitura.append(tenor)
        partitura.append(baixo)
        
        return partitura

# Função de conveniência
def criar_gerador_partituras():
    """Retorna uma instância do gerador de partituras"""
    return GeradorPartituras()

# Teste básico
if __name__ == "__main__":
    gerador = GeradorPartituras()
    
    print("🎼 GERADOR DE PARTITURAS")
    print("=" * 30)
    
    # Gerar partitura de exemplo
    resultado = gerador.gerar_partitura_completa("C", "tradicional", "Ave Maria")
    
    print(f"Título: {resultado['info']['titulo']}")
    print(f"Tom: {resultado['info']['tom']}")
    print(f"Estilo: {resultado['info']['estilo']}")
    print(f"Cifras: {resultado['info']['cifras']}")
    print(f"Progressão: {resultado['info']['progressao']}")
    
    # Testar exportação
    try:
        midi_bytes = gerador.exportar_para_midi(resultado['partitura'])
        if midi_bytes:
            print(f"✅ MIDI gerado: {len(midi_bytes)} bytes")
        else:
            print("❌ Erro ao gerar MIDI")
    except Exception as e:
        print(f"❌ Erro no teste MIDI: {str(e)}")
