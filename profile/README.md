# Cartilha de Desenvolvimento de Suape: do zero ao deploy

Coordenadoria de Tecnologia da Informação e Comunicação (CTIC) · versão 2.4 · outubro de 2026

Esta cartilha é para quem desenvolve na Coordenadoria de Inovação. Ela vale para todo projeto da org [Complexo-Industrial-Suape](https://github.com/Complexo-Industrial-Suape) que vai rodar no Google Cloud.

A ideia é simples: o desenvolvedor cuida do projeto, a infraestrutura cuida do ambiente, e os dois seguem o mesmo padrão. Isso reduz custo, retrabalho e surpresa na hora do deploy.

---

## 1. Quem faz o quê

| Você, desenvolvedor | Responsável pela infraestrutura (Raul César) |
|---|---|
| Cria o repositório na org | Administra a org do GitHub, o GCP e o AGY |
| Desenvolve o MVP e as regras de negócio | Avalia o pedido e confere a documentação |
| Documenta o projeto (C4 + Scan Systems) | Cria os três ambientes e as branches `dev` e `hml` |
| Deixa o projeto dockerizado e com testes | Configura o deploy automático (Cloud Build) |
| Controla branches, PRs e a promoção entre ambientes | Combina com você CI, ciclos, rotinas e cron jobs |
| Corrige o que for apontado nas issues | Devolve um resumo do que foi feito |

A infraestrutura não mexe em regra de negócio. Se algo no código impedir o deploy, você recebe uma issue no repositório e faz a correção.

Para trabalhar aqui, você precisa dominar o básico de Git e GitHub: branch, commit, PR, merge e resolução de conflito. E precisa pensar desde o início em duas coisas: como o projeto se comporta com mais usuários e quanto custa mantê-lo no ar.

---

## 2. Stack padrão

Projetos novos usam esta stack:

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.14 com Flask, FastAPI ou Django |
| Frontend | React com Vite |

Com todo mundo na mesma base, fica mais fácil revisar o código, reaproveitar soluções e manter tudo atualizado e seguro. O pipeline de deploy, os testes e as auditorias de dependência já estão prontos para essa stack.

Qual framework de backend usar depende do projeto:

| Use | Quando |
|---|---|
| FastAPI | API REST pura, com validação de dados e documentação automática (OpenAPI) |
| Django | Sistema com muitos cadastros, painel administrativo e regras de permissão |
| Flask | Serviço pequeno, ou o backend que também entrega o frontend compilado |

Precisa de outra tecnologia? Explique o motivo no e-mail do chamado (seção 5).

---

## 3. O caminho de um projeto novo

```
1. Você cria o repositório e desenvolve o MVP
2. Você documenta (C4 + Scan Systems) e sobe tudo para o GitHub
3. Você abre o chamado por e-mail
4. A infraestrutura confirma, confere a documentação e inspeciona o projeto
     └─ faltou algo? → issues no repositório + resposta no e-mail → você corrige → volta ao passo 4
5. A infraestrutura cria os ambientes, as branches e o deploy automático
6. Vocês alinham CI, ciclos, rotinas e cron jobs
7. Você recebe o resumo e passa a trabalhar no fluxo normal
```

> **Projeto sem documentação não recebe ambiente no GCP.** Não há exceção.

---

## 4. Antes de pedir ambiente: checklist do repositório

O pedido só segue quando todos os itens estiverem atendidos.

### 4.1 Repositório

- [ ] Está na org Complexo-Industrial-Suape, e não na sua conta pessoal. Todo desenvolvedor da Coordenadoria pode criar repositórios lá.
- [ ] O nome está em kebab-case: letras minúsculas, números e hífen, sem `_`, `.` ou maiúsculas. O formato é `<produto>[-api|-web|-mobile]`, como `rdo-suape-api`, `suape-drive` ou `premio-inova-industria-web`. "Suape" entra no nome quando faz parte do produto.
- [ ] O código do MVP está na `main`. Não precisa criar `dev` nem `hml`, porque elas são criadas no provisionamento. Se já existirem, serão aproveitadas.
- [ ] Nenhum segredo foi commitado: senha, token, chave de API, `.env` com valores reais ou chave de service account. No repositório fica só o `.env.example`, com os nomes das variáveis e sem valores.
- [ ] Os assets da marca Suape que o projeto usa (logos, fontes, cores) estão copiados numa pasta do próprio projeto, como `web/public/brand/`. Se você clonar o `suape-brand` dentro do repositório para consultar o kit, ponha a pasta `suape-brand/` no `.gitignore`. Nunca commite o kit inteiro e nunca use o `suape-brand` como submódulo.

### 4.2 Pronto para o GCP

- [ ] O projeto usa a stack padrão (seção 2) ou tem a exceção justificada no chamado.
- [ ] Cada parte publicável (API, frontend, job) tem um `Dockerfile` que funciona com `docker build .`.
- [ ] Se frontend e backend estão no mesmo repositório, a estrutura é esta, mesmo que o projeto rode num único container. Nesse caso, um só `Dockerfile` copia as duas pastas para dentro da imagem.
  ```
  meu-projeto/
  ├── web/     frontend React/Vite
  ├── api/     backend Python
  ├── docs/    documentação (C4 + Scan Systems)
  └── infra/   só se precisar (Terraform, scripts)
  ```
- [ ] A aplicação escuta na porta da variável `PORT`. O Cloud Run usa 8080 por padrão.
- [ ] Toda configuração vem de variáveis de ambiente. URL, credencial e nome de bucket não ficam fixos no código.
- [ ] A API tem um endpoint de saúde que responde 200: `/health`, ou o par `/livez` e `/readyz`. Evite `/healthz`, porque o Cloud Run não repassa esse caminho para o container.
- [ ] O projeto não depende de outro provedor de nuvem. Projetos gerados por ferramentas de IA ou por templates costumam trazer Cloudflare, Vercel, AWS, Supabase ou Firebase escondidos (`wrangler`, D1, R2, Vercel Functions, Lambda, S3). Confira o `package.json`, os arquivos de configuração e o README antes de abrir o chamado.
- [ ] Os testes automatizados rodam com um comando (`pytest`, `npm run test`).
- [ ] Não há vulnerabilidade alta ou crítica nas dependências. Rode `pip-audit` (ou `uv run --with pip-audit pip-audit`) e `npm audit --omit=dev`. Vulnerabilidade alta ou crítica bloqueia o provisionamento e vira issue até ser corrigida.

### 4.3 Documentação

A documentação segue o C4 model (skill `/c4-architecture`) e o Scan Systems (skill `/scan-systems`). As duas skills estão [publicadas aqui](https://github.com/Complexo-Industrial-Suape/.github/tree/main/skills), com instruções de instalação para o AGY e o Claude Code.

| Arquivo | Conteúdo | Obrigatório |
|---|---|---|
| `README.md` | O que o projeto faz, como rodar localmente em menos de 5 minutos e como rodar os testes | Sim |
| `docs/architecture/c4-context.md` | C4 nível 1: o sistema, quem usa e com quais sistemas externos ele conversa | Sim |
| `docs/architecture/c4-containers.md` | C4 nível 2: API, frontend, banco, filas e jobs, com a tecnologia de cada um e como se comunicam | Sim |
| `docs/architecture/c4-components-<parte>.md` | C4 nível 3: componentes internos, só para as partes complexas | Quando ajudar |
| `docs/architecture/c4-deployment.md` | Como o projeto deve rodar em produção, ou seja, o que você espera do GCP | Recomendado |
| `docs/systems/<nome-do-projeto>.md` | Relatório do Scan Systems: stack, modelos de dados, rotas da API, variáveis de ambiente e segredos (só os nomes), fluxos de acesso, testes e segurança | Sim |
| `docs/SYSTEMS_CATALOG.md` | Catálogo consolidado do Scan Systems | Sim |

Algumas regras:
- Os diagramas usam Mermaid e precisam renderizar no GitHub.
- Todo elemento do diagrama tem nome, tecnologia e descrição. Toda seta diz o que faz e por qual protocolo, como "Consulta reservas via HTTPS/JSON". Rótulo genérico como "usa" não serve.
- Nada inventado. Cada afirmação aponta para um arquivo real do repositório, com link relativo, e nunca para um caminho da sua máquina (`C:\Users\...`, `/home/...`).
- Liste todas as variáveis de ambiente e segredos que o projeto usa, só com os nomes. Os segredos do GCP são criados a partir dessa lista.

**Documentação ausente ou incompleta bloqueia o provisionamento.** Isso vale para um arquivo obrigatório que falta, uma seção que falta (o README sem como rodar os testes, por exemplo) e uma variável que o código lê e a documentação não cita. Documentação desatualizada vira issue, mas não bloqueia.

No AGY ou no Claude Code, peça "rode /scan-systems neste repositório" e depois "/c4-architecture". Revise o resultado antes de commitar: quem responde pela documentação é você, não a ferramenta.

---

## 5. Como abrir o chamado de provisionamento

Mande um e-mail para **raulsilva@suape.pe.gov.br** com o assunto `Provisionamento de ambiente GCP - <nome-do-repositório>`. Exemplo: `Provisionamento de ambiente GCP - rdo-suape-api`.

A confirmação chega por e-mail. Se precisar de um contato mais rápido, peça na própria mensagem.

### Modelo do e-mail

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
   - Aceita alguns segundos de lentidão no primeiro acesso do dia (cold start)? ( ) sim  ( ) não
   - Impacto se ficar fora do ar por 1 hora:

4. Técnica
   - Stack: ( ) padrão (Python 3.14 + Flask/FastAPI/Django, React/Vite)  ( ) outra, justificativa:
   - Partes publicáveis (API, frontend, job) e a pasta de cada uma:
   - Banco de dados: ( ) nenhum  ( ) PostgreSQL  ( ) MongoDB  ( ) outro:
   - Volume de dados estimado:
   - Armazenamento de arquivos (fotos, PDFs, uploads)? Volume estimado:
   - Integrações externas (APIs de terceiros, Google Drive, Gemini, e-mail, SMS):
   - Tarefas agendadas (cron) e frequência:
   - Variáveis de ambiente e segredos: ver docs/systems/<projeto>.md

5. Prazos
   - Data desejada para hml:
   - Data desejada para produção:

6. Checklist (seção 4 da cartilha)
   ( ) Repositório na org, nome no padrão, sem segredos commitados
   ( ) Stack padrão ou exceção justificada
   ( ) Dockerizado, configuração por variáveis de ambiente, endpoint de saúde
   ( ) Sem vulnerabilidade alta ou crítica nas dependências
   ( ) Sem dependência de outro provedor de nuvem
   ( ) Documentação C4 e Scan Systems no repositório
```

As seções 2 e 3 do e-mail decidem quanto o projeto vai custar. Um sistema interno usado só em horário comercial pode desligar quando ninguém está usando e sai quase de graça. Um sistema público 24x7 precisa de instância ligada o tempo todo. Responda com sinceridade, porque superdimensionar custa dinheiro público.

---

## 6. Depois do chamado

1. Você recebe a confirmação de que o pedido chegou.
2. O repositório e a documentação são inspecionados.
3. Se algo impedir o provisionamento, você recebe issues no repositório e um resumo na resposta do e-mail. Os casos mais comuns são projeto sem Dockerfile, dependência de outro provedor, documentação incompleta e segredo commitado. Corrija e responda o mesmo e-mail, que a inspeção recomeça.
4. Com tudo certo, a infraestrutura cria:
   - os ambientes dev, hml e prod no GCP, dimensionados conforme o chamado;
   - as branches `dev` e `hml` a partir da `main`, ou aproveita as que já existem;
   - os segredos no Secret Manager, com valores combinados com você por canal seguro (nunca por e-mail);
   - o deploy automático pelo Cloud Build (`cloudbuild.yaml`).
5. Vocês combinam o CI (quais testes rodam antes do deploy), os ciclos de entrega, as rotinas e os cron jobs.
6. Você recebe um resumo com a URL de cada ambiente, os gatilhos de deploy, os nomes dos segredos e onde acompanhar os builds.

O `cloudbuild.yaml` é infraestrutura, e só o responsável pela infraestrutura altera esse arquivo. Precisa mudar algo no pipeline? Peça por e-mail.

---

## 7. O dia a dia depois do provisionamento

### Cada branch publica no seu ambiente

| Push ou merge em | Publica em |
|---|---|
| `dev` | dev |
| `hml` | hml (homologação) |
| `main` | **prod (produção)** |

Não existe botão de deploy. Entrou na branch, vai para o ar.

### Fluxo de trabalho

```
feature/minha-tarefa ──PR──▶ dev ──PR──▶ hml ──PR──▶ main
                              │           │           │
                         publica em   publica em  publica em
                            dev          hml         PROD
```

1. Crie sua branch a partir de `dev`: `git checkout dev && git pull && git checkout -b feature/descricao`.
2. Rode os testes na sua máquina antes de abrir o PR.
3. Abra PR para `dev`. O merge publica em dev.
4. Quando estiver pronto para validar, abra PR de `dev` para `hml`.
5. Depois da validação, abra PR de `hml` para `main`. Esse merge publica em produção.

| Prefixo de branch | Uso |
|---|---|
| `feature/` | funcionalidade nova |
| `fix/` | correção pelo fluxo normal |
| `hotfix/` | correção urgente de produção |
| `docs/` | só documentação |

### Regras

1. Não faça push direto em `main`. Ela publica em produção na hora, e a proteção automática ainda não está ativa no GitHub. Por enquanto, essa regra depende de você.
2. Não pule ambiente. O caminho é sempre `dev → hml → main`.
3. Rode os testes antes de subir. O pipeline também roda: se falharem, nada é publicado e o ambiente continua na versão anterior.
4. Segredo fica no Secret Manager. Precisa de um novo? Peça por e-mail.
5. Não faça deploy por fora, com `gcloud run deploy` manual ou upload pelo console. O próximo push sobrescreve o que você fez, e o histórico se perde.
6. Migrations andam junto com o código e rodam antes do deploy. Teste localmente e nunca edite uma migration já aplicada em hml ou prod.
7. Atualize a documentação no mesmo PR quando a arquitetura mudar, entrar um banco novo ou um serviço externo.

### Acompanhar o deploy

Abra o [histórico do Cloud Build](https://console.cloud.google.com/cloud-build/builds;region=southamerica-east1?project=inovacao-491419) e procure o build `<projeto>-<ambiente>`, como `suape-drive-dev`. Ele aparece segundos depois do merge e leva de 3 a 10 minutos. Verde quer dizer que a versão está no ar. Vermelho quer dizer que algo falhou: abra o passo com erro e leia o log. O status também aparece ao lado do commit no GitHub.

### Quando o deploy falha

| Onde falhou | O que fazer |
|---|---|
| Testes (`test`, `pre-flight`, `lint-and-test`) | Rode os testes localmente, corrija e faça novo push |
| `docker build` | Rode `docker build .` localmente |
| Migration | Não tente de novo às cegas. Avise a infraestrutura, porque uma migration com erro pode deixar o banco pela metade |
| `PERMISSION_DENIED` ou `secret not found` | É problema de infraestrutura. Mande o link do build por e-mail |
| Teste final (`smoke`) | O serviço subiu mas não respondeu. Veja os logs no Cloud Run |

### Situações especiais

Commit que mexe só em `docs/` ou em arquivos `.md` não dispara deploy.

Para um hotfix, crie a branch a partir de `main` e abra PR para `main`. Depois, leve a correção de volta com PR de `main` para `hml` e de `hml` para `dev`. Se esquecer, o próximo deploy apaga a correção.

Para voltar uma versão, abra o serviço no [Cloud Run](https://console.cloud.google.com/run?project=inovacao-491419), vá em Revisões, escolha a anterior e mande 100% do tráfego para ela. Isso resolve na hora, mas é temporário: corrija o código ou use `git revert` e siga o fluxo normal.

Variáveis de frontend (`VITE_*`) entram no código durante o build. Para mudar o valor, é preciso um novo deploy. Peça por e-mail.

---

## 8. Contato

| Assunto | Como |
|---|---|
| Ambiente novo no GCP | E-mail para raulsilva@suape.pe.gov.br com o assunto `Provisionamento de ambiente GCP - <repositório>` |
| Deploy com falha, segredos, permissões, mudança no pipeline | E-mail para raulsilva@suape.pe.gov.br com o link do build |
| Acesso ao GitHub ou ao AGY | E-mail para raulsilva@suape.pe.gov.br |
| Regra de negócio do projeto | Desenvolvedor responsável pelo projeto |

---

## Consulta rápida

- Stack: Python 3.14 (Flask, FastAPI ou Django) no backend, React com Vite no frontend.
- Nome do repositório em kebab-case: `meu-projeto-api`.
- Projeto novo: repositório, MVP, documentação (C4 + Scan Systems) e e-mail `Provisionamento de ambiente GCP - <repositório>`.
- Sem documentação, sem ambiente.
- Antes do chamado: Dockerfile, configuração por variável de ambiente, endpoint de saúde, nenhum outro provedor de nuvem, nenhum segredo commitado, nenhuma vulnerabilidade alta.
- `dev` publica em dev, `hml` em hml e `main` em produção.
- Fluxo: `feature/*` → `dev` → `hml` → `main`, sempre por PR.
- Nunca: push direto em `main`, segredo no código, deploy manual, alteração no `cloudbuild.yaml`.
- Deploy falhou? O ambiente continua na versão anterior. Leia o log, corrija e faça novo push.

---

Raul César
Coordenadoria de Tecnologia da Informação e Comunicação (CTIC)
Complexo Industrial Portuário de Suape
raulsilva@suape.pe.gov.br
