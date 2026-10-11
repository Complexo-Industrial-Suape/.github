---
name: scan-systems
description: >-
  Gera o relatório Scan Systems exigido pela CTIC de Suape para provisionar
  ambiente no GCP (Cloud Run, Cloud SQL, Secret Manager, Cloud Build):
  docs/systems/<repositorio>.md e docs/SYSTEMS_CATALOG.md, com veredito item a
  item da seção 4 da cartilha (evidência arquivo:linha), partes publicáveis,
  variáveis de ambiente e segredos só por nome (build x runtime), banco,
  armazenamento, cron, integrações, rotas, testes, segurança e pendências que
  viram issues. Documentação obrigatória ausente ou incompleta bloqueia.
  Detecta dependência escondida de Cloudflare, Vercel, AWS,
  Supabase ou Firebase e suape-brand commitado ou como submódulo. Use antes de
  abrir o chamado de provisionamento, ao revisar se um repositório está pronto
  para o GCP ou ao atualizar a documentação depois de mudar arquitetura, banco
  ou serviço externo. Gatilhos: "scan systems", "/scan-systems", "rode o scan
  systems", "documentar para provisionamento", "pronto para o GCP", "chamado de
  provisionamento", "catálogo de sistemas", "prepare this repo for GCP
  provisioning", "systems catalog", "GCP readiness report".
---

# Scan Systems (Suape)

Você vai produzir, no repositório atual, os dois arquivos que o responsável pela infraestrutura da CTIC lê antes de provisionar: `docs/systems/<nome-do-repositorio>.md` e `docs/SYSTEMS_CATALOG.md`. Ele não roda o projeto nem conhece o código. Com o que você escrever, ele decide se provisiona, dimensiona Cloud Run e Cloud SQL (projeto `inovacao-491419`, região `southamerica-east1`), cria os segredos no Secret Manager a partir dos nomes listados, configura o Cloud Build por pasta e abre issues para o que faltar.

Pense como o inspetor, não como o autor do projeto. A pergunta em cada seção é: "a infra consegue agir com isto sem abrir o código?". Se a resposta depende de adivinhar, falta evidência ou falta uma pendência.

A régua são os três documentos de checklist da cartilha: [Repositório (4.1)](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/03-repositorio.md), [Pronto para o GCP (4.2)](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/04-pronto-para-o-gcp.md) e [Documentação (4.3)](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/05-documentacao.md). A numeração 4.1, 4.2 e 4.3 vem da cartilha 2.x e continua sendo usada nesta skill. Se tiver acesso à web, leia a versão atual; se não, use os itens resumidos em [references/gcp-readiness-checks.md](references/gcp-readiness-checks.md), que reproduz a versão 2.2.

## O que um modelo genérico erra aqui

Estes casos já aconteceram em Suape. Cada um passou por um relatório "bonito" e travou o provisionamento:

- Projeto gerado por ferramenta de IA com template Cloudflare escondido no `vite.config` (binding D1 e R2) e nada no README. Só aparece lendo config e lockfile.
- README que afirma "deploy na Vercel" ou "roda no Cloud Run" sem nenhum arquivo que confirme. O README é alegação; código e config são evidência.
- SQLite gravando em `/tmp` ou no diretório do container. No Cloud Run o disco é efêmero: os dados somem a cada reinício ou nova revisão.
- Dockerfile com `USER` não-root antes de rodar migration que escreve em pasta do root: o build passa, o container quebra ao subir.
- `VITE_*`/`NEXT_PUBLIC_*` embutidos no bundle: o mesmo build não serve para dev, hml e prod. Exige build por ambiente.
- CORS da API amarrado a uma URL `*.run.app` ou `localhost` fixa no código: quebra assim que a URL do ambiente muda.
- Documentação com `file:///` e caminhos `/home/...` ou `C:\Users\...`: os links só abrem na máquina de quem gerou.

## Regras (NUNCA)

