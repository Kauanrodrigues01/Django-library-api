# Django Library API

Uma API desenvolvida com Django REST Framework para gerenciar uma biblioteca. Este projeto fornece endpoints para operações CRUD em livros, autores e categorias, além de suporte para empréstimos de livros e autenticação de usuários. 

## Funcionalidades

- **Livros**: Crie, leia, atualize e exclua informações sobre livros, incluindo título, descrição, data de publicação, categoria e autor.
- **Autores**: Gerencie informações sobre autores, incluindo nome e biografia.
- **Categorias**: Mantenha categorias para livros.
- **Empréstimos**: Controle de empréstimos de livros, incluindo data de início, data prevista de devolução e status de devolução.
- **Autenticação**: Suporte a autenticação de usuários utilizando tokens JWT.
- **Validações**: Validações customizadas para garantir a integridade dos dados, como garantir que nomes e biografias não sejam vazios ou contenham apenas dígitos.

## Instalação

1. Clone o repositório:
    ```bash
    git clone https://github.com/seu-usuario/django-library-api.git
    ```

2. Navegue para o diretório do projeto:
    ```bash
    cd django-library-api
    ```

3. Crie um ambiente virtual e instale as dependências:
    ```bash
    python -m venv env
    source env/bin/activate  # No Windows: env\Scripts\activate
    pip install -r requirements.txt
    ```

4. Realize as migrações do banco de dados:
    ```bash
    python manage.py migrate
    ```

5. Inicie o servidor de desenvolvimento:
    ```bash
    python manage.py runserver
    ```

## Uso

Acesse os endpoints da API através dos seguintes URLs:
- **Livros**: `/api/livros/`
- **Autores**: `/api/livros/categorias/`
- **Categorias**: `/api/livros/categorias/`
- **Empréstimos**: `/api/emprestimos/`
- **Autenticação**: `/api/token/`, `/api/token/refresh/`, `/api/token/verify/`

Consulte a documentação do Django REST Framework para mais detalhes sobre como interagir com a API.

## Contribuição

Sinta-se à vontade para contribuir com melhorias ou correções. Veja o arquivo [CONTRIBUTING.md](CONTRIBUTING.md) para mais informações sobre como contribuir.

## Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).
