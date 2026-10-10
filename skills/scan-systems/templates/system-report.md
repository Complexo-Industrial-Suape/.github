<!--
Template do relatório Scan Systems de Suape. Mantenha títulos, ordem, colunas e
os valores do veredito (atendido | pendente | não se aplica | não verificado).
A infraestrutura lê este arquivo seção a seção. Remova os comentários HTML e os
textos <entre sinais> ao preencher. Links relativos à pasta docs/systems/
(raiz do repositório = ../../). Nenhum valor de variável ou segredo.
-->
# <nome-do-repositorio>

- Repositório: <URL do remoto, ou "sem remoto">
- Commit analisado: <hash curto> · data da varredura: <AAAA-MM-DD de hoje>
- Gerado por: scan-systems, varredura <paralela | sequencial>
- Cartilha de referência: [seção 3](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/README.md#3-antes-de-pedir-ambiente-checklist-do-repositório)

## Resumo para a infraestrutura

- O que o sistema faz: <2 a 3 frases, a partir do código>
- Veredito: **<pronto para provisionar | não pronto: N pendências bloqueantes>**
- Partes publicáveis: <web/, api/, ...>
- Banco: <nenhum | PostgreSQL via ... | ...>
- Armazenamento de arquivos: <nenhum | ...>
- Tarefas agendadas: <nenhuma | em processo: ... | agendador externo: <qual/onde, ou "a confirmar com o dev"> chamando <rota>>
- Sinais para dimensionamento: <cold start sensível? WebSocket? processamento longo? cron em processo?>

## 1. Prontidão para o GCP (seção 3 da cartilha)

| Item | Veredito | Evidência | Observação |
|---|---|---|---|
| 3.1 Repositório na org Complexo-Industrial-Suape | | | |
| 3.1 Nome em kebab-case | | | |
| 3.1 Branches existentes (informativo, nunca pendente) | não se aplica | | <ex.: main, dev, hml> |
| 3.1 Nenhum segredo commitado | | | |
| 3.1 .env.example com todos os nomes e sem valores reais | | | <placeholder genérico ok; e-mail, URL de produção ou ID de projeto real = pendente> |
| 3.1 suape-brand fora do git (nem submódulo, nem commitado) | | | |
| 3.2 Dockerfile em cada parte publicável | | | |
| 3.2 Estrutura web/ api/ docs/ infra/ (front e back no mesmo repo, mesmo em container único) | | | <pendente não bloqueante se fora do padrão> |
| 3.2 Porta via variável PORT | | | |
| 3.2 Configuração só por variáveis de ambiente | | | |
| 3.2 Health 200: /health ou o par /livez + /readyz (/healthz não serve) | | | |
| 3.2 Sem dependência de outro provedor de nuvem | | | <provedores procurados e resultado> |
| 3.2 Testes rodam com um comando | | | |
| 3.2 Sem CVE alta ou crítica nas dependências | | | <bloqueante se houver> |
| 3.3 Documentação obrigatória completa (ver tabela abaixo) | | | <bloqueante se algo ficar ausente ou incompleto> |
| 3.3 README, badges e diagramas sem pipeline inexistente | | | <desatualizado: não bloqueante> |
| 3.3 .env.example coerente com o código | | | <desatualizado: não bloqueante> |

### Documentação obrigatória (seção 3.3)

| Item | Antes desta varredura | Depois | Bloqueia? |
|---|---|---|---|
| README.md: o que faz, como rodar localmente, como rodar os testes | | | |
| docs/architecture/c4-context.md | | | |
| docs/architecture/c4-containers.md | | | |
| docs/systems/<repo>.md (este arquivo) | <ausente | existia> | gerado | não |
| docs/SYSTEMS_CATALOG.md | <ausente | existia> | gerado/atualizado | não |
| Variáveis lidas no código documentadas por nome | | <N de M documentadas> | |

<!-- Estados: ausente | incompleto (<o que falta>) | completo. Incompleto = falta seção obrigatória, diagrama não renderiza ou variável lida no código sem documentação. Bloqueia = sim se o estado "Depois" não for completo. c4-components e c4-deployment são opcionais e não entram aqui. Documentação desatualizada (pipeline inexistente, badge quebrado, .env.example com valor real ou promessa falsa, variável documentada sem uso) fica nas linhas acima, não bloqueante. -->

<!-- Evidência no formato [api/Dockerfile:12](../../api/Dockerfile#L12). -->

## 2. Partes publicáveis

| Parte | Pasta | Dockerfile | Imagem base | Porta (lê PORT?) | Comando de start | Health | USER |
|---|---|---|---|---|---|---|---|

<!-- Uma linha por parte. Pacotes compartilhados não entram aqui. -->

### Diagrama de contêineres

```mermaid
flowchart LR
  %% Cada nó: nome, tecnologia. Cada seta: ação e protocolo.
```

## 3. Variáveis de ambiente e segredos

| Nome | Parte | Lida em | Momento | Segredo? | Obrigatória? | Observação |
|---|---|---|---|---|---|---|

<!--
Momento: build (VITE_*, NEXT_PUBLIC_*, REACT_APP_*, PUBLIC_*, ARG no Dockerfile)
ou runtime. Segredo: sim | não. Variável de build marcada como segredo é
pendência: o valor vai para o bundle público.
Liste também as variáveis do .env.example que o código não lê (coluna
Observação: "declarada, sem uso") e as lidas que faltam no .env.example.
-->

## 4. Dados

### Banco de dados

| Parte | Motor | Driver/ORM | Conexão lida de | Evidência |
|---|---|---|---|---|

### Migrations

- Ferramenta e pasta: <...>
- Como e quando rodam hoje: <CMD do container | script manual | não há>
- Riscos: <destrutivas, USER sem permissão, rodam em cada instância...>

### Armazenamento de arquivos e disco local

| Parte | O que grava | Onde | Persiste no Cloud Run? | Evidência |
|---|---|---|---|---|

<!-- Escrita em /tmp, ./uploads, SQLite: "não". -->

## 5. Tarefas agendadas e integrações externas

### Tarefas agendadas

| Tarefa | Frequência | Como roda hoje (em processo / agendador externo: qual e onde) | Evidência |
|---|---|---|---|

### Integrações externas

| Serviço | Para quê | Parte | Variáveis usadas | Evidência |
|---|---|---|---|---|

## 6. Rotas da API

<!-- Até ~30 rotas: tabela A. Acima: tabela B, mais a lista de rotas expostas. Uma subtabela por API, se houver mais de uma. -->

Tabela A (até ~30 rotas):

| Método | Caminho | Auth | Arquivo | Observação |
|---|---|---|---|---|

Tabela B (agrupada por prefixo ou blueprint):

| Métodos | Prefixo | Nº de rotas | Auth exigida | Arquivo |
|---|---|---|---|---|

Rotas sem autenticação ou chamadas por sistema externo (webhook, Cloud Scheduler): <listar uma a uma com arquivo:linha>

## 7. Testes

| Parte | Comando | Arquivos de teste | Executado? | Resultado | Cobertura |
|---|---|---|---|---|---|

<!-- Cobertura: valor medido ou "não medida". Nunca estimada. -->

## 8. Segurança

| Verificação | Ferramenta usada | Resultado | Achados (severidade, arquivo:linha) |
|---|---|---|---|
| Segredos no código e no histórico | | | |
| Segredo com valor padrão no código | | | <ex.: os.environ.get("SECRET_KEY", "dev-...")> |
| Dependências (CVE) | | | |
| SQL injection | | | |
| Headers HTTP e CORS | | | |

### Vulnerabilidades em dependências

| Pacote | Versão | Severidade | Fonte da severidade | ID (CVE/GHSA/PYSEC) | Versão corrigida | Bloqueia? |
|---|---|---|---|---|---|---|

<!-- Alta/crítica: Bloqueia = sim. Média/baixa: Bloqueia = não. Sem severidade publicada: "a confirmar", Bloqueia = sim, até o dev comprovar. Toda linha vira pendência. Ferramenta indisponível: linha na seção 9. -->

### Fluxos de acesso e permissões

<Quem entra, como autentica, quais papéis existem e onde isso é checado no código. "Sem autenticação" se for o caso, com evidência.>

## 9. Não verificado

| O quê | Motivo | Como o dev fecha |
|---|---|---|

## 10. Pendências (viram issues)

| # | Título da issue | Bloqueia? | Item da cartilha | Arquivo |
|---|---|---|---|---|

<!-- Título no imperativo: "Remover binding D1 do vite.config.ts e usar Cloud SQL". Bloqueia = sim só para: CVE alta/crítica (ou "a confirmar"), uso real de outro provedor, segredo commitado (código ou histórico), parte sem Dockerfile, segredo com valor padrão inseguro no código, documentação obrigatória da 3.3 ausente ou incompleta ao final. O resto: não, inclusive documentação desatualizada. -->