- NUNCA escreva o valor de uma variável ou segredo, nem mascarado (`sk-****abc`). O relatório fica no GitHub; parte do valor já ajuda um atacante. Só o nome e onde é lido.
- NUNCA marque um item como atendido sem `arquivo:linha`. A infra usa o veredito para decidir; "atendido" sem prova vira provisionamento quebrado e retrabalho de ida e volta por e-mail.
- NUNCA aceite o README como prova de plataforma, porta ou banco. Confirme no Dockerfile, no código de bootstrap e no manifesto. Divergência entre README e código é pendência.
- NUNCA diga "verificado" para algo que você não executou. Se `pip-audit`, `npm audit`, `docker` ou rede não estavam disponíveis, escreva "não verificado: <motivo>". Um "sem vulnerabilidades" falso é pior que uma lacuna declarada.
- NUNCA invente rotas, tabelas, cron ou integrações para completar o template. Seção vazia leva "nenhum encontrado" e a busca que você fez.
- NUNCA use link absoluto de máquina nem `file:///`. A partir de `docs/systems/`, a raiz do repositório é `../../`. A única URL absoluta permitida é a da cartilha (pública).
- NUNCA altere código, Dockerfile ou config do projeto durante o scan. Você documenta; quem corrige é o dev, a partir das pendências. Mexer agora esconde o problema que a infra precisa ver.
- NUNCA mude a estrutura do template (títulos, ordem, colunas, valores do veredito). A infra lê esses arquivos com o mesmo roteiro para todo projeto.

## Fluxo

### 1. Reconhecimento (você, antes de delegar)

1. Nome do repositório: `git remote get-url origin`; sem remoto, o nome da pasta raiz. Use esse nome no arquivo. Se não estiver em kebab-case, registre pendência de nome (item 4.1), mas não renomeie o arquivo para "corrigir".
2. Partes publicáveis: procure `Dockerfile*`, `package.json`, `pyproject.toml`, `requirements*.txt`, `go.mod`, `pom.xml` até 3 níveis, ignorando `node_modules`, `.venv`, `dist`, `build`, `suape-brand`. Uma parte publicável é o que vira um serviço ou job no Cloud Run: `web/`, `api/`, um worker. Pacote compartilhado (`packages/shared`) não é parte: documente dentro de quem o usa.
3. Leia o README e o que existir em `docs/` só para saber o que o projeto **alega**. Guarde as alegações para confrontar depois.

Decisão do formato:

| Encontrou | Faça |
|---|---|
| Uma parte (repo só API ou só web) | Um relatório, sem subagentes. |
| `web/` + `api/` (o caso comum) ou mais partes | Um subagente por parte, em paralelo, se o runtime oferecer. |
| Front e back no mesmo repo fora de `web/` + `api/` (ex.: backend na raiz + `frontend/`) | Varra como está, inclusive se for um container só. Registre pendência de estrutura (4.2), **não bloqueante**. A regra vale mesmo com uma imagem única: um Dockerfile copia `web/` e `api/`. |
| Nenhum manifesto reconhecível | Pare e diga ao dev o que encontrou; não gere relatório vazio. |

### 2. Varredura por parte

**MANDATORY**: antes de varrer, leia inteiro [references/gcp-readiness-checks.md](references/gcp-readiness-checks.md). Ele tem os padrões de busca de cada item da seção 4, a detecção de outros provedores e de `suape-brand`, e os fallbacks quando uma ferramenta não existe.

Com subagentes (Claude Code: ferramenta Agent/Task; Antigravity: subagente do AGY), dispare todos juntos, um por parte. **MANDATORY**: monte cada prompt a partir de [references/subagent-brief.md](references/subagent-brief.md), trocando só o nome e a pasta da parte. O subagente devolve texto no formato das seções do template; ele não grava arquivo. Só você escreve em `docs/`, para não haver dois agentes editando o mesmo relatório.

Sem subagentes, faça a mesma rotina parte por parte e anote no relatório "varredura sequencial".

A rotina, por parte:

1. Prontidão GCP: cada item da seção 4 aplicável à parte, com evidência.
2. Publicação: Dockerfile, porta, comando de start, health, usuário do container.
3. Variáveis: toda leitura de ambiente no código e nos arquivos de config, classificada em build ou runtime.
4. Dados: banco e driver, migrations e como rodam, armazenamento de arquivos, uso de disco local.
5. Agendado e externo: cron, filas, jobs, chamadas a APIs de terceiros. Endpoint chamado por agendador externo (Cloud Scheduler, cron de outro sistema) conta como cron: escreva "sim (agendador externo: <qual/onde>)", ou "a confirmar com o dev" se o repositório não diz quem chama.
6. Rotas: até ~30 rotas, uma linha por rota. Acima disso, agrupe por prefixo ou blueprint/router (método, prefixo, contagem, auth exigida, arquivo) e liste uma a uma só as rotas sem auth e as chamadas por sistema externo (webhook, Cloud Scheduler). A infra quer saber o que fica exposto, não o catálogo inteiro.
7. Testes: comando real (do `package.json`/`pyproject.toml`/CI) e cobertura. Rode se o comando existir e as dependências estiverem instaladas ou instaláveis localmente, com limite de 10 min (`timeout 600 <comando>`). Estourou o limite ou exige banco/serviço externo: "não executado: <motivo>".
   Build da imagem: se `docker` existir, rode `timeout 900 docker build -t scan-<parte> <pasta>` sem pedir permissão (é local e não tem efeito externo). Sem docker ou estourou 15 min: "não verificado".
