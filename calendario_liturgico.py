#!/usr/bin/env python3
"""
Módulo de Calendário Litúrgico Católico
Implementa lógica para determinar tempos litúrgicos, festas e sugestões musicais
"""

from datetime import datetime, date, timedelta
import calendar

class CalendarioLiturgico:
    """Classe para gerenciar o calendário litúrgico católico"""
    
    def __init__(self):
        self.ano_atual = datetime.now().year
        self.data_atual = date.today()
        
        # Cores litúrgicas
        self.cores_liturgicas = {
            "Advento": "#663399",  # Roxo
            "Natal": "#FFFFFF",    # Branco
            "Tempo Comum": "#228B22",  # Verde
            "Quaresma": "#663399", # Roxo
            "Páscoa": "#FFFFFF",   # Branco
            "Pentecostes": "#DC143C"  # Vermelho
        }
        
        # Estilos musicais por tempo
        self.estilos_por_tempo = {
            "Advento": "gregoriano",
            "Natal": "tradicional", 
            "Tempo Comum": "contemporâneo",
            "Quaresma": "gregoriano",
            "Páscoa": "tradicional",
            "Pentecostes": "contemporâneo"
        }
        
        # Temas por tempo litúrgico
        self.temas_por_tempo = {
            "Advento": "esperança, preparação, vigilância, Maria",
            "Natal": "alegria, nascimento de Jesus, paz, família",
            "Tempo Comum": "crescimento espiritual, vida cristã, comunidade",
            "Quaresma": "penitência, conversão, jejum, oração",
            "Páscoa": "ressurreição, vida nova, alegria, vitória",
            "Pentecostes": "Espírito Santo, dons, missão, Igreja"
        }
    
    def calcular_pascoa(self, ano):
        """Calcula a data da Páscoa para um ano específico (algoritmo de Gauss)"""
        # Algoritmo de Gauss para calcular a Páscoa
        a = ano % 19
        b = ano // 100
        c = ano % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        n = (h + l - 7 * m + 114) // 31
        p = (h + l - 7 * m + 114) % 31
        
        return date(ano, n, p + 1)
    
    def obter_datas_liturgicas(self, ano=None):
        """Retorna as principais datas litúrgicas do ano"""
        if ano is None:
            ano = self.ano_atual
            
        pascoa = self.calcular_pascoa(ano)
        
        datas = {
            # Advento (4 domingos antes do Natal)
            "inicio_advento": self._calcular_inicio_advento(ano),
            "natal": date(ano, 12, 25),
            
            # Quaresma (46 dias antes da Páscoa)
            "quarta_cinzas": pascoa - timedelta(days=46),
            "pascoa": pascoa,
            "ascensao": pascoa + timedelta(days=39),
            "pentecostes": pascoa + timedelta(days=49),
            
            # Outras festas importantes
            "epifania": date(ano, 1, 6),
            "candelaria": date(ano, 2, 2),
            "anunciacao": date(ano, 3, 25),
            "assuncao": date(ano, 8, 15),
            "todos_santos": date(ano, 11, 1),
            "cristo_rei": self._calcular_cristo_rei(ano)
        }
        
        return datas
    
    def _calcular_inicio_advento(self, ano):
        """Calcula o primeiro domingo do Advento"""
        natal = date(ano, 12, 25)
        # Encontrar o domingo mais próximo antes do Natal (4 semanas antes)
        dias_ate_domingo = (natal.weekday() + 1) % 7
        primeiro_domingo_advento = natal - timedelta(days=dias_ate_domingo + 21)
        return primeiro_domingo_advento
    
    def _calcular_cristo_rei(self, ano):
        """Calcula a festa de Cristo Rei (último domingo do ano litúrgico)"""
        inicio_advento = self._calcular_inicio_advento(ano)
        return inicio_advento - timedelta(days=7)
    
    def obter_tempo_liturgico_atual(self):
        """Determina o tempo litúrgico atual"""
        datas = self.obter_datas_liturgicas()
        hoje = self.data_atual
        
        # Verificar cada tempo litúrgico
        if datas["inicio_advento"] <= hoje < datas["natal"]:
            return "Advento"
        elif datas["natal"] <= hoje <= date(hoje.year, 1, 13):  # Até Batismo do Senhor
            return "Natal"
        elif datas["quarta_cinzas"] <= hoje < datas["pascoa"]:
            return "Quaresma"
        elif datas["pascoa"] <= hoje <= datas["pentecostes"]:
            return "Páscoa"
        else:
            return "Tempo Comum"
    
    def obter_cor_liturgica_atual(self):
        """Retorna a cor litúrgica atual"""
        tempo = self.obter_tempo_liturgico_atual()
        return self.cores_liturgicas.get(tempo, "#228B22")
    
    def obter_estilo_sugerido(self):
        """Retorna o estilo musical sugerido para o tempo atual"""
        tempo = self.obter_tempo_liturgico_atual()
        return self.estilos_por_tempo.get(tempo, "contemporâneo")
    
    def obter_temas_sugeridos(self):
        """Retorna temas sugeridos para o tempo litúrgico atual"""
        tempo = self.obter_tempo_liturgico_atual()
        return self.temas_por_tempo.get(tempo, "louvor, gratidão, fé")
    
    def obter_informacoes_completas(self):
        """Retorna informações completas sobre o tempo litúrgico atual"""
        tempo = self.obter_tempo_liturgico_atual()
        
        return {
            "tempo": tempo,
            "cor": self.obter_cor_liturgica_atual(),
            "estilo_sugerido": self.obter_estilo_sugerido(),
            "temas_sugeridos": self.obter_temas_sugeridos(),
            "data_atual": self.data_atual.strftime("%d/%m/%Y"),
            "ano_liturgico": self._obter_ano_liturgico()
        }
    
    def _obter_ano_liturgico(self):
        """Determina o ano litúrgico (A, B ou C)"""
        # O ano litúrgico A, B, C segue um ciclo de 3 anos
        # Ano A: anos divisíveis por 3
        # Ano B: resto 1 na divisão por 3  
        # Ano C: resto 2 na divisão por 3
        resto = self.ano_atual % 3
        if resto == 0:
            return "A"
        elif resto == 1:
            return "B"
        else:
            return "C"
    
    def obter_santos_do_dia(self, data=None):
        """Retorna os santos do dia (implementação básica)"""
        if data is None:
            data = self.data_atual
            
        # Alguns santos importantes (implementação básica)
        santos_calendario = {
            (1, 1): "Santa Maria, Mãe de Deus",
            (1, 6): "Epifania do Senhor",
            (2, 2): "Apresentação do Senhor",
            (3, 19): "São José",
            (3, 25): "Anunciação do Senhor",
            (5, 31): "Visitação de Nossa Senhora",
            (6, 24): "Nascimento de São João Batista",
            (6, 29): "São Pedro e São Paulo",
            (8, 15): "Assunção de Nossa Senhora",
            (9, 8): "Natividade de Nossa Senhora",
            (10, 4): "São Francisco de Assis",
            (11, 1): "Todos os Santos",
            (11, 2): "Finados",
            (12, 8): "Imaculada Conceição",
            (12, 25): "Natal do Senhor"
        }
        
        chave = (data.month, data.day)
        return santos_calendario.get(chave, "")
    
    def obter_sugestoes_musicais_detalhadas(self):
        """Retorna sugestões musicais detalhadas para o tempo atual"""
        tempo = self.obter_tempo_liturgico_atual()
        santo_do_dia = self.obter_santos_do_dia()
        
        sugestoes = {
            "tempo_liturgico": tempo,
            "estilo_principal": self.obter_estilo_sugerido(),
            "temas": self.obter_temas_sugeridos(),
            "santo_do_dia": santo_do_dia,
            "tons_recomendados": self._obter_tons_por_tempo(tempo),
            "instrumentacao": self._obter_instrumentacao_por_tempo(tempo)
        }
        
        return sugestoes
    
    def _obter_tons_por_tempo(self, tempo):
        """Retorna tons musicais recomendados por tempo litúrgico"""
        tons_por_tempo = {
            "Advento": ["D", "Em", "Am"],  # Tons mais contemplativos
            "Natal": ["C", "G", "F"],      # Tons alegres e brilhantes
            "Tempo Comum": ["G", "C", "D", "A"],  # Tons versáteis
            "Quaresma": ["Dm", "Am", "Em"], # Tons menores, contemplativos
            "Páscoa": ["C", "G", "D", "A"], # Tons maiores, alegres
            "Pentecostes": ["G", "D", "A"]  # Tons vibrantes
        }
        
        return tons_por_tempo.get(tempo, ["C", "G", "D"])
    
    def _obter_instrumentacao_por_tempo(self, tempo):
        """Retorna instrumentação recomendada por tempo litúrgico"""
        instrumentacao = {
            "Advento": ["órgão", "flauta", "violino"],
            "Natal": ["órgão", "violão", "flauta", "coral"],
            "Tempo Comum": ["violão", "piano", "flauta"],
            "Quaresma": ["órgão", "violino", "voz solo"],
            "Páscoa": ["órgão", "trompete", "coral", "violão"],
            "Pentecostes": ["órgão", "violão", "percussão leve"]
        }
        
        return instrumentacao.get(tempo, ["violão", "piano"])

# Função de conveniência para uso externo
def obter_calendario_liturgico():
    """Retorna uma instância do calendário litúrgico"""
    return CalendarioLiturgico()

# Teste básico
if __name__ == "__main__":
    cal = CalendarioLiturgico()
    info = cal.obter_informacoes_completas()
    
    print("📅 CALENDÁRIO LITÚRGICO CATÓLICO")
    print("=" * 40)
    print(f"Data: {info['data_atual']}")
    print(f"Tempo Litúrgico: {info['tempo']}")
    print(f"Ano Litúrgico: {info['ano_liturgico']}")
    print(f"Cor Litúrgica: {info['cor']}")
    print(f"Estilo Sugerido: {info['estilo_sugerido']}")
    print(f"Temas: {info['temas_sugeridos']}")
    
    santo = cal.obter_santos_do_dia()
    if santo:
        print(f"Santo do Dia: {santo}")
