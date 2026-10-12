# Cartilha de Desenvolvimento de Suape

Coordenadoria de Tecnologia da Informação e Comunicação (CTIC) · versão 3.0 · outubro de 2026

Esta cartilha é o guia de desenvolvimento da Coordenadoria de Inovação para qualquer projeto da org [Complexo-Industrial-Suape](https://github.com/Complexo-Industrial-Suape) que vá rodar no Google Cloud.

Ela funciona como um catálogo prático. Cada item abaixo resume uma obrigação técnica e aponta para o documento com o passo a passo completo.

> **Sem documentação, o projeto não ganha ambiente no GCP. Não há exceção.**
>
> **Commit sem assinatura não entra em produção.** Todo desenvolvedor precisa assinar commits com chave SSH.

---

## Obrigações

### 1. Autenticação e assinatura com chave SSH

Você precisa de duas chaves SSH ed25519 cadastradas no GitHub: uma para push/pull e outra exclusiva para assinar commits. Todo commit publicado precisa exibir o selo **Verified**. Chave privada nunca sai da sua máquina.

[Guia: gerar, cadastrar e testar as chaves](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/01-chave-ssh-autenticacao-e-assinatura.md)

### 2. Stack padrão

Trabalhamos com Python 3.14 (FastAPI, Flask ou Django) no backend e React com Vite ou Astro no frontend. Bancos leves: PostgreSQL ou MongoDB. Como lidamos com verba pública, o código precisa ser enxuto, sem vazamento de memória e aproveitando o paralelismo do Python 3.14. Exceção exige justificativa técnica no chamado.

[Diretrizes da stack, boas práticas e otimização](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/02-stack-padrao.md)

### 3. Repositório: org, nome e segredos

Todo repositório fica na org Complexo-Industrial-Suape, com nome em kebab-case, código inicial na branch `main` e zero segredos commitados. Assets da marca ficam copiados no próprio projeto, e os commits precisam estar assinados.

[Checklist de repositório e convenções Git](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/03-repositorio.md)

### 4. Pronto para o GCP

Toda parte publicável precisa de Dockerfile, escutar na porta `PORT`, carregar configuração apenas por variáveis de ambiente, responder em rota de health check e ter testes rodando por comando único. Sem dependência oculta de outra nuvem e sem pacotes com vulnerabilidade alta ou crítica.

[Checklist técnico para Cloud Run e contêineres](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/04-pronto-para-o-gcp.md)

### 5. Documentação: C4 e Scan Systems

Repositório pronto traz `README.md`, diagramas C4 (Contexto e Contêineres em Mermaid) e o relatório do Scan Systems gerados pelas skills oficiais (`/c4-architecture` e `/scan-systems`). Documentação ausente ou incompleta trava o provisionamento.

[Arquivos obrigatórios, regras de escrita e skills](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/05-documentacao.md)

### 6. Chamado de provisionamento

O pedido de ambiente é feito por e-mail para a infraestrutura com o assunto `Provisionamento de ambiente GCP - <repositório>`. As respostas sobre público, horários e tolerância a quedas definem o tamanho das máquinas e o custo da nuvem.

[Modelo do e-mail e etapas pós-chamado](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/06-chamado-de-provisionamento.md)

### 7. Fluxo de trabalho e deploy

Cada branch entrega direto no seu ambiente: `dev` publica em desenvolvimento, `hml` em homologação e `main` em produção. O fluxo é sempre `feature/*` → `dev` → `hml` → `main`, exclusivamente por Pull Request. Nada de push direto na `main` e nada de deploy manual no console.

[Regras de PR, esteira do Cloud Build, falhas e hotfix](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/07-fluxo-de-trabalho-e-deploy.md)

### 8. Papéis e caminho de um projeto novo

Desenvolvedor cuida das regras de negócio, do código e da documentação técnica. Infraestrutura cuida dos ambientes, segredos e pipelines, sem interferir na lógica da aplicação.

[Divisão de responsabilidades e ciclo do projeto](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/08-papeis-e-caminho-do-projeto.md)

### 9. Marca e identidade visual (Suape Brand Kit)

Todo sistema de Suape precisa exibir a splash screen oficial na abertura e respeitar os logotipos vetorizados conforme as normas da CCOM. É proibido usar Git Submodule e proibido commitar o kit inteiro no repositório.

[Diretrizes da CCOM, splash screen e integração](https://github.com/Complexo-Industrial-Suape/.github/blob/main/profile/cartilha/09-marca-e-identidade-visual.md) · [Manual em PDF (Drive)](https://drive.google.com/file/d/154VjAL91h3ZSnVLfwki4QChXGyZjBlGW/view?usp=sharing)

---

## Consulta rápida

- Commits com chave SSH e selo Verified no GitHub.
- Stack oficial: Python 3.14 (FastAPI, Flask ou Django), React (Vite ou Astro) e bancos leves (PostgreSQL, MongoDB).
- Repositório em kebab-case, dentro da org, sem credenciais commitadas.
- Splash screen oficial obrigatória na abertura de todo sistema.
- Sem documentação técnica aprovada, o ambiente não é criado.
- Fluxo contínuo: `feature/*` → `dev` → `hml` → `main`, sempre via PR.
- Proibido: push direto na `main`, segredos no código, deploy manual e editar o `cloudbuild.yaml`.

---

## Contato

| Assunto | Canal |
|---|---|
| Novo ambiente no GCP | E-mail para raulsilva@suape.pe.gov.br com assunto `Provisionamento de ambiente GCP - <repositório>` |
| Falhas de deploy, segredos, permissões | E-mail para raulsilva@suape.pe.gov.br com o link do build |
| Acessos ao GitHub ou AGY | E-mail para raulsilva@suape.pe.gov.br |
| Dúvidas sobre o produto e regras de negócio | Fale com o desenvolvedor responsável pelo projeto |

---

Raul César  
Coordenadoria de Tecnologia da Informação e Comunicação (CTIC)  
Complexo Industrial Portuário de Suape  
raulsilva@suape.pe.gov.br
