<!--
Template de docs/SYSTEMS_CATALOG.md. Uma linha por repositório documentado.
Se o arquivo já existe, atualize só a linha deste repositório e a data.
Links relativos a docs/.
-->
# Catálogo de sistemas

Atualizado em <AAAA-MM-DD, data da varredura (hoje), não a do último commit>. Gerado pela skill scan-systems.

| Repositório | Commit analisado | O que faz | Partes publicáveis | Banco | Arquivos | Cron | Veredito GCP | Pendências bloqueantes | Relatório |
|---|---|---|---|---|---|---|---|---|---|
| <nome> | <hash curto> | <1 frase> | <web/, api/> | <PostgreSQL / nenhum> | <sim/não> | <não / sim (em processo: ...) / sim (agendador externo: <qual/onde>)> | <pronto / não pronto> | <N> | [systems/<nome>.md](systems/<nome>.md) |

## Dependências entre sistemas

```mermaid
flowchart LR
  %% Só serviços deste catálogo e integrações externas relevantes.
```

## Segurança consolidada

| Repositório | Segredos | Dependências | SQL injection | Headers |
|---|---|---|---|---|
| <nome> | <ok / N achados / não verificado> | | | |