8. Segurança: segredos no código e no histórico; CVE com `pip-audit` e `npm audit --omit=dev` (fallbacks em `gcp-readiness-checks.md`); SQL montado por concatenação; headers e CORS na configuração do código (não há URL publicada antes do provisionamento). CVE **alta ou crítica bloqueia** o provisionamento; média ou baixa vira pendência não bloqueante. `pip-audit` não informa severidade: consulte cada ID em `https://api.osv.dev/v1/vulns/<ID>` (campos `severity` ou `database_specific.severity`). IDs `PYSEC-*` costumam vir sem severidade: siga o alias `GHSA-*` do campo `aliases`, que traz `database_specific.severity` (LOW/MODERATE/HIGH/CRITICAL). Sem severidade publicada ou sem rede: "a confirmar", tratada como **bloqueante** até o dev comprovar.

### 3. Arquitetura e intenção

- Confronte as alegações do passo 1 com a varredura. Toda divergência que afete deploy (plataforma, banco, porta, auth) vira pendência. Dois casos comuns que passam despercebidos:
  - README, badge ou diagrama citando pipeline que não existe mais (ex.: badge de `.github/workflows/deploy.yml` depois que o deploy foi para o Cloud Build). Confira com `ls .github/workflows` e `test -e cloudbuild.yaml`.
  - `.env.example` prometendo comportamento que o código não tem (ex.: "sem DATABASE_URL usa SQLite" quando o código exige Postgres). Confira cada comentário do `.env.example` contra o código que lê a variável.
  Os dois são documentação **desatualizada**: pendência (4.3) **não bloqueante**.
- Documentação **ausente ou incompleta** é outra coisa e **bloqueia**. Registre o estado de cada item obrigatório da 4.3 **antes** desta varredura e **depois** dela:

  | Item obrigatório | Incompleto quando |
  |---|---|
  | `README.md` | falta o que o projeto faz, como rodar localmente ou como rodar os testes |
  | `docs/architecture/c4-context.md` e `c4-containers.md` | ausente, sem diagrama, ou o diagrama não renderiza |
  | `docs/systems/<repo>.md` e `docs/SYSTEMS_CATALOG.md` | ausente ou com seção obrigatória do template vazia sem justificativa |
  | Variáveis de ambiente e segredos | alguma variável lida no código não está documentada por nome |

  Esta skill gera o relatório e o catálogo, então eles saem como "ausente antes desta varredura; gerado". A pendência bloqueante só fica para o que continuar ausente ou incompleto ao final: o C4 é outra skill (registre e sugira `/c4-architecture`), o README é do dev. `c4-components` e `c4-deployment` são opcionais e nunca bloqueiam.
  Variável documentada que o código não lê, ou `.env.example` com valor real, é desatualização: não bloqueante.
- Os diagramas C4 ficam em `docs/architecture/`. Aqui entra só o diagrama de contêineres resumido do template, com a convenção de rótulos do C4 (nome e tecnologia no nó; ação e protocolo na seta).

### 4. Escrita

**MANDATORY**: leia [templates/system-report.md](templates/system-report.md) e preencha-o em `docs/systems/<nome-do-repositorio>.md`. Monorepo gera **um** relatório com uma subseção por parte onde o template indica; não um arquivo por pasta.

**MANDATORY**: leia [templates/systems-catalog.md](templates/systems-catalog.md) e crie ou atualize `docs/SYSTEMS_CATALOG.md`. Se ele já existir com outras linhas, atualize só a linha deste repositório.

