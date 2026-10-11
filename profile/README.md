# Cartilha de Desenvolvimento de Suape

Coordenadoria de Tecnologia da Informação e Comunicação (CTIC) · versão 3.0 · outubro de 2026

Esta cartilha vale para quem desenvolve na Coordenadoria de Inovação e para todo projeto da org [Complexo-Industrial-Suape](https://github.com/Complexo-Industrial-Suape) que vai rodar no Google Cloud.

A cartilha é um **catálogo**: cada item traz um resumo e um link para o documento que explica o assunto por inteiro. Leia o resumo para saber o que se espera de você e abra o documento quando precisar fazer.

> **Projeto sem documentação não recebe ambiente no GCP. Não há exceção.**
>
> **Commit sem assinatura não é aceito.** Todo desenvolvedor assina os commits com chave SSH.

---

## Obrigações

### 1. Autenticação e assinatura com chave SSH

Todo desenvolvedor tem duas chaves SSH ed25519 (uma para entrar no GitHub, outra para assinar commits), cadastradas na conta do GitHub, e todo commit que ele publica aparece com o selo **Verified**. A chave privada é pessoal e nunca sai da sua máquina.

**Obrigatório a partir desta versão.** Quem ainda não tem as chaves configura antes do próximo commit.

[Ler o guia: gerar, cadastrar e testar as chaves](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/01-chave-ssh-autenticacao-e-assinatura.md)

### 2. Stack padrão

A stack padrão deve ser respeitada: Python 3.14 (FastAPI, Flask ou Django) no backend, React com Vite ou Astro no frontend e bancos leves (PostgreSQL, MongoDB). Estamos lidando com dinheiro público: o código precisa ser otimizado, enxuto e aproveitar a concorrência e o paralelismo do Python 3.14. Exceções exigem comprovação de restrição técnica no chamado.

[Ler: diretrizes da stack, boas práticas e otimização](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/02-stack-padrao.md)

### 3. Repositório: org, nome e segredos

O repositório fica na org Complexo-Industrial-Suape, com nome em kebab-case, código do MVP na `main`, nenhum segredo commitado, assets da marca copiados para o próprio projeto e commits assinados.

[Ler: checklist do repositório](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/03-repositorio.md)

### 4. Pronto para o GCP

Cada parte publicável tem `Dockerfile`, escuta na porta `PORT`, lê toda a configuração de variáveis de ambiente, expõe um endpoint de saúde, tem testes que rodam com um comando e não depende de outro provedor de nuvem nem de dependência com vulnerabilidade alta ou crítica.

[Ler: checklist técnico](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/04-pronto-para-o-gcp.md)

### 5. Documentação: C4 e Scan Systems

O repositório traz `README.md`, os diagramas C4 e o relatório do Scan Systems, gerados com as skills `/c4-architecture` e `/scan-systems`. Documentação ausente ou incompleta bloqueia o provisionamento.

[Ler: arquivos exigidos e regras de escrita](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/05-documentacao.md)

### 6. Chamado de provisionamento

O pedido de ambiente é um e-mail para a infraestrutura com o assunto `Provisionamento de ambiente GCP - <repositório>`. As respostas sobre público, disponibilidade e prazo definem o tamanho, e portanto o custo, do ambiente.

[Ler: modelo do e-mail e o que acontece depois](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/06-chamado-de-provisionamento.md)

### 7. Fluxo de trabalho e deploy

Cada branch publica no seu ambiente: `dev` em dev, `hml` em hml e `main` em **produção**. O caminho é sempre `feature/*` → `dev` → `hml` → `main`, por PR. Não existe push direto em `main` nem deploy manual.

[Ler: regras, acompanhamento do deploy, falhas e hotfix](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/07-fluxo-de-trabalho-e-deploy.md)

### 8. Papéis e caminho de um projeto novo

O desenvolvedor cuida do projeto e da documentação. A infraestrutura cuida do ambiente e do pipeline e não mexe em regra de negócio.

[Ler: quem faz o quê e as etapas de um projeto novo](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/08-papeis-e-caminho-do-projeto.md)

### 9. Marca e identidade visual (Suape Brand Kit)

Todo sistema desenvolvido por Suape usa obrigatoriamente a splash screen oficial na abertura e logotipos vetorizados conforme as diretrizes da CCOM (Coordenadoria de Comunicação). Proibido Git Submodule e cópia integral do kit.

[Ler: diretrizes da CCOM, splash screen obrigatória e integração](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/09-marca-e-identidade-visual.md)

---

## Consulta rápida

- Commits assinados com chave SSH, selo **Verified** no GitHub.
- Stack obrigatória: Python 3.14 (FastAPI/Flask/Django), React (Vite/Astro), bancos leves (PostgreSQL/MongoDB). Código otimizado para economizar recursos públicos.
- Repositório em kebab-case, na org, sem segredo.
- Splash screen oficial obrigatória em todos os sistemas e logos da CCOM.
- Sem documentação, sem ambiente.
- `feature/*` → `dev` → `hml` → `main`, sempre por PR.
- Nunca: push direto em `main`, segredo no código, deploy manual, alteração no `cloudbuild.yaml`.

---

## Contato

| Assunto | Como |
|---|---|
| Ambiente novo no GCP | E-mail para raulsilva@suape.pe.gov.br com o assunto `Provisionamento de ambiente GCP - <repositório>` |
| Deploy com falha, segredos, permissões, mudança no pipeline | E-mail para raulsilva@suape.pe.gov.br com o link do build |
| Acesso ao GitHub ou ao AGY | E-mail para raulsilva@suape.pe.gov.br |
| Regra de negócio do projeto | Desenvolvedor responsável pelo projeto |

---

Raul César
Coordenadoria de Tecnologia da Informação e Comunicação (CTIC)
Complexo Industrial Portuário de Suape
raulsilva@suape.pe.gov.br
