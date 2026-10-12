# Repositório: organização, convenções e Git

[← Voltar ao catálogo da cartilha](../README.md)

Organizar o repositório direito desde o primeiro commit evita retrabalho e chamados travados. Aqui estão as regras práticas para criar, nomear e estruturar projetos em Suape.

---

## 1. Localização e permissões

* **Org oficial:** Crie o repositório sempre dentro da organização [Complexo-Industrial-Suape](https://github.com/Complexo-Industrial-Suape), nunca na sua conta pessoal.
* **Autonomia:** Todos os desenvolvedores da Coordenadoria têm permissão para criar repositórios na organização.
* **Visibilidade:** Projetos internos nascem como repositórios privados, a não ser que haja orientação expressa da CTIC.

---

## 2. Nomenclatura em kebab-case

O nome do repositório define a URL no GitHub, a imagem no Artifact Registry e o serviço no Cloud Run. Use kebab-case estrito.

### Regras práticas
* Use apenas letras minúsculas, números e hífens (`-`).
* Nada de maiúsculas, sublinhados (`_`) ou pontos (`.`).
* Formato: `<produto>[-<componente>]`.
  * Sufixos comuns: `-api` para backend, `-web` para frontend, `-mobile` para apps móveis e `-infra` para Terraform.
  * Sem sufixo quando o projeto for um repositório único.
* Use o termo "suape" no nome apenas se fizer parte da marca oficial do produto (como *Suape Drive* ou *RDO Suape*). Não adicione prefixos à toa.

| Projeto | Nome correto | Como evitar |
|---|---|---|
| API do RDO Suape | `rdo-suape-api` | `RDO_Suape_API`, `rdo.suape.api` |
| Frontend do RDO Suape | `rdo-suape-web` | `RDO-suape-frontend`, `rdo_frontend` |
| Sistema unificado | `suape-drive` | `SuapeDrive`, `suape_drive` |
| Frontend do prêmio | `premio-inova-industria-web` | `premio_inova_industria_frontend` |

---

## 3. Estrutura de Monorepo

Se você juntar frontend e backend no mesmo repositório, separe as pastas com clareza:

```text
meu-projeto/
├── web/       # Frontend React/Vite com Dockerfile próprio
├── api/       # Backend Python com Dockerfile próprio
├── docs/      # Documentação técnica (C4 e Scan Systems)
└── infra/     # Opcional: Terraform ou scripts de infra
```

Se o projeto rodar em um contêiner único (por exemplo, um backend Flask que entrega a build estática do React), mantenha as pastas `web/` e `api/` separadas da mesma forma. O `Dockerfile` na raiz apenas copia e compila os dois lados.

---

## 4. Segredos e arquivos locais

Segredo commitado no Git gera retrabalho imediato: exige revogar chaves, limpar histórico e atrasa o deploy.

1. **Nunca commite credenciais:** Senhas, chaves de API, tokens JWT, conexões de banco e arquivos de service account ficam fora do Git.
2. **Arquivo de exemplo (`.env.example`):**
   * Mantenha no repositório um `.env.example` com a lista completa das variáveis que a aplicação lê.
   * Coloque apenas nomes e placeholders genéricos (exemplo: `DATABASE_URL=postgresql://user:pass@localhost:5432/banco`).
   * Não coloque e-mails reais de servidores, URLs privadas de produção nem credenciais válidas no exemplo.
3. **Arquivo `.gitignore`:**
   Mantenha um `.gitignore` limpo e abrangente desde o primeiro commit:
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

## 5. Marca Suape (`suape-brand`)

As diretrizes visuais e logos oficiais ficam no repositório [suape-brand](https://github.com/Complexo-Industrial-Suape/suape-brand). As regras da CCOM e o uso da splash screen obrigatória estão explicados em [Marca e Identidade Visual](09-marca-e-identidade-visual.md).

* **Copie apenas o necessário:** Copie os arquivos de logotipo, ícones e fontes diretamente para a pasta de arquivos estáticos do frontend (por exemplo, `web/public/brand/`).
* **Não use Git Submodule:** Submódulos quebram com frequência em esteiras de CI/CD e complicam o clone da equipe.
* **Se clonar para consulta:** Adicione a pasta ao seu `.gitignore`:
  ```gitignore
  suape-brand/
  ```
  Nunca suba o kit da marca inteiro para dentro do repositório do seu sistema.

---

## 6. Commits assinados e histórico limpo

1. **Assinatura obrigatória:** Todo commit publicado precisa ter o selo **Verified** no GitHub gerado por chave SSH ed25519. Sem isso, o chamado de provisionamento não é aprovado. Veja o [guia de configuração de SSH](01-chave-ssh-autenticacao-e-assinatura.md).
2. **Commits semânticos:** Escreva mensagens que expliquem o que mudou de forma direta:
   * `feat: adiciona endpoint de agendamento de vistorias`
   * `fix: corrige cálculo de tempo de permanência de carretas`
   * `docs: atualiza diagrama C4 de containers`
   * `test: adiciona testes de validação de formulário`
3. **Branch inicial na `main`:** Crie o MVP inicial direto na `main`. Não precisa abrir branches `dev` e `hml` manualmente: elas são criadas e conectadas aos ambientes durante o provisionamento. Se já existirem, serão mantidas.

---

## Checklist rápido

Antes de pedir ambiente, confira:

- [ ] Repositório criado na organização `Complexo-Industrial-Suape`.
- [ ] Nome em **kebab-case** (`<produto>[-<componente>]`).
- [ ] MVP inicial commitado na branch `main`.
- [ ] Commits com assinatura SSH exibindo o selo **Verified** no GitHub.
- [ ] Nenhum arquivo `.env` com credenciais reais commitado.
- [ ] Arquivo `.env.example` com a lista completa de variáveis.
- [ ] Pasta `suape-brand/` no `.gitignore` e assets copiados localmente (ver [Marca e Identidade Visual](09-marca-e-identidade-visual.md)).
- [ ] Pastas organizadas no padrão `web/`, `api/` e `docs/` quando houver frontend e backend juntos.
