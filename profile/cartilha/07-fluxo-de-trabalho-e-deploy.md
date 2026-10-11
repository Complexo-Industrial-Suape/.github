# Fluxo de trabalho, branches e deploy contínuo no GCP

[← Voltar ao catálogo da cartilha](../README.md)

Depois que o ambiente é provisionado pela infraestrutura, o desenvolvimento segue um fluxo automatizado e contínuo. Não existem botões manuais de deploy nem esteiras fora do Git: **todo deploy é acionado pelo ciclo de branches e Pull Requests.**

---

## 1. Mapeamento de branches e ambientes

| Branch no Git | Ambiente no GCP | Quem acessa | Propósito |
|---|---|---|---|
| `dev` | **Ambiente de Desenvolvimento (dev)** | Desenvolvedores | Testes contínuos de integração de novas funcionalidades. |
| `hml` | **Ambiente de Homologação (hml)** | Desenvolvedores, POs e clientes | Validação final de regras de negócio antes de ir para o ar. |
| `main` | **Ambiente de Produção (prod)** | Usuários finais / público | Sistema em operação real. |

> **Atenção:** Entrou na branch, o deploy inicia imediatamente. Não existe etapa intermediária de confirmação manual após o merge.

---

## 2. O ciclo de vida do código (Fluxo de PRs)

```text
feature/minha-tarefa ──PR──▶ dev ──PR──▶ hml ──PR──▶ main
                              │           │           │
                         Deploy dev   Deploy hml  Deploy PROD
```

### Passo a passo de uma tarefa:

1. **Crie a branch a partir de `dev`:**
   ```bash
   git checkout dev
   git pull
   git checkout -b feature/nome-da-funcionalidade
   ```
2. **Desenvolva e rode os testes locais:**
   Garanta que a suíte passe na sua máquina antes de enviar commits.
3. **Faça commits atômicos e assinados:**
   Todo commit deve ter a assinatura SSH ativa (`git commit -S -m "feat: ..."`).
4. **Abra Pull Request para `dev`:**
   Ao realizar o merge do PR, o Cloud Build dispara e atualiza o ambiente de desenvolvimento.
5. **Teste e valide em dev:**
   Confira o comportamento do sistema com os dados de desenvolvimento.
6. **Promova para homologação (`dev → hml`):**
   Abra um PR da branch `dev` para a branch `hml`. O merge dispara a publicação automática em homologação.
7. **Homologue com os usuários/clientes.**
8. **Promova para produção (`hml → main`):**
   Com a funcionalidade validada em homologação, abra um PR da branch `hml` para a branch `main`. O merge desse PR é o que coloca o código em produção.

---

## 3. O que o Cloud Build executa a cada commit

Para entender o ciclo e saber onde depurar quando algo falhar, o pipeline executa rigorosamente estas etapas:

1. **Testes e validações de código:**
   Executa a suíte de testes do projeto (`pytest` ou `npm test`). Se algum teste quebrar, o pipeline é cancelado na hora e nada é publicado.
2. **Build da imagem Docker:**
   Constrói a imagem com base no `Dockerfile` do projeto, injetando variáveis de build necessárias (como `VITE_*`).
3. **Publicação no Artifact Registry:**
   Armazena a imagem gerada no repositório oficial do projeto com a tag imutável do commit (`${_ENV}-${SHORT_SHA}`).
4. **Execução de migrações de banco (se houver):**
   Para projetos com Alembic ou Django Migrations, o pipeline aplica as migrações contra o banco de dados do respectivo ambiente **antes** de atualizar o tráfego do serviço. Se a migração falhar, o deploy é cancelado, protegendo o banco contra estados inconsistentes.
5. **Atualização no Cloud Run:**
   Executa `gcloud run deploy`, apontando o serviço para a nova imagem publicada.
6. **Sonda de integridade (Smoke Test):**
   Dispara uma requisição HTTP contra o endpoint de saúde (`/health` ou `/livez`) para confirmar que a aplicação subiu com sucesso.

---

## 4. Regras obrigatórias do fluxo

