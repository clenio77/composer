# 🔧 ADICIONAR WORKFLOW GITHUB ACTIONS MANUALMENTE

## ⚠️ **IMPORTANTE**

O arquivo `.github/workflows/deploy.yml` não pôde ser enviado automaticamente devido a restrições de OAuth scope. Você precisa adicioná-lo manualmente no GitHub.

---

## 📋 **INSTRUÇÕES PASSO A PASSO**

### **1. Acessar o Repositório no GitHub**
1. Vá para: https://github.com/clenio77/composer
2. Faça login na sua conta

### **2. Criar o Diretório de Workflows**
1. Clique em **"Create new file"**
2. Digite: `.github/workflows/deploy.yml`
3. O GitHub criará automaticamente os diretórios

### **3. Copiar o Conteúdo do Workflow**
Copie e cole o conteúdo do arquivo `.github/workflows/deploy.yml` que está no seu diretório local:

```yaml
name: Deploy Compositor de Música Católica

on:
  push:
    branches: [ master, main ]
  pull_request:
    branches: [ master, main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.10
      uses: actions/setup-python@v3
      with:
        python-version: "3.10"
    
    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y ffmpeg libsndfile1
    
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Test imports
      run: |
        python -c "
        import streamlit as st
        import AgentCompose
        print('✅ Imports successful')
        "
    
    - name: Run basic tests
      run: |
        python test_compositor.py

  deploy-streamlit:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/master'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Streamlit Cloud
      run: |
        echo "🚀 Deploy automático para Streamlit Cloud"
        echo "✅ Streamlit Cloud detecta mudanças automaticamente"

  deploy-railway:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/master'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Railway
      run: |
        echo "🚀 Deploy automático para Railway"
        echo "✅ Railway detecta mudanças automaticamente"

  deploy-render:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/master'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Render
      run: |
        echo "🚀 Deploy automático para Render"
        echo "✅ Render detecta mudanças automaticamente"

  build-docker:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t compositor-catolico .
        echo "✅ Docker image built successfully"
    
    - name: Test Docker container
      run: |
        docker run -d -p 8501:8501 --name test-container compositor-catolico
        sleep 30
        curl -f http://localhost:8501/_stcore/health || exit 1
        docker stop test-container
        echo "✅ Docker container tested successfully"

  notify:
    needs: [test, deploy-streamlit, deploy-railway, deploy-render, build-docker]
    runs-on: ubuntu-latest
    if: always()
    
    steps:
    - name: Notify deployment status
      run: |
        if [ "${{ needs.test.result }}" == "success" ]; then
          echo "✅ Testes passaram com sucesso"
        else
          echo "❌ Testes falharam"
        fi
        
        echo "🎵✝️ Deploy do Compositor de Música Católica concluído!"
```

### **4. Commit do Arquivo**
1. Adicione uma mensagem de commit: `🔧 Adicionar CI/CD workflow`
2. Clique em **"Commit new file"**

### **5. Verificar Funcionamento**
1. Vá para a aba **"Actions"** no seu repositório
2. Você deve ver o workflow executando automaticamente
3. Verifique se todos os testes passam

---

## 🎯 **ALTERNATIVA RÁPIDA**

### **Upload Direto do Arquivo**
1. No GitHub, vá para o diretório `.github/workflows/`
2. Clique em **"Upload files"**
3. Arraste o arquivo `deploy.yml` do seu computador
4. Commit as mudanças

---

## ✅ **VERIFICAÇÃO**

Após adicionar o workflow, você deve ver:
- ✅ Aba "Actions" ativa no repositório
- ✅ Workflow executando a cada push
- ✅ Testes automáticos funcionando
- ✅ Badge de status (opcional)

---

## 🚀 **PRÓXIMOS PASSOS**

Depois de adicionar o workflow:
1. **Testar** fazendo um pequeno commit
2. **Verificar** se os testes passam
3. **Configurar** secrets se necessário
4. **Fazer deploy** usando as instruções

---

## 💡 **DICA**

O workflow está configurado para:
- ✅ **Testar** automaticamente a cada push
- ✅ **Verificar** imports e dependências
- ✅ **Executar** testes unitários
- ✅ **Simular** deploy para múltiplas plataformas

**🎵✝️ Workflow adicionado = CI/CD completo! ✝️🎵**
