# 🚀 INSTRUÇÕES DE DEPLOY - Compositor de Música Católica

## ⚡ **DEPLOY RÁPIDO (1 MINUTO)**

### **🎈 Streamlit Cloud (RECOMENDADO)**
```bash
# 1. Fork este repositório no GitHub
# 2. Acesse: https://share.streamlit.io
# 3. Login com GitHub
# 4. "New app" → Selecionar seu fork
# 5. Main file: AgentCompose.py
# 6. Deploy automático!
```

**✅ URL final:** `https://[seu-usuario]-composer-agentcompose-[hash].streamlit.app`

---

## 🛠️ **DEPLOY AUTOMATIZADO**

### **Script de Deploy:**
```bash
# Tornar executável
chmod +x deploy.sh

# Deploy para Streamlit Cloud
./deploy.sh streamlit

# Deploy para todas as plataformas
./deploy.sh all

# Apenas testar
./deploy.sh test
```

---

## 🌐 **PLATAFORMAS DISPONÍVEIS**

### **1. 🎈 Streamlit Cloud** (Gratuito)
- ✅ **Otimizado** para Streamlit
- ✅ **SSL** automático
- ✅ **Deploy** via GitHub
- 🔸 **1GB RAM** limite

**Deploy:**
1. Fork repositório
2. Login em [share.streamlit.io](https://share.streamlit.io)
3. New app → GitHub repo
4. Deploy automático!

### **2. 🚀 Railway** ($5/mês gratuito)
- ✅ **Mais recursos**
- ✅ **Escalabilidade**
- ✅ **Banco de dados**
- 🔸 **$5/mês** limite

**Deploy:**
1. Login em [railway.app](https://railway.app)
2. New Project → GitHub
3. Deploy automático!

### **3. 🔷 Render** (Gratuito com sleep)
- ✅ **SSL** automático
- ✅ **Logs** detalhados
- 🔸 **Sleep** após 15min

**Deploy:**
1. Login em [render.com](https://render.com)
2. New Web Service → GitHub
3. Build: `pip install -r requirements.txt`
4. Start: `streamlit run AgentCompose.py --server.port=$PORT --server.address=0.0.0.0`

### **4. 🐳 Docker** (Qualquer servidor)
```bash
# Build
docker build -t compositor-catolico .

# Run
docker run -p 8501:8501 compositor-catolico

# Com Docker Compose
docker-compose up -d
```

---

## 🔧 **CONFIGURAÇÃO DE VARIÁVEIS**

### **Variáveis Obrigatórias:**
```bash
OPENAI_API_KEY=sua_chave_openai_aqui
```

### **Variáveis Opcionais:**
```bash
ENVIRONMENT=production
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### **Como Configurar:**

#### **Streamlit Cloud:**
1. Dashboard → App → Settings
2. Secrets → Edit
3. Adicionar variáveis

#### **Railway:**
1. Dashboard → Project → Variables
2. Adicionar variáveis

#### **Render:**
1. Dashboard → Service → Environment
2. Adicionar variáveis

---

## 📋 **CHECKLIST PRE-DEPLOY**

### **✅ Verificações:**
- [ ] Código commitado no GitHub
- [ ] `requirements.txt` atualizado
- [ ] Variáveis de ambiente configuradas
- [ ] Testes passando
- [ ] Arquivos de configuração criados

### **🧪 Testar Localmente:**
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run AgentCompose.py

# Testar funcionalidades
python test_compositor.py
```

---

## 🚨 **TROUBLESHOOTING**

### **Problemas Comuns:**

#### **1. Erro de Dependências**
```bash
# Solução: Atualizar requirements.txt
pip freeze > requirements.txt
```

#### **2. Erro de Memória**
```bash
# Solução: Otimizar código
# - Usar @st.cache_resource
# - Reduzir imports
# - Limitar tamanho de áudio
```

#### **3. Erro de API Key**
```bash
# Solução: Configurar variável
OPENAI_API_KEY=sua_chave_aqui
```

#### **4. Erro de Port**
```bash
# Solução: Usar variável PORT
--server.port=$PORT
```

### **Logs de Debug:**
```bash
# Streamlit Cloud: Dashboard → Logs
# Railway: Dashboard → Deployments → Logs  
# Render: Dashboard → Logs
# Docker: docker logs container_name
```

---

## 🎯 **RECOMENDAÇÕES POR USO**

### **🏠 Uso Pessoal:**
- **Streamlit Cloud** - Gratuito e simples

### **⛪ Paróquia Pequena:**
- **Railway** - Mais recursos, $5/mês

### **🏛️ Diocese/Organização:**
- **Render** ou **VPS próprio** com Docker

### **👨‍💻 Desenvolvedor:**
- **Docker** em servidor próprio

---

## 📊 **MONITORAMENTO**

### **Métricas Importantes:**
- **Uptime** - Disponibilidade
- **Response Time** - Velocidade
- **Memory Usage** - Uso de RAM
- **Error Rate** - Taxa de erros

### **Ferramentas:**
- **Streamlit Cloud:** Dashboard integrado
- **Railway:** Métricas automáticas
- **Render:** Logs detalhados
- **Docker:** Prometheus + Grafana

---

## 🔄 **ATUALIZAÇÕES**

### **Deploy Contínuo:**
1. **Push** para GitHub
2. **Deploy automático** nas plataformas
3. **Verificar** funcionamento
4. **Monitorar** logs

### **Rollback:**
```bash
# Git
git revert HEAD
git push

# Docker
docker run previous_image_tag
```

---

## 🆘 **SUPORTE**

### **Documentação:**
- [Streamlit Docs](https://docs.streamlit.io)
- [Railway Docs](https://docs.railway.app)
- [Render Docs](https://render.com/docs)
- [Docker Docs](https://docs.docker.com)

### **Comunidade:**
- [Streamlit Forum](https://discuss.streamlit.io)
- [Railway Discord](https://discord.gg/railway)
- [Stack Overflow](https://stackoverflow.com)

---

## 🎵 **DEPLOY FINALIZADO!**

### **Próximos Passos:**
1. ✅ **Testar** todas as funcionalidades
2. ✅ **Configurar** domínio personalizado (opcional)
3. ✅ **Monitorar** performance
4. ✅ **Backup** regular dos dados
5. ✅ **Atualizar** conforme necessário

### **URLs de Exemplo:**
- **Streamlit:** `https://usuario-composer-agentcompose-abc123.streamlit.app`
- **Railway:** `https://compositor-catolico-production.up.railway.app`
- **Render:** `https://compositor-catolico.onrender.com`

---

## ✝️ **Ad Majorem Dei Gloriam!**

**🎵 Seu Compositor de Música Católica está agora disponível online para servir a Igreja em todo o mundo! ✝️🎵**

**Que esta ferramenta possa elevar corações a Deus através da música sacra!**
