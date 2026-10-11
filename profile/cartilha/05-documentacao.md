# Padrões de documentação: C4 Model e Scan Systems

[← Voltar ao catálogo da cartilha](../README.md)

A CTIC adota uma política clara de governança: **projeto sem documentação técnica não recebe ambiente no GCP.**

A infraestrutura não desenvolve as regras de negócio e não tem como adivinhar o comportamento de dezenas de microsserviços. A documentação técnica é o contrato formal que permite à infraestrutura dimensionar recursos (CPU, memória, instâncias mínimas, banco de dados, storage e filas) sem custos excessivos de nuvem e sem riscos de indisponibilidade.

---

## 1. O Modelo C4 (C4 Architecture Model)

O C4 model descreve a arquitetura de software em diferentes níveis de zoom. Em Suape, todos os diagramas são escritos em sintaxe **Mermaid** diretamente nos arquivos Markdown, garantindo renderização nativa na interface web do GitHub.

### Os níveis de documentação em Suape

| Nível | Arquivo no repositório | O que deve mostrar | Obrigatoriedade |
|---|---|---|---|
| **Nível 1: Contexto** | `docs/architecture/c4-context.md` | O sistema como uma caixa central, os tipos de usuários (ex.: operador do porto, vistoriador, cidadão) e todos os sistemas externos integrados (ex.: SEI, Gemini, SMTP, APIs externas). | **Obrigatório** |
| **Nível 2: Contêineres** | `docs/architecture/c4-containers.md` | O mapa de todas as aplicações implantáveis: frontend (`web/`), backend (`api/`), jobs, bancos de dados (PostgreSQL/Cloud SQL), buckets de armazenamento (GCS) e filas. | **Obrigatório** |
| **Nível 3: Componentes** | `docs/architecture/c4-components-<parte>.md` | A decomposição interna de um contêiner complexo (ex.: controllers, services, repositories). | Opcional (apenas quando agregar valor a lógicas densas) |
| **Nível 4: Deployment** | `docs/architecture/c4-deployment.md` | O mapeamento exato da arquitetura física no Google Cloud: serviços Cloud Run, instâncias Cloud SQL, buckets GCS, segredos do Secret Manager e jobs do Cloud Scheduler. | **Recomendado** |

### Regras de ouro para diagramas C4 em Mermaid

1. **Rastreabilidade real:** Cada contêiner desenhado no diagrama deve apontar para um arquivo ou pasta real do repositório (com link relativo, ex.: `api/Dockerfile` apontando para `../../api/Dockerfile`). Nunca invente nós ou serviços hipotéticos.
2. **Flechas descritivas e com protocolo:**
   * **Correto:** `Rel(spa, api, "Envia reservas de veículos", "HTTPS/JSON")`
   * **Proibido:** Setas ambíguas com textos genéricos como "usa", "conecta" ou sem especificar o protocolo (ex.: `HTTPS`, `JDBC`, `gRPC`).
3. **Sem dependências ocultas:** Se o sistema ainda conversa com serviços fora do GCP (ex.: Cloudflare ou Vercel), isso deve aparecer em destaque no diagrama como `System_Ext`, permitindo que a infraestrutura aponte o plano de migração.

---

## 2. O Scan Systems (Auditoria de Sistemas)

O Scan Systems é uma auditoria técnica profunda que inspeciona o código-fonte, configurações, dependências e padrões de segurança, gerando dois arquivos padronizados:

1. **`docs/systems/<nome-do-repositorio>.md` (Relatório do Sistema):**
   * Veredito item a item de prontidão para o GCP (conformidade com a cartilha).
   * Inventário de partes publicáveis, portas, comandos de inicialização e rotas de saúde.
   * Lista exata de variáveis de ambiente e segredos (apenas os nomes).
   * Inventário de bancos de dados, migrações e persistência de arquivos.
   * Inventário de rotas expostas e políticas de autenticação.
   * Auditoria de vulnerabilidades de dependências (`pip-audit` / `npm audit`).
   * Tabela de pendências priorizadas por severidade (Bloqueante / Não bloqueante).
2. **`docs/SYSTEMS_CATALOG.md` (Catálogo Consolidado):**
   * Resumo de inventário do repositório para composição do catálogo geral da organização.

---

## 3. Como gerar a documentação usando as Skills oficiais

Você não precisa desenhar diagramas manualmente do zero. A CTIC disponibiliza skills automatizadas para o **AGY (Antigravity)** e para o **Claude Code**.

As skills estão publicadas no repositório [.github da organização](https://github.com/Complexo-Industrial-Suape/.github/tree/main/skills).

### Fluxo de geração passo a passo:

1. **Instale as skills no seu ambiente:**
   * Copie o diretório de skills para `~/.gemini/config/skills/` (no AGY) ou `~/.claude/skills/` (no Claude Code), conforme as instruções no [README de skills](https://github.com/Complexo-Industrial-Suape/.github/tree/main/skills).
2. **Execute a auditoria do Scan Systems na raiz do repositório:**
   ```text
   rode /scan-systems neste repositório
   ```
   A ferramenta vai varrer a base de código, checar a prontidão para o GCP, auditar dependências e gerar `docs/systems/<projeto>.md` e `docs/SYSTEMS_CATALOG.md`.
3. **Execute a geração dos diagramas C4:**
   ```text
   rode /c4-architecture e gere os diagramas de contexto, contêineres e deployment
   ```
   A ferramenta vai produzir os diagramas Mermaid em `docs/architecture/`.
4. **Revisão humana obrigatória:**
   A IA atua como ferramenta de assistência; **você, desenvolvedor, é o responsável técnico que assina o commit.** Abra os arquivos gerados, leia cada tabela e diagrama, corrija eventuais imprecisões e confirme que os links relativos abrem corretamente.

---

## 4. Política de Bloqueio por Documentação

A documentação é checada rigorosamente durante a avaliação do chamado de provisionamento:

* **Bloqueiam o provisionamento:**
  * Ausência de `README.md` com instruções claras de execução e teste.
  * Ausência ou diagrama quebrado em `c4-context.md` ou `c4-containers.md`.
  * Ausência do relatório `docs/systems/<projeto>.md` ou de `docs/SYSTEMS_CATALOG.md`.
  * Variável de ambiente consumida no código que não conste na documentação.
* **Virão pendências (issues), mas não bloqueiam:**
  * Diagramas de componentes ou deployment ausentes.
  * Badges ou referências antigas no README.
  * Variável documentada que não é mais consumida no código.

---

## Checklist de Documentação

- [ ] Arquivo `README.md` na raiz explicando o propósito do sistema, requisitos locais e comandos de teste.
- [ ] Diagrama de Contexto (`docs/architecture/c4-context.md`) renderizando corretamente.
- [ ] Diagrama de Contêineres (`docs/architecture/c4-containers.md`) com todos os componentes publicáveis.
- [ ] Diagrama de Deployment (`docs/architecture/c4-deployment.md`) mapeando serviços GCP.
- [ ] Relatório completo gerado pelo Scan Systems em `docs/systems/<repositorio>.md`.
- [ ] Catálogo atualizado em `docs/SYSTEMS_CATALOG.md`.
- [ ] Todas as variáveis de ambiente necessárias listadas por nome.
- [ ] Nenhum link absoluto de máquina (`file:///`, `/home/...`, `C:\...`) no texto.
