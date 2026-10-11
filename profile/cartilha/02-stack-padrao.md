# Stack padrão de desenvolvimento

[← Voltar ao catálogo da cartilha](../README.md)

**A stack padrão deve ser respeitada.** Estamos lidando com dinheiro público: cada núcleo de CPU, megabyte de memória e instância ativa no Cloud Run custa verba do erário. Padronizar a tecnologia não é apenas facilitar a manutenção compartilhada da equipe, mas garantir que os sistemas sejam modernos, robustos, seguros e de baixo custo operacional.

Salvo restrições técnicas comprovadas e homologadas na arquitetura, todo projeto em Suape adota:

| Camada | Tecnologia oficial | Ferramental |
|---|---|---|
| **Backend** | Python 3.14+ | FastAPI, Flask ou Django |
| **Frontend** | React | Vite, Astro ou similar |
| **Bancos de Dados** | Relacionais ou Documentais leves | PostgreSQL (Cloud SQL), MongoDB, etc. |
| **Empacotamento** | Docker multi-stage | Imagens mínimas para Cloud Run |

---

## 1. Princípio ético: Otimização e dinheiro público

No modelo serverless do Cloud Run, você paga pelo tempo de CPU e memória que a sua aplicação consome. Um código ineficiente ou mal estruturado consome mais instâncias, demora mais para responder e encarece a fatura da nuvem desnecessariamente.

* **Otimize consultas e banco:** Elimine consultas N+1 com `select_related` / `prefetch_related` no Django ou joins explícitos no SQLAlchemy/Pydantic. Indexe chaves de busca e chaves estrangeiras.
* **Tamanho de imagem importa:** Use imagens Docker mínimas (`alpine` ou `slim`). Contêineres pesados atrasam o cold start e exigem instâncias com mais memória alocada.
* **Aproveite o paralelismo do Python 3.14:**
  * O Python 3.14 traz melhorias significativas de performance e suporte aprimorado a concorrência e paralelismo.
  * Utilize rotinas assíncronas (`async` / `await` com FastAPI) em I/O bound (chamadas de banco, APIs externas, leitura de arquivos).
  * Configure workers e threads do servidor ASGI/WSGI (Uvicorn / Gunicorn) calibrados para a carga real, evitando instâncias ociosas sobredimensionadas.

---

## 2. Backend: Python 3.14

### Qual framework escolher?

| Framework | Quando usar | Boas práticas |
|---|---|---|
| **FastAPI** | APIs REST, microsserviços orientados a dados, integrações com IA. | Aproveite validação nativa com Pydantic v2. Mantenha rotas enxutas e jogue lógica de negócio em services desacoplados. |
| **Flask** | Microsserviços enxutos ou serviços onde o backend também distribui os arquivos estáticos do frontend. | Use Blueprints para modularizar rotas e factory functions (`create_app`) para facilitar testes com pytest. |
| **Django** | Sistemas com modelagem relacional extensa, painel administrativo complexo ou regras densas de permissão. | Isole regras de negócio fora de models e views gigantes. Use DRF ou Django Ninja para construir endpoints modernos. |

### Toolchain recomendada
* **Gerenciador de pacotes:** [`uv`](https://docs.astral.sh/uv/) para gerenciar dependências e gerar lockfiles reprodutíveis (`uv.lock`) em milissegundos.
* **Linter e formatação:** [`ruff`](https://docs.astral.sh/ruff/) para garantir código limpo e idiomático antes de commitar.
* **Tipagem:** Type hints rigorosos em todos os módulos.

---

## 3. Frontend: React com Vite ou Astro

Para construir interfaces rápidas, responsivas e leves:

* **React + Vite:** Padrão para Single Page Applications (SPAs), painéis administrativos e sistemas transacionais ricos em interação no cliente.
* **React + Astro (ou similar):** Excelente para páginas orientadas a conteúdo, portais públicos e sistemas que se beneficiam de Server-Side Rendering leve ou geração estática (SSG) com ilhas de interatividade, garantindo carregamento instantâneo.
* **TypeScript obrigatório:** `strict: true` no `tsconfig.json`. Elimine o uso de `any` para prevenir falhas de runtime no navegador.
* **Estilização eficiente:** Tailwind CSS, Radix UI ou shadcn/ui. Evite bibliotecas pesadas de componentes que inflam o bundle e lentificam a inicialização.

---

## 4. Bancos de dados leves e eficientes

Escolha a persistência conforme a modelagem real dos dados:

* **PostgreSQL (Cloud SQL):** Banco relacional padrão para dados estruturados, integridade referencial, transações ACID e consultas analíticas.
* **MongoDB:** Banco de documentos leve para catálogos flexíveis, históricos de logs, documentos semiestruturados ou modelos que demandem esquema dinâmico.
* **Proibido em produção:** SQLite em disco local de contêiner (`/tmp` ou `./data.db`), pois o Cloud Run descarta o disco ao recriar instâncias, causando perda irreversível de dados.

---

## 5. Exceções à stack padrão

A stack padrão é a regra. Exceções são raras e aceitas apenas quando houver **restrições técnicas comprovadas da aplicação** (por exemplo, sistemas legados com dependências binárias específicas, ou apps móveis com Expo/React Native).

Caso precise de outra tecnologia:
1. Comprove a restrição técnica e justifique no e-mail do [chamado de provisionamento](06-chamado-de-provisionamento.md).
2. O projeto continua precisando obrigatoriamente de Dockerfile, testes automatizados e conformidade com o Cloud Run.
