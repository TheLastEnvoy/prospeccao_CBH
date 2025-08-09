# 🔍 Guia de Teste - Palavras-chave

## ✅ Como Testar o Filtro de Palavras-chave

### 📋 **Cenário de Teste: Palmeira + "rural"**

1. **Abra o dashboard:** http://127.0.0.1:8000

2. **Selecione o município:**
   - No campo "Município", digite "Palmeira"
   - Clique no botão verde "+" ou pressione Enter
   - Verifique se "Palmeira" aparece como uma tag verde

3. **Adicione palavra-chave (Método 1 - Recomendado):**
   - No campo "Palavras-chave", digite "rural"
   - Pressione **Enter** ou clique no botão azul "+"
   - Verifique se "rural" aparece como uma tag azul

4. **Ou digite diretamente (Método 2 - Novo):**
   - No campo "Palavras-chave", digite "rural" 
   - **NÃO** pressione Enter nem clique em +
   - Vá direto para o próximo passo

5. **Execute a busca:**
   - Clique no botão "Filtrar Dados"
   - Abra o Console do navegador (F12) para ver os logs de debug

6. **Resultado esperado:**
   - **4 OSCs** devem ser encontradas
   - Nomes das OSCs:
     - FUNDACAO MEDICO ASSISTENCIAL DO TRAB RURAL DE PALMEIRA
     - CENTRO DE ESTUDOS E ASSESSORIA AO DESENVOLVIMENTO RURAL SUSTENTAVEL E SOLIDARIO
     - ASSOCIACAO RURAL DE PALMEIRA
     - SOCIEDADE RURAL DE PALMEIRA

---

## 🐛 **Logs de Debug no Console**

Quando você executar a busca, deve ver no console:

```
🔤 Tentando adicionar palavra-chave: rural
📝 Array atual de palavras-chave: []
✅ Palavra-chave adicionada. Array atualizado: ["rural"]

🔍 Filtros coletados: {municipio: "Palmeira", palavras_chave: "rural", ...}
📝 Array de palavras-chave: ["rural"]
🏙️ Array de municípios: ["Palmeira"]

📤 Dados a serem enviados: {municipio: "Palmeira", palavras_chave: "rural", ...}
🔍 Detalhes dos filtros:
  - Município: Palmeira
  - Palavras-chave: rural
  - Natureza jurídica: 
  - Naturezas para ver: []
```

---

## 🔧 **Melhorias Implementadas**

### 1. **Dupla Funcionalidade**
- **Método 1:** Adicionar palavras-chave explicitamente (botão + ou Enter)
- **Método 2:** Digitar diretamente e clicar em "Filtrar Dados"

### 2. **Interface Melhorada**
- Placeholder mais claro: "Digite e pressione Enter ou clique +"
- Instruções visuais: "💡 Digite uma palavra e pressione Enter para adicionar à busca"

### 3. **Logs de Debug**
- Console mostra exatamente o que está sendo enviado
- Facilita identificar problemas

---

## 🧪 **Testes Adicionais**

### Teste 1: Múltiplas Palavras-chave
1. Município: "Palmeira"
2. Palavras-chave: "rural" + "agua"
3. Resultado esperado: **5 OSCs** (rural OU agua)

### Teste 2: Só Palavras-chave (sem município)
1. Município: (vazio)
2. Palavras-chave: "rural"
3. Resultado esperado: **553 OSCs** em todo o Paraná

### Teste 3: Case Insensitive
1. Município: "Palmeira"
2. Palavras-chave: "RURAL" (maiúsculo)
3. Resultado esperado: **4 OSCs** (mesmo resultado)

---

## ❌ **Se Não Funcionar**

### Verificações:
1. **Console do navegador:** Há erros JavaScript?
2. **Network tab:** A requisição está sendo enviada?
3. **Servidor Django:** Há erros no terminal?

### Possíveis Problemas:
1. **JavaScript desabilitado**
2. **CSRF token inválido**
3. **Banco de dados não encontrado**
4. **Servidor não rodando**

---

## 📊 **Dados de Validação**

### OSCs em Palmeira com "rural":
- **Total:** 4 OSCs
- **Nomes completos:**
  1. FUNDACAO MEDICO ASSISTENCIAL DO TRAB RURAL DE PALMEIRA
  2. CENTRO DE ESTUDOS E ASSESSORIA AO DESENVOLVIMENTO RURAL SUSTENTAVEL E SOLIDARIO
  3. ASSOCIACAO RURAL DE PALMEIRA
  4. SOCIEDADE RURAL DE PALMEIRA

### Estatísticas Gerais:
- **Total OSCs:** 50.585
- **Municípios:** 399
- **OSCs em Palmeira:** 171
- **OSCs com "rural" (geral):** 553

---

## 🚀 **Próximos Passos**

Se o teste passar:
1. ✅ Sistema funcionando corretamente
2. ✅ Interface melhorada
3. ✅ Dupla funcionalidade implementada

Se o teste falhar:
1. 🔍 Verificar logs de debug
2. 🔧 Investigar problema específico
3. 🛠️ Aplicar correção direcionada
