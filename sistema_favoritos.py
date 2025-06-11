#!/usr/bin/env python3
"""
Sistema de Favoritos e Playlists
Gerencia músicas salvas, favoritos e playlists organizadas
"""

import json
import os
from datetime import datetime
import hashlib
import base64

class SistemaFavoritos:
    """Classe para gerenciar favoritos e playlists"""
    
    def __init__(self, arquivo_dados="dados_favoritos.json"):
        self.arquivo_dados = arquivo_dados
        self.dados = self._carregar_dados()
        
        # Estrutura padrão dos dados
        if not self.dados:
            self.dados = {
                "musicas": {},
                "favoritos": [],
                "playlists": {},
                "historico": [],
                "configuracoes": {
                    "max_historico": 100,
                    "auto_salvar": True
                }
            }
            self._salvar_dados()
    
    def _carregar_dados(self):
        """Carrega dados do arquivo JSON"""
        try:
            if os.path.exists(self.arquivo_dados):
                with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar dados: {str(e)}")
        return {}
    
    def _salvar_dados(self):
        """Salva dados no arquivo JSON"""
        try:
            with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
                json.dump(self.dados, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Erro ao salvar dados: {str(e)}")
            return False
    
    def _gerar_id_musica(self, titulo, letra, tom, estilo):
        """Gera ID único para uma música"""
        conteudo = f"{titulo}_{letra}_{tom}_{estilo}"
        return hashlib.md5(conteudo.encode()).hexdigest()[:12]
    
    def salvar_musica(self, titulo, letra, tom, estilo, cifras="", audio_bytes=None, 
                     tipo_audio="instrumental", metadados_extras=None):
        """Salva uma música no sistema"""
        try:
            # Gerar ID único
            id_musica = self._gerar_id_musica(titulo, letra, tom, estilo)
            
            # Preparar dados da música
            musica_dados = {
                "id": id_musica,
                "titulo": titulo,
                "letra": letra,
                "tom": tom,
                "estilo": estilo,
                "cifras": cifras,
                "tipo_audio": tipo_audio,
                "data_criacao": datetime.now().isoformat(),
                "data_modificacao": datetime.now().isoformat(),
                "contador_reproducoes": 0,
                "metadados": metadados_extras or {}
            }
            
            # Salvar áudio se fornecido
            if audio_bytes:
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                musica_dados["audio_base64"] = audio_base64
            
            # Adicionar aos dados
            self.dados["musicas"][id_musica] = musica_dados
            
            # Adicionar ao histórico
            self._adicionar_ao_historico(id_musica, "criacao")
            
            # Salvar dados
            if self.dados["configuracoes"]["auto_salvar"]:
                self._salvar_dados()
            
            return id_musica
            
        except Exception as e:
            print(f"Erro ao salvar música: {str(e)}")
            return None
    
    def obter_musica(self, id_musica):
        """Obtém uma música pelo ID"""
        musica = self.dados["musicas"].get(id_musica)
        if musica:
            # Incrementar contador de reproduções
            musica["contador_reproducoes"] += 1
            self._adicionar_ao_historico(id_musica, "reproducao")
            
            # Decodificar áudio se existir
            if "audio_base64" in musica:
                try:
                    audio_bytes = base64.b64decode(musica["audio_base64"])
                    musica["audio_bytes"] = audio_bytes
                except Exception as e:
                    print(f"Erro ao decodificar áudio: {str(e)}")
            
            if self.dados["configuracoes"]["auto_salvar"]:
                self._salvar_dados()
        
        return musica
    
    def listar_musicas(self, filtro_estilo=None, filtro_tom=None, ordenar_por="data_criacao"):
        """Lista músicas com filtros opcionais"""
        musicas = []
        
        for id_musica, musica in self.dados["musicas"].items():
            # Aplicar filtros
            if filtro_estilo and musica["estilo"] != filtro_estilo:
                continue
            if filtro_tom and musica["tom"] != filtro_tom:
                continue
            
            # Criar cópia sem áudio para listagem
            musica_listagem = musica.copy()
            if "audio_base64" in musica_listagem:
                del musica_listagem["audio_base64"]
            
            musicas.append(musica_listagem)
        
        # Ordenar
        if ordenar_por == "data_criacao":
            musicas.sort(key=lambda x: x["data_criacao"], reverse=True)
        elif ordenar_por == "titulo":
            musicas.sort(key=lambda x: x["titulo"].lower())
        elif ordenar_por == "reproducoes":
            musicas.sort(key=lambda x: x["contador_reproducoes"], reverse=True)
        
        return musicas
    
    def adicionar_aos_favoritos(self, id_musica):
        """Adiciona música aos favoritos"""
        if id_musica in self.dados["musicas"] and id_musica not in self.dados["favoritos"]:
            self.dados["favoritos"].append(id_musica)
            self._adicionar_ao_historico(id_musica, "favorito_adicionado")
            
            if self.dados["configuracoes"]["auto_salvar"]:
                self._salvar_dados()
            return True
        return False
    
    def remover_dos_favoritos(self, id_musica):
        """Remove música dos favoritos"""
        if id_musica in self.dados["favoritos"]:
            self.dados["favoritos"].remove(id_musica)
            self._adicionar_ao_historico(id_musica, "favorito_removido")
            
            if self.dados["configuracoes"]["auto_salvar"]:
                self._salvar_dados()
            return True
        return False
    
    def obter_favoritos(self):
        """Obtém lista de músicas favoritas"""
        favoritos = []
        for id_musica in self.dados["favoritos"]:
            musica = self.dados["musicas"].get(id_musica)
            if musica:
                # Cópia sem áudio
                musica_favorito = musica.copy()
                if "audio_base64" in musica_favorito:
                    del musica_favorito["audio_base64"]
                favoritos.append(musica_favorito)
        
        return favoritos
    
    def criar_playlist(self, nome_playlist, descricao="", musicas_ids=None):
        """Cria uma nova playlist"""
        try:
            playlist_id = hashlib.md5(f"{nome_playlist}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
            
            playlist_dados = {
                "id": playlist_id,
                "nome": nome_playlist,
                "descricao": descricao,
                "musicas": musicas_ids or [],
                "data_criacao": datetime.now().isoformat(),
                "data_modificacao": datetime.now().isoformat(),
                "contador_reproducoes": 0
            }
            
            self.dados["playlists"][playlist_id] = playlist_dados
            
            if self.dados["configuracoes"]["auto_salvar"]:
                self._salvar_dados()
            
            return playlist_id
            
        except Exception as e:
            print(f"Erro ao criar playlist: {str(e)}")
            return None
    
    def adicionar_musica_playlist(self, playlist_id, musica_id):
        """Adiciona música a uma playlist"""
        if (playlist_id in self.dados["playlists"] and 
            musica_id in self.dados["musicas"] and
            musica_id not in self.dados["playlists"][playlist_id]["musicas"]):
            
            self.dados["playlists"][playlist_id]["musicas"].append(musica_id)
            self.dados["playlists"][playlist_id]["data_modificacao"] = datetime.now().isoformat()
            
            if self.dados["configuracoes"]["auto_salvar"]:
                self._salvar_dados()
            return True
        return False
    
    def remover_musica_playlist(self, playlist_id, musica_id):
        """Remove música de uma playlist"""
        if (playlist_id in self.dados["playlists"] and 
            musica_id in self.dados["playlists"][playlist_id]["musicas"]):
            
            self.dados["playlists"][playlist_id]["musicas"].remove(musica_id)
            self.dados["playlists"][playlist_id]["data_modificacao"] = datetime.now().isoformat()
            
            if self.dados["configuracoes"]["auto_salvar"]:
                self._salvar_dados()
            return True
        return False
    
    def obter_playlist(self, playlist_id):
        """Obtém uma playlist com suas músicas"""
        playlist = self.dados["playlists"].get(playlist_id)
        if not playlist:
            return None
        
        # Incrementar contador
        playlist["contador_reproducoes"] += 1
        
        # Obter dados das músicas
        musicas_playlist = []
        for musica_id in playlist["musicas"]:
            musica = self.dados["musicas"].get(musica_id)
            if musica:
                # Cópia sem áudio
                musica_playlist = musica.copy()
                if "audio_base64" in musica_playlist:
                    del musica_playlist["audio_base64"]
                musicas_playlist.append(musica_playlist)
        
        playlist_completa = playlist.copy()
        playlist_completa["musicas_dados"] = musicas_playlist
        
        if self.dados["configuracoes"]["auto_salvar"]:
            self._salvar_dados()
        
        return playlist_completa
    
    def listar_playlists(self):
        """Lista todas as playlists"""
        playlists = []
        for playlist_id, playlist in self.dados["playlists"].items():
            playlist_resumo = {
                "id": playlist["id"],
                "nome": playlist["nome"],
                "descricao": playlist["descricao"],
                "quantidade_musicas": len(playlist["musicas"]),
                "data_criacao": playlist["data_criacao"],
                "contador_reproducoes": playlist["contador_reproducoes"]
            }
            playlists.append(playlist_resumo)
        
        # Ordenar por data de criação
        playlists.sort(key=lambda x: x["data_criacao"], reverse=True)
        return playlists
    
    def _adicionar_ao_historico(self, id_musica, acao):
        """Adiciona entrada ao histórico"""
        entrada_historico = {
            "id_musica": id_musica,
            "acao": acao,
            "timestamp": datetime.now().isoformat()
        }
        
        self.dados["historico"].append(entrada_historico)
        
        # Limitar tamanho do histórico
        max_historico = self.dados["configuracoes"]["max_historico"]
        if len(self.dados["historico"]) > max_historico:
            self.dados["historico"] = self.dados["historico"][-max_historico:]
    
    def obter_historico(self, limite=20):
        """Obtém histórico de ações"""
        historico_recente = self.dados["historico"][-limite:]
        
        # Enriquecer com dados das músicas
        historico_enriquecido = []
        for entrada in reversed(historico_recente):
            musica = self.dados["musicas"].get(entrada["id_musica"])
            if musica:
                entrada_enriquecida = entrada.copy()
                entrada_enriquecida["titulo_musica"] = musica["titulo"]
                entrada_enriquecida["estilo_musica"] = musica["estilo"]
                historico_enriquecido.append(entrada_enriquecida)
        
        return historico_enriquecido
    
    def obter_estatisticas(self):
        """Obtém estatísticas do sistema"""
        total_musicas = len(self.dados["musicas"])
        total_favoritos = len(self.dados["favoritos"])
        total_playlists = len(self.dados["playlists"])
        
        # Estilo mais usado
        estilos_count = {}
        for musica in self.dados["musicas"].values():
            estilo = musica["estilo"]
            estilos_count[estilo] = estilos_count.get(estilo, 0) + 1
        
        estilo_mais_usado = max(estilos_count.items(), key=lambda x: x[1]) if estilos_count else ("Nenhum", 0)
        
        # Música mais reproduzida
        musica_mais_reproduzida = max(
            self.dados["musicas"].values(),
            key=lambda x: x["contador_reproducoes"],
            default=None
        )
        
        return {
            "total_musicas": total_musicas,
            "total_favoritos": total_favoritos,
            "total_playlists": total_playlists,
            "estilo_mais_usado": estilo_mais_usado,
            "musica_mais_reproduzida": {
                "titulo": musica_mais_reproduzida["titulo"] if musica_mais_reproduzida else "Nenhuma",
                "reproducoes": musica_mais_reproduzida["contador_reproducoes"] if musica_mais_reproduzida else 0
            }
        }
    
    def exportar_dados(self, arquivo_destino):
        """Exporta todos os dados para backup"""
        try:
            with open(arquivo_destino, 'w', encoding='utf-8') as f:
                json.dump(self.dados, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Erro ao exportar dados: {str(e)}")
            return False
    
    def importar_dados(self, arquivo_origem):
        """Importa dados de backup"""
        try:
            with open(arquivo_origem, 'r', encoding='utf-8') as f:
                dados_importados = json.load(f)
            
            # Validar estrutura básica
            if all(key in dados_importados for key in ["musicas", "favoritos", "playlists"]):
                self.dados = dados_importados
                self._salvar_dados()
                return True
            else:
                print("Estrutura de dados inválida")
                return False
                
        except Exception as e:
            print(f"Erro ao importar dados: {str(e)}")
            return False

# Função de conveniência
def criar_sistema_favoritos():
    """Retorna uma instância do sistema de favoritos"""
    return SistemaFavoritos()

# Teste básico
if __name__ == "__main__":
    sistema = SistemaFavoritos()
    
    print("💾 SISTEMA DE FAVORITOS E PLAYLISTS")
    print("=" * 40)
    
    # Teste básico
    id_musica = sistema.salvar_musica(
        titulo="Ave Maria Teste",
        letra="Ave Maria, cheia de graça",
        tom="C",
        estilo="mariano",
        cifras="C - G - Am - F"
    )
    
    if id_musica:
        print(f"✅ Música salva com ID: {id_musica}")
        
        # Adicionar aos favoritos
        sistema.adicionar_aos_favoritos(id_musica)
        print("✅ Adicionada aos favoritos")
        
        # Criar playlist
        playlist_id = sistema.criar_playlist("Músicas Marianas", "Devoção à Nossa Senhora")
        if playlist_id:
            sistema.adicionar_musica_playlist(playlist_id, id_musica)
            print(f"✅ Playlist criada: {playlist_id}")
    
    # Estatísticas
    stats = sistema.obter_estatisticas()
    print(f"\n📊 Estatísticas:")
    print(f"   Músicas: {stats['total_musicas']}")
    print(f"   Favoritos: {stats['total_favoritos']}")
    print(f"   Playlists: {stats['total_playlists']}")
    print(f"   Estilo mais usado: {stats['estilo_mais_usado'][0]}")
