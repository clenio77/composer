#!/bin/bash

# Script de Deploy Automatizado - Compositor de Música Católica
# Uso: ./deploy.sh [plataforma]
# Plataformas: streamlit, railway, render, docker, all

set -e

echo "🎵✝️ DEPLOY - Compositor de Música Católica ✝️🎵"
echo "=================================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se Git está limpo
check_git_status() {
    log_info "Verificando status do Git..."
    
    if [ -n "$(git status --porcelain)" ]; then
        log_warning "Há mudanças não commitadas. Commitando automaticamente..."
        git add .
        git commit -m "🚀 Deploy automático - $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    log_success "Git status OK"
}

# Verificar dependências
check_dependencies() {
    log_info "Verificando dependências..."
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 não encontrado!"
        exit 1
    fi
    
    # Verificar pip
    if ! command -v pip &> /dev/null; then
        log_error "pip não encontrado!"
        exit 1
    fi
    
    # Instalar dependências
    log_info "Instalando dependências..."
    pip install -r requirements.txt > /dev/null 2>&1
    
    log_success "Dependências OK"
}

# Testar aplicação
test_app() {
    log_info "Testando aplicação..."
    
    # Teste básico de import
    python3 -c "
import AgentCompose
print('✅ Import successful')
" || {
        log_error "Teste de import falhou!"
        exit 1
    }
    
    # Executar testes se existirem
    if [ -f "test_compositor.py" ]; then
        python3 test_compositor.py || {
            log_error "Testes falharam!"
            exit 1
        }
    fi
    
    log_success "Testes OK"
}

# Deploy para Streamlit Cloud
deploy_streamlit() {
    log_info "Preparando deploy para Streamlit Cloud..."
    
    # Verificar se arquivo de configuração existe
    if [ ! -f ".streamlit/config.toml" ]; then
        log_error "Arquivo .streamlit/config.toml não encontrado!"
        exit 1
    fi
    
    # Push para GitHub (Streamlit Cloud detecta automaticamente)
    git push origin master || git push origin main
    
    log_success "Deploy para Streamlit Cloud iniciado!"
    log_info "Acesse: https://share.streamlit.io para monitorar"
}

# Deploy para Railway
deploy_railway() {
    log_info "Preparando deploy para Railway..."
    
    # Verificar se Railway CLI está instalado
    if ! command -v railway &> /dev/null; then
        log_warning "Railway CLI não encontrado. Instalando..."
        npm install -g @railway/cli
    fi
    
    # Login (se necessário)
    railway login
    
    # Deploy
    railway up
    
    log_success "Deploy para Railway concluído!"
}

# Deploy para Render
deploy_render() {
    log_info "Preparando deploy para Render..."
    
    # Verificar se arquivo de configuração existe
    if [ ! -f "render.yaml" ]; then
        log_error "Arquivo render.yaml não encontrado!"
        exit 1
    fi
    
    # Push para GitHub (Render detecta automaticamente)
    git push origin master || git push origin main
    
    log_success "Deploy para Render iniciado!"
    log_info "Acesse: https://dashboard.render.com para monitorar"
}

# Build Docker
build_docker() {
    log_info "Construindo imagem Docker..."
    
    # Build da imagem
    docker build -t compositor-catolico:latest .
    
    # Testar container
    log_info "Testando container Docker..."
    docker run -d -p 8501:8501 --name test-compositor compositor-catolico:latest
    
    # Aguardar inicialização
    sleep 30
    
    # Testar health check
    if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        log_success "Container Docker funcionando!"
    else
        log_error "Container Docker falhou no teste!"
        docker logs test-compositor
        docker stop test-compositor
        docker rm test-compositor
        exit 1
    fi
    
    # Limpar teste
    docker stop test-compositor
    docker rm test-compositor
    
    log_success "Imagem Docker criada com sucesso!"
}

# Deploy completo
deploy_all() {
    log_info "Iniciando deploy completo..."
    
    check_git_status
    check_dependencies
    test_app
    
    deploy_streamlit
    deploy_render
    build_docker
    
    log_success "Deploy completo finalizado!"
}

# Menu principal
case "${1:-help}" in
    "streamlit")
        check_git_status
        check_dependencies
        test_app
        deploy_streamlit
        ;;
    "railway")
        check_git_status
        check_dependencies
        test_app
        deploy_railway
        ;;
    "render")
        check_git_status
        check_dependencies
        test_app
        deploy_render
        ;;
    "docker")
        check_dependencies
        test_app
        build_docker
        ;;
    "all")
        deploy_all
        ;;
    "test")
        check_dependencies
        test_app
        ;;
    "help"|*)
        echo "Uso: $0 [comando]"
        echo ""
        echo "Comandos disponíveis:"
        echo "  streamlit  - Deploy para Streamlit Cloud"
        echo "  railway    - Deploy para Railway"
        echo "  render     - Deploy para Render"
        echo "  docker     - Build imagem Docker"
        echo "  all        - Deploy completo (todas as plataformas)"
        echo "  test       - Apenas executar testes"
        echo "  help       - Mostrar esta ajuda"
        echo ""
        echo "Exemplos:"
        echo "  $0 streamlit"
        echo "  $0 all"
        ;;
esac

echo ""
log_success "Script finalizado!"
echo "🎵✝️ Ad Majorem Dei Gloriam! ✝️🎵"
