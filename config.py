# Configurações do Compositor de Música Católica

# Tons musicais disponíveis
TONS_MUSICAIS = {
    "C": {"freq": 261.63, "nome": "Dó"},
    "C#": {"freq": 277.18, "nome": "Dó#"},
    "Db": {"freq": 277.18, "nome": "Réb"},
    "D": {"freq": 293.66, "nome": "Ré"},
    "D#": {"freq": 311.13, "nome": "Ré#"},
    "Eb": {"freq": 311.13, "nome": "Mib"},
    "E": {"freq": 329.63, "nome": "Mi"},
    "F": {"freq": 349.23, "nome": "Fá"},
    "F#": {"freq": 369.99, "nome": "Fá#"},
    "Gb": {"freq": 369.99, "nome": "Solb"},
    "G": {"freq": 392.00, "nome": "Sol"},
    "G#": {"freq": 415.30, "nome": "Sol#"},
    "Ab": {"freq": 415.30, "nome": "Láb"},
    "A": {"freq": 440.00, "nome": "Lá"},
    "A#": {"freq": 466.16, "nome": "Lá#"},
    "Bb": {"freq": 466.16, "nome": "Sib"},
    "B": {"freq": 493.88, "nome": "Si"}
}

# Estilos musicais católicos
ESTILOS_CATOLICOS = {
    "tradicional": {
        "nome": "Tradicional (Hinos Clássicos)",
        "descricao": "Hinos clássicos católicos com harmonias tradicionais",
        "progressao": [1, 1.5, 1.68, 1.33],  # I-V-vi-IV
        "tempo": "moderato"
    },
    "contemporâneo": {
        "nome": "Contemporâneo (Música Católica Moderna)",
        "descricao": "Música católica moderna com instrumentação atual",
        "progressao": [1.68, 1.33, 1, 1.5],  # vi-IV-I-V
        "tempo": "allegro"
    },
    "gregoriano": {
        "nome": "Gregoriano (Inspiração Medieval)",
        "descricao": "Inspirado no canto gregoriano medieval",
        "progressao": [1, 1.125, 1.25, 1],  # Modalidade gregoriana
        "tempo": "largo"
    },
    "mariano": {
        "nome": "Mariano (Devoção à Nossa Senhora)",
        "descricao": "Focado na devoção à Virgem Maria",
        "progressao": [1, 1.33, 1.5, 1],  # I-IV-V-I
        "tempo": "andante"
    },
    "litúrgico": {
        "nome": "Litúrgico (Para Missa)",
        "descricao": "Apropriado para uso durante a Santa Missa",
        "progressao": [1, 1.25, 1.5, 1.33],  # I-iii-V-IV
        "tempo": "moderato"
    }
}

# Temas católicos comuns
TEMAS_CATOLICOS = [
    "Santíssima Trindade",
    "Virgem Maria",
    "Santos e Santas",
    "Eucaristia",
    "Paixão de Cristo",
    "Ressurreição",
    "Espírito Santo",
    "Igreja Católica",
    "Liturgia",
    "Oração",
    "Perdão",
    "Esperança",
    "Caridade",
    "Fé"
]

# Tempos litúrgicos
TEMPOS_LITURGICOS = [
    "Advento",
    "Natal",
    "Quaresma", 
    "Páscoa",
    "Tempo Comum",
    "Festas Marianas",
    "Festas dos Santos"
]
