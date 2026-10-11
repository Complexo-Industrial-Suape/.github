# Repositório: org, convenções, segredos e Git

[← Voltar ao catálogo da cartilha](../README.md)

Um repositório bem organizado desde o primeiro dia economiza horas de suporte e refatoração. Esta seção detalha as convenções de código, versionamento e segurança que todo projeto em Suape deve seguir.

---

## 1. Localização e permissões

* **Organização oficial:** Crie sempre o repositório dentro da organização [Complexo-Industrial-Suape](https://github.com/Complexo-Industrial-Suape), e nunca na sua conta pessoal.
* **Autonomia:** Todos os desenvolvedores da Coordenadoria de Inovação têm permissão para criar repositórios na organização.
* **Visibilidade:** Repositórios institucionais internos nascem privados, salvo determinação expressa em contrário da CTIC.

---

## 2. Nomenclatura em kebab-case

O nome do repositório define a identidade do projeto no GitHub, o repositório de imagens no Artifact Registry e os nomes dos serviços no Cloud Run. Use **kebab-case estrito**.

### A regra
* Apenas letras minúsculas, números e hífens (`-`).
* Proibido usar maiúsculas, sublinhados (`_`) ou pontos (`.`).
* Formato padrão: `<produto>[-<componente>]`.
  * Componentes padronizados: `-api` (backend), `-web` (frontend), `-mobile` (app), `-infra` (Terraform).
  * Sem sufixo quando o projeto for monorepo ou aplicação unificada.
* Mantenha "suape" no nome apenas quando fizer parte da marca oficial do produto (ex.: *Suape Drive*, *RDO Suape*). Não use prefixos redundantes quando o produto não tiver essa identidade.

| Situação | Nome correto (kebab-case) | Como evitar |
|---|---|---|
| API do RDO Suape | `rdo-suape-api` | `RDO_Suape_API`, `rdo.suape.api` |
| Frontend do RDO Suape | `rdo-suape-web` | `RDO-suape-frontend`, `rdo_frontend` |
| Sistema unificado | `suape-drive` | `SuapeDrive`, `suape_drive` |
| Frontend de premiação | `premio-inova-industria-web` | `premio_inova_industria_frontend` |

---

## 3. Estrutura do projeto e Monorepo

Se o seu projeto reúne frontend e backend no mesmo repositório, organize as pastas com fronteiras claras:

```text
meu-projeto/
├── web/       # Frontend React/Vite com Dockerfile próprio
├── api/       # Backend Python com Dockerfile próprio
├── docs/      # Documentação oficial (architecture/ com C4 e systems/ com Scan Systems)
└── infra/     # Opcional: IaC (Terraform) ou scripts auxiliares
```

> **Atenção:** Mesmo quando o projeto for empacotado em um único container (por exemplo, backend Flask que serve o bundle React compilado), mantenha a separação em `web/` e `api/`. Nesse caso, um único `Dockerfile` na raiz copia e compila ambas as pastas.

---

## 4. Segurança de segredos e arquivos locais

A regra de ouro da CTIC é: **segredo em repositório é incidente de segurança.**

1. **Nunca commite credenciais:** Senhas, tokens JWT, chaves de API do Google/Gemini, strings de conexão a bancos de dados e chaves privadas de service account jamais sobem para o Git.
2. **Template de ambiente (`.env.example`):**
   * Mantenha no repositório um arquivo `.env.example` listando **todas** as variáveis que o sistema consome.
   * Coloque apenas nomes e valores ilustrativos ou placeholders (ex.: `DATABASE_URL=postgresql://user:pass@localhost:5432/meubanco`).
   * Não coloque e-mails institucionais reais, URLs privadas de produção nem credenciais de teste em `.env.example`.
3. **Arquivo `.gitignore` obrigatório e completo:**
   Garanta que ambientes locais, caches e builds sejam ignorados:
   ```gitignore
   # Ambientes e segredos
   .env
   .env.local
   *.pem
   *.key
   service-account*.json

   # Python
   __pycache__/
   *.pyc
   .venv/
   .pytest_cache/
   .ruff_cache/

   # Node / Frontend
   node_modules/
   dist/
   build/
   .env*.local

   # Banco e uploads locais
   *.sqlite3
   *.db
   uploads/
   ```

---

## 5. Integração com a Marca Suape (`suape-brand`)

O repositório [suape-brand](https://github.com/Complexo-Industrial-Suape/suape-brand) concentra os logotipos, paletas de cores, fontes oficiais e diretrizes visuais do Complexo.

* **Copie apenas o que usar:** Selecione os arquivos de imagem, ícones ou fontes necessários e copie-os para a pasta estática do seu frontend (ex.: `web/public/brand/`).
* **NUNCA use Git Submodule:** O uso de submódulo quebra o deploy automático no Cloud Build e dificulta o clone local.
* **Clone para consulta:** Se você clonar o `suape-brand` localmente para extrair arquivos, adicione a pasta clonada ao seu `.gitignore`:
  ```gitignore
  suape-brand/
  ```
  Nunca commite o repositório da marca inteiro dentro do seu projeto.

---

## 6. Boas práticas de Git e Commits assinados

1. **Assinatura obrigatória (Verified Badge):**
   Todos os commits devem ser assinados digitalmente com chave SSH ed25519 pessoal. Commits sem o selo **Verified** não são aceitos para provisionamento nem para deploy em produção. Veja o [guia passo a passo de SSH](01-chave-ssh-autenticacao-e-assinatura.md).
2. **Padrão de commits semânticos (Conventional Commits):**
   Escreva mensagens de commit claras e objetivas em português ou inglês:
   * `feat: adiciona endpoint de agendamento de vistorias`
   * `fix: resolve cálculo de tempo de permanência de carretas`
   * `docs: atualiza diagrama C4 de containers`
   * `test: adiciona testes unitários para emissão de relatórios`
3. **Estado inicial na `main`:**
   Ao desenvolver seu MVP, mantenha o código na branch `main`. Não crie branches `dev` e `hml` manualmente: elas serão geradas e amarradas aos gatilhos do GCP durante a fase de provisionamento. Caso já existam em projetos herdados, serão preservadas e vinculadas aos pipelines.

---

## Checklist rápido do repositório

Antes de solicitar ambiente, confirme:

- [ ] Repositório criado dentro da organização `Complexo-Industrial-Suape`.
- [ ] Nome rigorosamente em **kebab-case** (`<produto>[-<componente>]`).
- [ ] Código inicial do MVP testado e commiltado na branch `main`.
- [ ] Commits assinados com SSH e exibindo selo **Verified** no GitHub.
- [ ] Nenhum arquivo `.env` ou credencial real rastreada pelo Git.
- [ ] Arquivo `.env.example` documentando todas as variáveis necessárias.
- [ ] Pasta `suape-brand/` ignorada no `.gitignore` e assets incorporados localmente.
- [ ] Estrutura de pastas respeitando monorepo (`web/`, `api/`, `docs/`) quando aplicável.
