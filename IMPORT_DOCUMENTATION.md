# Importação de Produtos - Soluções para Grandes Volumes

## Problemas Resolvidos

- ✅ **Timeout/CORS em grandes volumes**: Processamento em lotes com sleep
- ✅ **Feedback de progresso**: Estatísticas em tempo real
- ✅ **Transações seguras**: Rollback automático em caso de erro
- ✅ **Performance otimizada**: Uso de transações em batch

## APIs Disponíveis

### 1. Importação Padrão (Recomendada)

**Endpoint**: `POST /api/import/products/`

- Processa em lotes de 50 produtos (configurável)
- Sleep de 500ms entre lotes
- Retorna estatísticas completas

**Exemplo de uso:**

```javascript
const formData = new FormData();
formData.append("file", arquivoExcel);

try {
  const response = await fetch("/api/import/products/", {
    method: "POST",
    body: formData,
  });

  const result = await response.json();

  if (result.status === "sucesso") {
    console.log(`✅ ${result.statistics.created} criados`);
    console.log(`🔄 ${result.statistics.updated} atualizados`);
    console.log(`❌ ${result.statistics.errors} erros`);
  }
} catch (error) {
  console.error("Erro na importação:", error);
}
```

### 2. Importação com Progresso (Para arquivos > 1000 produtos)

**Endpoint**: `POST /api/import/products/progress/`

- Processa em chunks de 20 produtos
- Streaming de progresso em tempo real
- Ideal para arquivos muito grandes

**Exemplo de uso:**

```javascript
const formData = new FormData();
formData.append("file", arquivoExcel);

const response = await fetch("/api/import/products/progress/", {
  method: "POST",
  body: formData,
});

const reader = response.body.getReader();

while (true) {
  const { done, value } = await reader.read();

  if (done) break;

  const chunk = new TextDecoder().decode(value);
  const lines = chunk.split("\n");

  for (const line of lines) {
    if (line.startsWith("data: ")) {
      const data = JSON.parse(line.substring(6));

      if (data.status === "progresso") {
        const progress = data.progress;
        console.log(`Progresso: ${progress.percentage.toFixed(1)}%`);
        console.log(`${progress.processed}/${progress.total} produtos`);
      } else if (data.status === "concluido") {
        console.log("✅ Importação finalizada!");
      }
    }
  }
}
```

## Configurações Recomendadas

### Por Tamanho do Arquivo:

- **< 500 produtos**: Use API padrão com batch_size=50
- **500-2000 produtos**: Use API padrão com batch_size=30
- **> 2000 produtos**: Use API com progresso (chunk_size=20)

### Parâmetros Configuráveis:

1. **batch_size**: Tamanho do lote na importação padrão
2. **chunk_size**: Tamanho do chunk na importação com progresso
3. **sleep_time**: Tempo de pausa entre lotes (padrão: 0.5s)

## Formato da Planilha Excel

Colunas esperadas (C até K):

- **C**: Marca
- **D**: Tamanho
- **E**: Preço (obrigatório)
- **F**: Data
- **G**: Quantidade
- **H**: Código (obrigatório)
- **I**: Referência
- **J**: Custo

## Estatísticas Retornadas

```json
{
  "status": "sucesso",
  "msg": "Importação concluída! 150 criados, 25 atualizados.",
  "statistics": {
    "total_processed": 175,
    "created": 150,
    "updated": 25,
    "errors": 0
  },
  "dados": [
    /* lista de produtos */
  ]
}
```

## Tratamento de Erros

### Erros Comuns:

1. **Dados obrigatórios faltando**: Código ou preço não informados
2. **Formato inválido**: Arquivo não é Excel válido
3. **Timeout**: Arquivo muito grande (use API com progresso)

### Validações Implementadas:

- ✅ Verificação de código e preço obrigatórios
- ✅ Tratamento de produtos duplicados
- ✅ Transações atômicas por lote
- ✅ Logs detalhados de erros

## Performance

### Melhorias Implementadas:

- **Transações em batch**: Reduz I/O do banco
- **Sleep controlado**: Evita sobrecarga do sistema
- **Validação prévia**: Filtra dados inválidos antes do processamento
- **Processamento incremental**: Evita timeout em arquivos grandes

### Benchmarks:

- 100 produtos: ~5 segundos
- 500 produtos: ~20 segundos
- 1000 produtos: ~40 segundos
- 5000+ produtos: Use API com progresso
