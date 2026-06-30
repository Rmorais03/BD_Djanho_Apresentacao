# BD_Django_Apresentacao
Réplica de Base de dados para a Unidade Curricular de Base de Dados.

Este projeto é uma aplicação web desenvolvida em **Django** que serve como interface interativa para gerir uma base de dados PostgreSQL alojada na plataforma Neon. Permite visualizar e interagir com diversas tabelas relacionais através de um website funcional com operações CRUD (Criar, Ler, Atualizar, Eliminar).

---

## 🚀 Como correr o projeto (Passo a Passo)

Para executar o servidor e conseguir abrir a página HTML (com tudo a funcionar) no seu browser a partir de um clone do GitHub, siga atentamente as instruções abaixo:

### Pré-requisitos
- Ter o **Python** instalado no seu computador.
- Ter acesso a um terminal (Linha de Comandos, PowerShell, ou o terminal integrado do VS Code).

### Passo 1: Navegar para a pasta do projeto
Abra o terminal e navegue para dentro da pasta principal da aplicação Django:
```bash
cd Projeto_BD_Django
```

### Passo 2: Criar o Ambiente Virtual (Apenas na 1ª vez)
Como a pasta `venv` não vai para o GitHub, tens de criar um ambiente virtual novo na tua máquina para instalar as bibliotecas de forma isolada:
```bash
python -m venv venv
```

### Passo 3: Ativar o Ambiente Virtual
Após a criação, ativa o ambiente:
- **No Windows (CMD / PowerShell):**
  ```cmd
  venv\Scripts\activate
  ```
- **No Mac / Linux / Git Bash:**
  ```bash
  source venv/bin/activate
  ```
*(Ao ativar com sucesso, o terminal deverá mostrar `(venv)` no início da linha)*

### Passo 4: Instalar as dependências
Com o ambiente ativado, instala todas as bibliotecas necessárias para o projeto funcionar a partir do ficheiro `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Passo 5: Iniciar o Servidor Local
Agora que tudo está configurado, inicia o servidor web interno do Django executando o seguinte comando:
```bash
python manage.py runserver
```

### Passo 6: Visualizar a página
Abre o teu browser favorito (Chrome, Firefox, Edge, Safari, etc.) e acede ao endereço local:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

E já está! A página inicial (Dashboard) deverá carregar com sucesso. 🎉

*(Para parar o servidor a qualquer momento, volta ao terminal e pressiona `CTRL + C`)*

---

## 📂 O que o projeto faz (Funcionalidades)

A aplicação está dividida em várias rotas (páginas) que gerem diferentes entidades da base de dados. O menu principal dá acesso às seguintes áreas:

- **🏠 Dashboard (`/`)**: Página principal que apresenta um resumo do sistema, facilitando a navegação.
- **🏢 Empresas (`/empresas/`)**: Permite visualizar a lista de empresas, registar novas, editar informações e remover empresas da base de dados.
- **🎫 Tickets (`/tickets/`)**: Área de suporte para gestão de tickets (pedidos/incidentes).
- **👨‍💼 Gestores (`/gestores/`)**: Administração dos gestores do sistema e os seus respetivos dados.
- **📄 Documentos (`/documentos/`)**: Gestão do arquivo de documentos associados.
- **📰 Notícias (`/noticias/`)**: Permite gerir publicações, comunicados e notícias.
- **📊 Modelo Lógico (`/modelo/`)**: Apresenta de forma visual a estrutura (esquema) da base de dados utilizando diagramas Mermaid.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** [Python](https://www.python.org/) e [Django](https://www.djangoproject.com/)
- **Base de Dados:** PostgreSQL (alojamento Cloud via [Neon](https://neon.tech/))
- **Frontend:** HTML, CSS, JavaScript (Templates do Django)