Pendências: cada item "pendente" da seção 4 e cada CVE (qualquer severidade) vira uma linha na seção de pendências, escrita como título de issue (verbo no imperativo, arquivo, o que fazer). Coluna "Bloqueia?" = **sim** só para: CVE alta/crítica (ou "a confirmar"); uso real de outro provedor; segredo commitado (código ou histórico); parte sem Dockerfile; segredo com valor padrão inseguro no código (ex.: `os.environ.get("SECRET_KEY", "dev-...")`, que deixa a aplicação subir em produção com uma chave conhecida); documentação obrigatória da 4.3 ausente ou incompleta ao final da varredura (passo 3). Todo o resto: **não**, inclusive documentação desatualizada. Bloqueantes e não bloqueantes viram issue; a infra copia as linhas para o seu repositório.

Revise o texto: frases curtas, sem adjetivo de propaganda, sem "robusto"/"escalável"/"moderno" sem número. Não reescreva tabelas nem valores do veredito nessa revisão.

### 5. Conferência final

Antes de entregar, confirme:

- [ ] Toda linha "atendido" tem `arquivo:linha` que abre de verdade (confira dois ou três links).
- [ ] Toda variável lida no código está na tabela, e nenhuma tem valor. Variável lida e não documentada fora deste relatório (`.env.example`/README) = bloqueante de documentação.
- [ ] A detecção de outro provedor e de `suape-brand` foi feita e o resultado está escrito, mesmo que negativo.
- [ ] Cada "não verificado" diz o motivo e o que o dev pode rodar para fechar.
- [ ] Nenhum `file:///`, `/home/`, `C:\` no texto gerado: `grep -nE 'file:///|/home/|[A-Z]:\\' docs/systems docs/SYSTEMS_CATALOG.md`.
- [ ] Os blocos Mermaid usam só sintaxe suportada pelo GitHub.
- [ ] O veredito do resumo conta como bloqueante só os seis casos do passo 4.
- [ ] A tabela de documentação obrigatória mostra o estado antes e depois, e só o que continuou ausente ou incompleto bloqueia. Branch `dev`/`hml` existente nunca entra.
- [ ] Data do catálogo = data de hoje, com o hash do commit analisado ao lado.

Ao terminar, diga ao dev quantas pendências existem e que ele responde pela documentação: deve revisar antes de abrir o chamado. Se houver pendências, o chamado vai voltar com issues; vale corrigir primeiro.

## Skills de apoio: essenciais e consultivas

Carregar todas estoura o contexto. "Essencial" quer dizer que a **verificação** é obrigatória, não que a skill inteira precise ser carregada: execute as buscas e ferramentas desta skill e de [references/gcp-readiness-checks.md](references/gcp-readiness-checks.md) e abra a skill de apoio só se precisar de um padrão que não está aqui.

| Tipo | Skill | Quando |
|---|---|---|
| Essencial | `scanning-for-hardcoded-secrets` | Sempre, no passo 2.8. Segredo vazado bloqueia. |
| Essencial | `auditing-python-dependencies` ou `auditing-npm-dependencies` | Sempre, conforme o manifesto. Só a do ecossistema presente. |
| Consultiva | `detecting-sql-injection-patterns` | Só se houver SQL escrito à mão (`execute(`, `text(`, `raw(`). |
| Consultiva | `database-schema-designer` | Só se houver models ou migrations e você precisar avaliar migration destrutiva. |
| Consultiva | `api-contract-review` | Só se houver cliente externo da API (app mobile, outro sistema). |
| Consultiva | `intended-vs-implemented`, `shipping-artifacts` | Só se a divergência README × código for grande demais para o passo 3. |
| Consultiva | `checking-http-security-headers`, `mermaid-diagrams`, `c4-architecture` | Só para tirar dúvida de sintaxe ou de header específico. |
| Consultiva | `humanizer`, `writing-clearly-and-concisely` | Só se o texto final sair com cara de propaganda. |

Skill consultiva que você não carregou não precisa ser citada no relatório. Verificação essencial que não rodou vira linha em "Não verificado".

## Arquivos desta skill

| Arquivo | Quando carregar |
|---|---|
| [references/gcp-readiness-checks.md](references/gcp-readiness-checks.md) | Sempre, no passo 2. |
| [references/subagent-brief.md](references/subagent-brief.md) | Só se for delegar a subagentes. Do NOT load em repositório de uma parte só. |
| [templates/system-report.md](templates/system-report.md) | Sempre, no passo 4. |
| [templates/systems-catalog.md](templates/systems-catalog.md) | Sempre, no passo 4. Do NOT load antes de terminar a varredura. |
