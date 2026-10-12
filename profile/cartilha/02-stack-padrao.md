# Stack padrão de desenvolvimento

[← Voltar ao catálogo da cartilha](../README.md)

A stack padrão precisa ser respeitada. Estamos operando com dinheiro público: cada núcleo de CPU, megabyte de RAM e instância ligada no Cloud Run sai direto do orçamento do Estado. Padronizar ferramentas evita que a equipe perca tempo reinventando esteiras de CI/CD ou decifrando frameworks exóticos a cada revisão de código.

Salvo restrições técnicas reais e aprovadas previamente na arquitetura, todo projeto em Suape usa:

| Camada | Tecnologia oficial | Ferramentas |
|---|---|---|
| **Backend** | Python 3.14+ | FastAPI, Flask ou Django |
| **Frontend** | React | Vite, Astro ou similar |
| **Bancos de dados** | Relacionais ou documentais leves | PostgreSQL (Cloud SQL), MongoDB |
| **Empacotamento** | Docker multi-stage | Imagens mínimas rodando no Cloud Run |

---

## 1. Responsabilidade com recursos públicos

No Cloud Run, a cobrança é calculada por milissegundo de CPU e memória consumida. Código mal escrito ou inchado exige instâncias maiores, demora a inicializar e encarece a fatura da nuvem sem necessidade.

* **Consultas de banco:** Evite o problema clássico de N+1 queries usando `select_related` e `prefetch_related` no Django ou joins explícitos com SQLAlchemy. Indexe chaves de busca e chaves estrangeiras.
* **Tamanho de imagem:** Use imagens Docker mínimas (`alpine` ou `slim`). Contêineres pesados aumentam o tempo de cold start e custam mais caro.
* **Aproveite o paralelismo do Python 3.14:**
  * O Python 3.14 traz melhorias consistentes de concorrência e execução.
  * Adote rotinas assíncronas (`async` e `await`) para operações com I/O intensivo (chamadas de banco, consumo de APIs externas, leitura de arquivos).
  * Dimensione os workers e threads do Uvicorn ou Gunicorn de acordo com a carga real, sem alocar recursos ociosos.

---

## 2. Backend: Python 3.14

### Qual framework escolher?

| Framework | Quando usar | Como estruturar |
|---|---|---|
| **FastAPI** | APIs REST, microsserviços rápidos, integrações com IA. | Valide entradas e saídas com Pydantic v2. Mantenha rotas enxutas e concentre a lógica em services desacoplados. |
| **Flask** | Serviços pequenos ou quando o backend também entrega os arquivos estáticos do frontend. | Organize rotas com Blueprints e use factory functions (`create_app`) para simplificar os testes com pytest. |
| **Django** | Sistemas com regras complexas de permissão, muitas tabelas relacionais ou necessidade do painel administrativo. | Mantenha regras de negócio fora de models e views sobrecarregadas. Use DRF ou Django Ninja para construir endpoints limpos. |

### Ferramentas de desenvolvimento
* **Gerenciador de pacotes:** Use o [`uv`](https://docs.astral.sh/uv/). Ele resolve dependências em milissegundos e cria lockfiles confiáveis (`uv.lock`).
* **Linter e formatação:** Use o [`ruff`](https://docs.astral.sh/ruff/) antes de commitar qualquer alteração.
* **Tipagem:** Escreva type hints em funções, parâmetros e modelos.

---

## 3. Frontend: React com Vite ou Astro

* **React com Vite:** Escolha padrão para painéis administrativos, SPAs e telas com muitas interações dinâmicas no cliente.
* **React com Astro:** Ideal para páginas públicas, portais institucionais e interfaces focadas em conteúdo, onde carregamento rápido e geração estática trazem economia de processamento.
* **TypeScript:** Configure `strict: true` no `tsconfig.json`. Evite `any` para não empurrar erros bobos de runtime para o navegador do usuário.
* **Estilização:** Use Tailwind CSS, Radix UI ou shadcn/ui. Evite bibliotecas gigantescas que pesam o bundle inicial.

---

## 4. Bancos de dados

Escolha o banco de acordo com a modelagem do dado:

* **PostgreSQL (Cloud SQL):** Banco relacional padrão para dados transacionais, tabelas relacionais e integridade referencial.
* **MongoDB:** Banco de documentos leve para catálogos flexíveis, históricos e dados semiestruturados.
* **Proibido em produção:** SQLite em disco local de contêiner (`/tmp` ou `./data.db`). O Cloud Run descarta o disco ao recriar instâncias, e você vai perder dados.

---

## 5. Exceções à stack padrão

A stack é a regra. Exceções são raras e aceitas apenas se houver restrições técnicas comprovadas do sistema (como dependências legadas muito específicas ou aplicativos móveis com React Native/Expo).

Se precisar usar outra tecnologia:
1. Comprove a necessidade técnica e descreva no [chamado de provisionamento](06-chamado-de-provisionamento.md).
2. O projeto continua precisando obrigatoriamente de Dockerfile, testes automatizados e total compatibilidade com o Cloud Run.
