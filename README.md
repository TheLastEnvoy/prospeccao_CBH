# 🌊 Dashboard de Prospecção - Comitês de Bacias Hidrográficas do Paraná

> **Ferramenta para facilitar o trabalho de prospecção de Organizações da Sociedade Civil (OSCs) relacionadas aos Comitês de Bacias Hidrográficas do estado do Paraná.**

## 🔗 Acesso Online

**🌐 [https://prospeccao-cbh.onrender.com](https://prospeccao-cbh.onrender.com)**

---

## 🎯 Objetivo

Esta ferramenta foi desenvolvida para **otimizar o processo de prospecção** de organizações que podem ter interesse ou atuação relacionada aos **Comitês de Bacias Hidrográficas do Paraná**, facilitando:

- 🔍 **Identificação rápida** de OSCs por município
- 🏷️ **Filtragem por natureza jurídica** (Associações, Fundações, etc.)
- 🔎 **Busca por palavras-chave** relacionadas a meio ambiente, água, sustentabilidade
- 📊 **Exportação de dados** para contato e análise
- 🗺️ **Visualização geográfica** da distribuição das organizações

## 📊 Base de Dados

- **50.585 OSCs** cadastradas no Paraná
- **399 municípios** cobertos
- **4 tipos** de natureza jurídica
- Dados atualizados e validados

## ⚡ Funcionalidades Principais

### 🔍 **Filtros Inteligentes**
- **Múltiplos municípios:** Selecione várias cidades simultaneamente
- **Múltiplas naturezas jurídicas:** Combine diferentes tipos de organização
- **Palavras-chave ambientais:** Busque por termos como "água", "ambiental", "sustentável", "rural"
- **Filtros combinados:** Use todos os critérios juntos para prospecção precisa

### 📋 **Visualização Otimizada**
- Interface responsiva e moderna
- Tabela com todas as informações de contato
- Estatísticas em tempo real
- Paginação inteligente

### 📥 **Exportação Profissional**
- Download em Excel (.xlsx)
- Dados filtrados prontos para uso
- Formatação automática das colunas
- Timestamp no nome do arquivo

## 🚀 Tecnologias

- **Backend:** Django 4.2.7 + Python 3.11
- **Frontend:** Bootstrap 5 + jQuery + DataTables
- **Mapas:** Leaflet.js
- **Deploy:** Render.com (sempre online)

## 💡 Casos de Uso

### Para Comitês de Bacias Hidrográficas:
- Identificar OSCs ambientais em municípios específicos
- Prospectar organizações para parcerias e projetos
- Mapear potenciais participantes em ações de conservação
- Facilitar comunicação com sociedade civil organizada

### Para Gestores Públicos:
- Encontrar organizações para consultas públicas
- Identificar parceiros para projetos ambientais
- Mapear atores locais em recursos hídricos

### Para Pesquisadores:
- Análise da distribuição de OSCs ambientais
- Estudos sobre sociedade civil e meio ambiente
- Mapeamento de organizações por região

## 🔧 Execução Local

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd dashboard_prospeccao

# 2. Instale dependências
pip install -r requirements.txt

# 3. Execute o servidor
python manage.py runserver

# 4. Acesse: http://localhost:8000
```

## 📈 Exemplos de Prospecção

### Cenário 1: OSCs Ambientais em Curitiba
```
Filtros: Município = "Curitiba" + Palavras-chave = "ambiental água"
Resultado: 45 organizações encontradas
```

### Cenário 2: Associações Rurais na Região Metropolitana
```
Filtros: Múltiplos municípios + Natureza = "Associação" + Palavra-chave = "rural"
Resultado: 127 organizações encontradas
```

### Cenário 3: Fundações de Conservação
```
Filtros: Natureza = "Fundação" + Palavras-chave = "conservação sustentável"
Resultado: 23 organizações encontradas
```

## 🗺️ Cobertura Geográfica

O dashboard cobre **100% dos municípios** do Paraná:
- Região Metropolitana de Curitiba
- Norte Pioneiro
- Norte Central
- Noroeste
- Oeste
- Sudoeste
- Centro-Sul
- Sudeste
- Centro-Oriental
- Centro-Ocidental

## 📞 Suporte

Para dúvidas sobre o uso da ferramenta ou sugestões de melhorias, abra uma issue no GitHub.

---

