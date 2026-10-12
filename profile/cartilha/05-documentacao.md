# Documentação técnica: C4 Model e Scan Systems

[← Voltar ao catálogo da cartilha](../README.md)

A regra é simples: **projeto sem documentação técnica não recebe ambiente no GCP.**

A equipe de infraestrutura não programa as regras de negócio e não tem como adivinhar a arquitetura de dezenas de microsserviços. A documentação técnica é o mapa que permite dimensionar CPU, memória, instâncias, banco de dados, storage e filas sem gastar dinheiro público à toa e sem risco de indisponibilidade.

---

## 1. Modelo C4 (C4 Architecture Model)

O modelo C4 descreve a arquitetura em diferentes níveis de detalhe. Todos os diagramas são feitos em sintaxe **Mermaid** nos arquivos Markdown, garantindo visualização direta na interface web do GitHub.

### Níveis exigidos

| Nível | Arquivo no repositório | O que mostra | Obrigatoriedade |
|---|---|---|---|
| **Nível 1: Contexto** | `docs/architecture/c4-context.md` | O sistema no centro, os atores que usam a solução e os sistemas externos integrados (SEI, Gemini, SMTP, APIs de terceiros). | **Obrigatório** |
| **Nível 2: Contêineres** | `docs/architecture/c4-containers.md` | O mapa das partes implantáveis: frontend (`web/`), backend (`api/`), jobs, bancos de dados, buckets e filas. | **Obrigatório** |
| **Nível 3: Componentes** | `docs/architecture/c4-components-<parte>.md` | Detalhe interno de um módulo específico com lógica densa. | Opcional |
| **Nível 4: Deployment** | `docs/architecture/c4-deployment.md` | O mapa real no Google Cloud: serviços Cloud Run, instâncias Cloud SQL, buckets GCS, segredos e agendamentos. | **Recomendado** |

### Boas práticas para diagramas Mermaid

1. **Rastreabilidade real:** Cada contêiner no diagrama precisa corresponder a uma pasta ou arquivo real do código (com link relativo, por exemplo `api/Dockerfile` apontando para `../../api/Dockerfile`). Nada de desenhar serviços hipotéticos.
2. **Setas com ação e protocolo:**
   * **Certo:** `Rel(spa, api, "Envia reservas de veículos", "HTTPS/JSON")`
   * **Evite:** Textos vagos como "usa" ou setas sem indicar o protocolo.
3. **Serviços externos visíveis:** Se o sistema consome algo fora do GCP, mostre como `System_Ext` no diagrama para podermos mapear a integração.

---

## 2. Scan Systems (Auditoria de Sistemas)

O Scan Systems é uma varredura automatizada que confere código, arquivos de configuração, dependências e padrões de segurança, gerando dois arquivos:

1. **`docs/systems/<nome-do-repositorio>.md` (Relatório do Sistema):**
   * Veredito item a item de prontidão para o GCP.
   * Lista de partes publicáveis, portas, comandos de inicialização e rotas de saúde.
   * Nomes das variáveis de ambiente e segredos necessários.
   * Bancos de dados, migrações e armazenamento de arquivos.
   * Rotas expostas e regras de autenticação.
   * Auditoria de dependências (`pip-audit` e `npm audit`).
   * Tabela de pendências priorizadas por gravidade.
2. **`docs/SYSTEMS_CATALOG.md` (Catálogo do Repositório):**
   * Ficha técnica do repositório para o catálogo geral da organização.

---

## 3. Como gerar a documentação com as skills

Você não precisa montar os diagramas e tabelas na mão. Use as skills oficiais para **AGY (Antigravity)** e **Claude Code**.

As skills estão publicadas no repositório [.github da organização](https://github.com/Complexo-Industrial-Suape/.github/tree/main/skills).

### Passo a passo:

1. **Instale as skills:**
   Copie as pastas para `~/.gemini/config/skills/` (no AGY) ou `~/.claude/skills/` (no Claude Code), seguindo o [guia de instalação](https://github.com/Complexo-Industrial-Suape/.github/tree/main/skills).
2. **Rode a auditoria do Scan Systems na raiz do projeto:**
   ```text
   rode /scan-systems neste repositório
   ```
   A skill analisa o código, checa a conformidade com a cartilha e gera `docs/systems/<projeto>.md` e `docs/SYSTEMS_CATALOG.md`.
3. **Gere os diagramas C4:**
   ```text
   rode /c4-architecture e gere os diagramas de contexto, contêineres e deployment
   ```
   A skill cria os arquivos Mermaid em `docs/architecture/`.
4. **Revise os arquivos:**
   As skills aceleram o trabalho, mas **quem assina o commit é você**. Abra os arquivos gerados, leia as tabelas e diagramas, ajuste eventuais imprecisões e confirme que os links funcionam antes de enviar.

---

## 4. O que trava o provisionamento

A documentação é avaliada antes de criarmos qualquer recurso:

* **Bloqueia o chamado:**
  * Falta de `README.md` com instruções de execução e teste.
  * Diagrama ausente ou quebrado em `c4-context.md` ou `c4-containers.md`.
  * Ausência do relatório `docs/systems/<projeto>.md` ou de `docs/SYSTEMS_CATALOG.md`.
  * Variável de ambiente usada no código que não foi documentada.
* **Gera issue, mas não bloqueia:**
  * Falta de diagramas de componentes ou deployment.
  * Badges ou referências antigas no README.
  * Variável documentada que não é mais lida pelo código.

---

## Checklist de conferência

- [ ] Arquivo `README.md` na raiz explicando o que o sistema faz, dependências e testes.
- [ ] Diagrama de Contexto (`docs/architecture/c4-context.md`) renderizando no GitHub.
- [ ] Diagrama de Contêineres (`docs/architecture/c4-containers.md`) cobrindo as partes publicáveis.
- [ ] Diagrama de Deployment (`docs/architecture/c4-deployment.md`) mapeando serviços GCP.
- [ ] Relatório completo em `docs/systems/<repositorio>.md`.
- [ ] Catálogo do repositório em `docs/SYSTEMS_CATALOG.md`.
- [ ] Todas as variáveis de ambiente listadas pelo nome.
- [ ] Nenhum link com caminhos locais de máquina (`file:///`, `/home/...`, `C:\...`).