1. **PROIBIDO push direto em `main`:**
   A branch `main` reflete o ambiente de produção. Todo código que entra em `main` deve ter passado obrigatoriamente por PR a partir de `hml`.
2. **Não pule ambientes:**
   Nunca abra PR direto de `feature/*` ou de `dev` para `main`. O caminho rigoroso é `dev → hml → main`.
3. **Não faça deploy manual por fora:**
   Comandos manuais como `gcloud run deploy` a partir da máquina local ou uploads manuais no console do GCP são proibidos. Eles quebram o rastreamento de versões, não deixam histórico de commit e serão sobrescritos no próximo push do Git.
4. **Segredos no Secret Manager:**
   Se sua funcionalidade exige uma nova chave de API ou credencial, solicite a criação do segredo à infraestrutura por e-mail antes de promover o código.
5. **Commits sempre assinados:**
   Todo commit deve exibir o selo **Verified** no GitHub. Veja o [guia de chave SSH](01-chave-ssh-autenticacao-e-assinatura.md).

---

## 5. Como acompanhar o deploy

1. Acesse o [Histórico de Builds no Google Cloud Console](https://console.cloud.google.com/cloud-build/builds;region=southamerica-east1?project=inovacao-491419) (projeto `inovacao-491419`, região `southamerica-east1`).
2. Localize o build nomeado como `<projeto>-<ambiente>` (ex.: `suape-drive-dev` ou `rdo-suape-api-prod`).
3. **Interprete os status:**
   * **Azul (Working):** Build em execução (duração típica: 3 a 8 minutos).
   * **Verde (Success):** Nova versão no ar.
   * **Vermelho (Failure):** Ocorreu um erro. Clique no build para inspecionar o log detalhado do passo que falhou.

O GitHub também exibe o status de validação ao lado de cada commit na visualização de branches e Pull Requests.

---

## 6. O que fazer quando o deploy falha

| Etapa da falha no log | Causa provável | Ação corretiva |
|---|---|---|
| Step `test` ou `lint` | Teste unitário ou checagem de tipos falhou | Execute a suíte localmente, corrija o código e faça novo push. |
| Step `build` | Erro na compilação do Dockerfile ou dependência faltando | Execute `docker build .` localmente para reproduzir e corrigir. |
| Step `migrate` | Erro de sintaxe na migration ou conflito de schema | Avalie a migration localmente antes de reexecutar. Nunca edite migrations já aplicadas. |
| `PERMISSION_DENIED` ou `Secret not found` | Falta de permissão da service account ou segredo ausente | Envie o link do build com falha para a infraestrutura por e-mail. |
| Step `smoke` / Health check | Aplicação subiu mas respondeu 500 ou timeout na rota de saúde | Verifique os logs de inicialização no painel do Cloud Run. |

---

## 7. Situações excepcionais

### Commits apenas de documentação
Commits que alteram exclusivamente arquivos em `docs/` ou arquivos com extensão `*.md` possuem filtro ignorado (`ignored-files`) e **não disparam builds**, economizando recursos.

### Correções críticas de produção (Hotfix)
Quando um bug crítico estiver quebrando produção e não puder aguardar o ciclo normal:
1. Crie uma branch a partir da `main`: `git checkout main && git pull && git checkout -b hotfix/descricao`
2. Corrija o bug, valide os testes e abra PR diretamente para a `main`.
3. Após o merge e deploy em produção, **é obrigatório fazer o back-merge:** abra PR da `main` para `hml` e de `hml` para `dev`. Se esquecer esse passo, o próximo deploy rotineiro vai sobrescrever a correção.

### Reversão de emergência (Rollback)
Se um deploy quebrar o ambiente e exigir retorno imediato da versão anterior:
1. Acesse o [Painel do Cloud Run](https://console.cloud.google.com/run?project=inovacao-491419).
2. Selecione o serviço afetado e acesse a aba **Revisões**.
3. Localize a revisão saudável anterior e clique em **Gerenciar tráfego**, direcionando 100% das requisições para ela.
4. **Atenção:** Essa ação é paliativa. Faça imediatamente o `git revert` do commit problemático no Git para alinhar a branch com o que está rodando.
