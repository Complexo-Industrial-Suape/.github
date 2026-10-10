# Cartilha de Desenvolvimento de Suape: do zero ao deploy

Coordenadoria de Tecnologia da Informação e Comunicação (CTIC) · versão 2.3 · outubro de 2026

Para todos os desenvolvedores da Coordenadoria de Inovação. Vale para os projetos da org [Complexo-Industrial-Suape](https://github.com/Complexo-Industrial-Suape) que rodam no Google Cloud.

---

## 1. Quem faz o quê

Cada um cuida do que é seu.

| Você, desenvolvedor | O responsável pela infraestrutura (Raul César) |
|---|---|
| Cria o repositório na org | É owner da org do GitHub e administra o GCP e o AGY |
| Desenvolve o MVP e as regras de negócio | Avalia o pedido e confere a documentação |
| Documenta o projeto (C4 + Scan Systems) | Cria os três ambientes e as branches `dev` e `hml` |
| Deixa o projeto dockerizado e com testes | Configura o deploy automático (Cloud Build) |
| Controla branches, PRs e o fluxo de promoção | Combina com você CI, ciclos, rotinas e cron jobs |
| Corrige o que for apontado nas issues | Devolve um resumo do que foi feito |

**O responsável pela infraestrutura não mexe em regra de negócio.** Ele não é o desenvolvedor do projeto. Se algo no código impedir o deploy, ele abre uma issue no seu repositório e você corrige.

Para trabalhar aqui, você precisa saber o básico de Git e GitHub: branch, commit, PR, merge e resolução de conflito. Também precisa pensar desde o início em como seu projeto se comporta com mais usuários (escalabilidade) e quanto ele custa para rodar.

---

## 2. O caminho de um projeto novo

```
1. Você cria o repositório e desenvolve o MVP
2. Você documenta (C4 + Scan Systems) e sobe tudo para o GitHub
3. Você abre o chamado por e-mail
4. A infraestrutura confirma, confere a documentação e inspeciona o projeto
     └─ faltou algo? → issues no seu repositório + resposta no e-mail → você corrige → volta ao passo 4
5. A infraestrutura cria os ambientes, as branches e o deploy automático
6. Vocês alinham CI, ciclos, rotinas e cron jobs
7. Você recebe o resumo do que foi feito e passa a trabalhar no fluxo normal
```

> **Projeto sem documentação não recebe ambiente no GCP.** Não há exceção. Isso reduz custo e retrabalho para todos.

---

## 3. Antes de pedir ambiente: checklist do repositório

Confira cada item. O pedido só segue quando todos estiverem atendidos.

### 3.1 Repositório

- [ ] Está na org **Complexo-Industrial-Suape**, não na sua conta pessoal.
- [ ] **Repositório próprio:** todo desenvolvedor da Coordenadoria pode criar repositórios na org.
- [ ] Nome em **kebab-case**: só letras minúsculas, números e hífen, sem `_`, `.` ou maiúsculas. Formato `<produto>[-api|-web|-mobile]`. Exemplos: `rdo-suape-api`, `suape-drive`, `premio-inova-industria-web`. "Suape" fica no nome quando faz parte do produto.
- [ ] O código do MVP está na branch `main`. Você não precisa criar `dev` nem `hml`: elas são criadas no provisionamento. Se o projeto já tem essas branches, tudo bem: elas são aproveitadas e ligadas aos ambientes.
- [ ] Nenhum segredo commitado: senha, token, chave de API, `.env` com valores reais ou chave de service account. Deixe só um `.env.example` com os nomes das variáveis, sem os valores.
- [ ] **Marca Suape:** os assets que o projeto usa (logos, fontes, cores) ficam copiados numa pasta do próprio projeto, por exemplo `web/public/brand/`. Se você clonar o `suape-brand` dentro do repositório para consultar o kit, **coloque a pasta `suape-brand/` no `.gitignore`**. Nunca commite o kit inteiro e nunca use o `suape-brand` como submódulo git.

### 3.2 Pronto para o GCP

- [ ] **Dockerizado:** cada parte publicável (API, frontend, job) tem um `Dockerfile` que funciona com `docker build .`.
- [ ] **Monorepo** (frontend e backend no mesmo repositório): organize nesta estrutura. Vale mesmo quando o projeto roda num único container (por exemplo, o backend servindo o frontend já compilado): nesse caso, um só `Dockerfile` copia as duas pastas para dentro da imagem.
  ```
  meu-projeto/
  ├── web/     frontend (Dockerfile próprio)
  ├── api/     backend (Dockerfile próprio)
  ├── docs/    documentação (C4 + Scan Systems)
  └── infra/   só se precisar (Terraform, scripts de infraestrutura)
  ```
- [ ] A aplicação escuta na porta definida pela variável `PORT` (padrão do Cloud Run: 8080).
- [ ] Toda configuração vem de **variáveis de ambiente**, sem nada fixo no código: URLs, credenciais, nomes de bucket.
- [ ] A API tem um endpoint de saúde que responde 200: `/health`, ou o par `/livez` e `/readyz`. Não use `/healthz`: o Cloud Run não repassa esse caminho para o container.
- [ ] **Sem dependência de outro provedor de nuvem.** Se o projeto foi gerado ou desenhado para Cloudflare, Vercel, AWS, Supabase, Firebase ou outra plataforma, isso precisa ser adaptado antes. Exemplos comuns: `wrangler`, D1, R2, Vercel Functions, Lambda, S3. Ferramentas de IA e geradores de projeto costumam trazer isso escondido; confira o `package.json`, os arquivos de configuração e o README.
- [ ] Testes automatizados que rodam com um comando (`pytest`, `npm run test`).
- [ ] **Sem vulnerabilidade alta ou crítica nas dependências.** Rode `pip-audit` (ou `uv run --with pip-audit pip-audit`) e `npm audit --omit=dev`. Vulnerabilidade alta ou crítica **bloqueia o provisionamento** e vira issue no repositório até ser corrigida.

### 3.3 Documentação

A documentação segue dois modelos: **C4 model** (skill `/c4-architecture`) e **Scan Systems** (skill `/scan-systems`). As duas skills são públicas: veja [skills de documentação](https://github.com/Complexo-Industrial-Suape/.github/tree/main/skills), com instruções de instalação para o AGY e o Claude Code.

| Arquivo | Conteúdo | Obrigatório |
|---|---|---|
| `README.md` | O que o projeto faz, como rodar localmente em menos de 5 minutos, como rodar os testes | Sim |
| `docs/architecture/c4-context.md` | **C4 nível 1:** o sistema, quem usa e com quais sistemas externos ele conversa | Sim |
| `docs/architecture/c4-containers.md` | **C4 nível 2:** API, frontend, banco, filas e jobs, com a tecnologia de cada um e como se comunicam | Sim |
| `docs/architecture/c4-components-<parte>.md` | **C4 nível 3:** componentes internos, só para as partes complexas | Quando ajudar |
| `docs/architecture/c4-deployment.md` | Como o projeto deve rodar em produção (o que você espera do GCP) | Recomendado |
| `docs/systems/<nome-do-projeto>.md` | **Relatório do Scan Systems:** stack, modelos de dados, rotas da API, variáveis de ambiente e segredos (só os nomes), fluxos de acesso, testes e postura de segurança | Sim |
| `docs/SYSTEMS_CATALOG.md` | Catálogo consolidado do Scan Systems | Sim |

Regras da documentação:
- Os diagramas usam Mermaid e precisam renderizar no GitHub.
- Todo elemento do diagrama tem nome, tecnologia e descrição. Toda seta diz o que faz e por qual protocolo, por exemplo "Consulta reservas via HTTPS/JSON". Rótulos vagos como "usa" não servem.
- Nada inventado: cada afirmação aponta para um arquivo real do repositório, com link relativo. Não use caminhos da sua máquina (`C:\Users\...`, `/home/...`).
- Liste **todas** as variáveis de ambiente e segredos que o projeto precisa, **só com os nomes**. É a partir dessa lista que os segredos são criados no GCP.

**Documentação ausente ou incompleta bloqueia o provisionamento.** Faltar qualquer arquivo obrigatório da tabela acima, uma seção dele (por exemplo, o README sem como rodar os testes) ou alguma variável de ambiente lida pelo código é motivo para o pedido não seguir. Documentação desatualizada vira issue, mas não bloqueia.

**Dica:** no AGY ou no Claude Code, peça "rode /scan-systems neste repositório" e depois "/c4-architecture". Revise o que for gerado. Você responde pela documentação, não a ferramenta.

---

## 4. Como abrir o chamado de provisionamento

**1. Mande um e-mail**
- **Para:** raulsilva@suape.pe.gov.br
- **Assunto:** `Provisionamento de ambiente GCP - <nome-do-repositório>`. Exemplo: `Provisionamento de ambiente GCP - rdo-suape-api`

**2. Aguarde a confirmação por e-mail.** Se precisar de um contato mais rápido, peça na própria mensagem.

### Modelo do e-mail

Copie, preencha e envie:

```text
Assunto: Provisionamento de ambiente GCP - <nome-do-repositório>

1. Projeto
   - Repositório: https://github.com/Complexo-Industrial-Suape/<repo>
   - Responsável (nome e contato):
   - Área/cliente demandante:
   - O que o sistema faz (2 a 3 frases):

2. Público e uso
   - Quem usa: ( ) só servidores de Suape  ( ) público externo  ( ) os dois
   - Usuários esperados (número aproximado):
   - Precisa de login? Qual (Google institucional, usuário e senha, outro)?

3. Disponibilidade
   - Horário de uso: ( ) só horário comercial  ( ) 24x7
   - Precisa estar no ar fora do horário comercial? Por quê?
   - Pode ter alguns segundos de lentidão no primeiro acesso do dia (cold start)? ( ) sim  ( ) não
   - Impacto se ficar fora do ar por 1 hora:

4. Técnica
   - Partes publicáveis (API, frontend, job...) e a pasta de cada uma:
   - Banco de dados: ( ) nenhum  ( ) PostgreSQL  ( ) MongoDB  ( ) outro:
   - Volume de dados estimado:
   - Armazenamento de arquivos (fotos, PDFs, uploads)? Volume estimado:
   - Integrações externas (APIs de terceiros, Google Drive, Gemini, e-mail, SMS):
   - Tarefas agendadas (cron) e frequência:
   - Variáveis de ambiente e segredos: ver docs/systems/<projeto>.md

5. Prazos
   - Data desejada para hml:
   - Data desejada para produção:

6. Checklist (seção 3 da cartilha)
   ( ) Repositório na org, nome no padrão, sem segredos commitados
   ( ) Dockerizado, configuração por variáveis de ambiente, endpoint de saúde
   ( ) Sem vulnerabilidade alta ou crítica nas dependências
   ( ) Sem dependência de outro provedor de nuvem
   ( ) Documentação C4 e Scan Systems no repositório
```

As seções 2 e 3 do e-mail definem quanto o projeto custa e como ele é configurado. Um sistema interno usado em horário comercial pode desligar quando ninguém usa e custa quase nada. Um sistema público 24x7 precisa de instância sempre ligada. Responda com sinceridade: superdimensionar custa dinheiro público.

---

## 5. O que acontece depois do chamado

1. **Confirmação:** você recebe a resposta de que o pedido foi recebido.
2. **Inspeção:** o repositório e a documentação são conferidos.
3. **Pendências viram issues:** se algo impedir o provisionamento, você recebe **issues no seu repositório** e um resumo na resposta do e-mail. Exemplos: projeto não dockerizado, dependência de outro provedor, documentação incompleta, segredo commitado. Corrija, responda o mesmo e-mail e a inspeção recomeça.
4. **Provisionamento:** a infraestrutura cria:
   - os ambientes **dev**, **hml** e **prod** no GCP, dimensionados conforme o chamado;
   - as branches **`dev`** e **`hml`** a partir da `main` (se já existirem, são aproveitadas);
   - os segredos no Secret Manager (os valores são combinados com você por canal seguro, nunca por e-mail);
   - o deploy automático pelo **Cloud Build** (`cloudbuild.yaml`).
5. **Alinhamento:** vocês combinam juntos o CI (quais testes rodam antes do deploy), os ciclos de entrega, as rotinas e os cron jobs.
6. **Resumo:** você recebe um resumo do que foi configurado: URLs de cada ambiente, gatilhos, segredos (só os nomes) e como acompanhar os deploys.

O `cloudbuild.yaml` é infraestrutura: quem altera é o responsável pela infraestrutura. Precisa mudar algo no pipeline? Peça por e-mail.

---

## 6. Depois do provisionamento: o dia a dia

### Cada branch publica no seu ambiente

| Você faz push ou merge em | Publica em |
|---|---|
| `dev` | **dev** |
| `hml` | **hml** (homologação) |
| `main` | **prod** (produção) |

Não existe botão de deploy. **Entrou na branch, vai para o ar.**

### Fluxo de trabalho

```
feature/minha-tarefa ──PR──▶ dev ──PR──▶ hml ──PR──▶ main
                              │           │           │
                         publica em   publica em  publica em
                            dev          hml         PROD
```

1. Crie sua branch a partir de `dev`: `git checkout dev && git pull && git checkout -b feature/descricao`.
2. Rode os testes na sua máquina antes de abrir o PR.
3. PR para `dev` → merge → deploy automático em dev.
4. Pronto para validar: PR de `dev` para `hml`.
5. Validado: PR de `hml` para `main`. Esse merge publica em **produção**.

| Prefixo de branch | Use para |
|---|---|
| `feature/` | funcionalidade nova |
| `fix/` | correção pelo fluxo normal |
| `hotfix/` | correção urgente de produção |
| `docs/` | só documentação |

### Regras

1. **Não faça push direto em `main`.** Ela publica em produção na hora. A proteção automática ainda não está ativa no GitHub, então a regra depende de você.
2. **Não pule ambiente:** sempre `dev → hml → main`.
3. **Teste antes de subir.** O pipeline roda os testes antes de publicar. Se falhar, nada é publicado e o ambiente fica na versão anterior.
4. **Segredos só no Secret Manager.** Precisa de um novo? Peça por e-mail.
5. **Não faça deploy por fora** (`gcloud run deploy` manual, upload pelo console). O próximo push sobrescreve e o histórico se perde.
6. **Migrations andam com o código** e rodam antes do deploy. Teste localmente e nunca edite uma migration já aplicada em hml ou prod.
7. **Mantenha a documentação viva.** Mudou a arquitetura, entrou um banco novo ou um serviço externo? Atualize o C4 e o relatório do Scan Systems no mesmo PR.

### Acompanhar o deploy

1. Abra o [Histórico do Cloud Build](https://console.cloud.google.com/cloud-build/builds;region=southamerica-east1?project=inovacao-491419).
2. Procure o build `<projeto>-<ambiente>`, por exemplo `suape-drive-dev`. Ele aparece segundos depois do merge e leva de 3 a 10 minutos.
3. Verde: no ar. Vermelho: abra o passo que falhou e leia o erro. O status também aparece ao lado do commit no GitHub.

### Quando o deploy falha

| Onde falhou | O que fazer |
|---|---|
| Testes (`test`, `pre-flight`, `lint-and-test`) | Rode os testes localmente, corrija e faça novo push |
| `docker build` | Rode `docker build .` localmente |
| Migration | Não tente de novo às cegas: avise a infraestrutura. Migration com erro pode deixar o banco pela metade |
| `PERMISSION_DENIED` ou `secret not found` | Problema de infraestrutura: mande o link do build por e-mail |
| Teste final (`smoke`) | O serviço subiu e não respondeu: veja os logs no Cloud Run |

### Situações especiais

- **Só documentação:** mudanças apenas em `docs/` ou `.md` não disparam deploy.
- **Hotfix:** branch a partir de `main` → PR para `main`. Depois, **leve a correção de volta** com PR de `main` para `hml` e de `hml` para `dev`. Se esquecer, o próximo deploy apaga a correção.
- **Rollback:** no [Cloud Run](https://console.cloud.google.com/run?project=inovacao-491419), abra o serviço → **Revisões** → revisão anterior → **Gerenciar tráfego** → 100%. É temporário: corrija o código ou use `git revert` e siga o fluxo.
- **Variáveis de frontend (`VITE_*`, `NEXT_PUBLIC_*`)** entram no código durante o build. Mudar o valor exige novo deploy; peça por e-mail.

---

## 7. Contato

| Assunto | Como |
|---|---|
| Ambiente novo no GCP | E-mail para raulsilva@suape.pe.gov.br com o assunto `Provisionamento de ambiente GCP - <repositório>` |
| Deploy que falhou, segredos, permissões, mudança no pipeline | E-mail para raulsilva@suape.pe.gov.br com o link do build |
| Acesso ao GitHub ou ao AGY | E-mail para raulsilva@suape.pe.gov.br |
| Regra de negócio do projeto | Com o desenvolvedor responsável pelo projeto |

---

## Consulta rápida

- **Nome do repo:** kebab-case (`meu-projeto-api`)
- **Projeto novo:** cria o repo → MVP → documenta (C4 + Scan Systems) → e-mail `Provisionamento de ambiente GCP - <repositório>`
- **Sem documentação, sem ambiente.**
- **Antes do chamado:** dockerizado · configuração por variável de ambiente · endpoint de saúde · sem outro provedor de nuvem · sem segredo commitado · sem vulnerabilidade alta
- **Branches:** `dev` → dev · `hml` → hml · `main` → **produção**
- **Fluxo:** `feature/*` → `dev` → `hml` → `main`, sempre por PR
- **Nunca:** push direto em `main` · segredo no código · deploy manual · editar o `cloudbuild.yaml`
- **Falhou?** O ambiente continua na versão anterior. Leia o log, corrija, faça novo push.
