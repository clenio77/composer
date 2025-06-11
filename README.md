# 🎵✝️ Compositor de Música Católica

Uma aplicação inteligente que utiliza IA para compor músicas católicas personalizadas, com geração de áudio e suporte a diferentes tons musicais.

## 🌟 Funcionalidades

### 🎼 Composição Musical
- **Geração de letras católicas** com base em sentimentos e temas
- **Suporte a múltiplos tons musicais** (C, D, E, F, G, A, B e suas variações)
- **Diferentes estilos católicos**:
  - Tradicional (Hinos Clássicos)
  - Contemporâneo (Música Católica Moderna)
  - Gregoriano (Inspiração Medieval)
  - Mariano (Devoção à Nossa Senhora)
  - Litúrgico (Para Missa)

### 🔊 Geração de Áudio Avançada
- **Text-to-Speech em português brasileiro** para cantar as letras
- **Áudio instrumental** baseado no tom e estilo selecionados
- **Áudio com voz** combinando TTS + música instrumental
- **Progressões harmônicas** específicas para cada estilo católico
- **Player integrado** para reprodução imediata
- **Download de arquivos MP3** de alta qualidade

### 🎵 Upload e Modificação de Músicas
- **Upload de músicas existentes** (MP3, WAV, M4A, OGG)
- **Mudança de tom preservando a voz** usando algoritmos avançados
- **Suporte a múltiplos formatos** de entrada e saída
- **Processamento em tempo real** com feedback visual

### 🎨 Interface Intuitiva
- **Interface web moderna** com Streamlit e sistema de abas
- **Aba "Criar Nova Música"** para composições originais
- **Aba "Modificar Música Existente"** para upload e edição
- **Configurações na sidebar** para tom e estilo
- **Visualização formatada** em Markdown
- **Feedback visual** durante o processamento

## 🛠️ Tecnologias Utilizadas

- **Python 3.11+**
- **Streamlit** - Interface web moderna
- **CrewAI** - Orquestração de agentes IA
- **GPT-4** - Modelo de linguagem para composição
- **gTTS** - Text-to-Speech em português brasileiro
- **LibROSA** - Processamento avançado de áudio
- **SoundFile** - Manipulação de arquivos de áudio
- **PyDub** - Edição e síntese de áudio
- **Pygame** - Reprodução de áudio
- **NumPy/SciPy** - Processamento numérico e científico

## 📦 Instalação

### Pré-requisitos
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

### Passos de instalação

1. **Clone o repositório**:
```bash
git clone https://github.com/clenio77/composer.git
cd composer
```

2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente** (se necessário):
```bash
# Adicione sua chave da OpenAI se necessário
export OPENAI_API_KEY="sua_chave_aqui"
```

4. **Execute a aplicação**:
```bash
streamlit run AgentCompose.py
```

5. **Acesse no navegador**:
```
http://localhost:8501
```

## 🚀 Como Usar

### 📝 Aba 1: Criar Nova Música

#### 1. Configuração
- **Selecione o tom musical** na sidebar (C, D, E, F, G, A, B, etc.)
- **Escolha o estilo católico** desejado
- **Digite os sentimentos ou temas** na área de texto

#### 2. Geração da Composição
- Clique em **"🎵 Gerar Música"** para criar letra e cifras
- Aguarde o processamento (pode levar alguns segundos)
- Visualize a letra, cifras e informações da música

#### 3. Geração de Áudio
- **🎼 Áudio Instrumental**: Base musical sem voz
- **🎤 Áudio com Voz**: TTS em português + instrumental
- Ouça no player integrado e faça download

### 🎼 Aba 2: Modificar Música Existente

#### 1. Upload
- **Faça upload** de uma música (MP3, WAV, M4A, OGG)
- Visualize informações do arquivo carregado
- Ouça a música original no player

#### 2. Configuração de Tons
- **Selecione o tom original** da música
- **Escolha o novo tom** desejado
- Visualize a diferença em semitons

#### 3. Processamento
- Clique em **"🔄 Mudar Tom da Música"**
- Aguarde o processamento (preserva qualidade da voz)
- Ouça o resultado e faça download

## 📋 Exemplos de Uso

### Música Mariana em Sol Maior
```
Tom: G
Estilo: Mariano (Devoção à Nossa Senhora)
Sentimentos: "devoção, gratidão, proteção maternal"
```

### Hino Litúrgico em Ré Maior
```
Tom: D
Estilo: Litúrgico (Para Missa)
Sentimentos: "adoração eucarística, comunhão, reverência"
```

## 🎵 Estrutura Musical

### Tons Suportados
- **Naturais**: C, D, E, F, G, A, B
- **Sustenidos/Bemóis**: C#/Db, D#/Eb, F#/Gb, G#/Ab, A#/Bb

### Estilos e Características

| Estilo | Progressão | Tempo | Uso Recomendado |
|--------|------------|-------|-----------------|
| Tradicional | I-V-vi-IV | Moderato | Hinos clássicos |
| Contemporâneo | vi-IV-I-V | Allegro | Música moderna |
| Gregoriano | Modal | Largo | Contemplação |
| Mariano | I-IV-V-I | Andante | Devoção mariana |
| Litúrgico | I-iii-V-IV | Moderato | Celebrações |

## 🔧 Configuração Avançada

### Personalização de Estilos
Edite o arquivo `config.py` para:
- Adicionar novos estilos musicais
- Modificar progressões harmônicas
- Ajustar configurações de áudio

### Variáveis de Ambiente
```bash
# Configurações opcionais
OPENAI_API_KEY=sua_chave_openai
STREAMLIT_SERVER_PORT=8501
```

## 🐳 Docker (Opcional)

### Usando DevContainer
O projeto inclui configuração DevContainer para desenvolvimento:

```bash
# Abra no VS Code com DevContainer
code .
# Selecione "Reopen in Container"
```

## 🤝 Contribuição

1. **Fork** o projeto
2. **Crie uma branch** para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
5. **Abra um Pull Request**

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🙏 Agradecimentos

- **Igreja Católica** pela rica tradição musical
- **Comunidade open source** pelas ferramentas utilizadas
- **Compositores católicos** que inspiram este projeto

## 📞 Suporte

Para dúvidas, sugestões ou problemas:
- **Issues**: Abra uma issue no GitHub
- **Email**: clenioti@gmail.com

---

✝️ **Ad Majorem Dei Gloriam** - Para a Maior Glória de Deus

🎵 *Que esta ferramenta possa servir para elevar corações a Deus através da música sacra*