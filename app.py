"""
══════════════════════════════════════════════════════════════
BANK2YOU — app.py
Backend em Python usando o framework Flask

══════════════════════════════════════════════════════════════
O QUE É O FLASK?
──────────────────
Flask é um micro-framework web para Python.
"Micro" = simples, sem baterias incluídas, extensível.

Ele faz três coisas essenciais:
1. Inicia um servidor web em Python
2. Mapeia URLs para funções Python (rotas)
3. Permite renderizar templates HTML (via Jinja2)

══════════════════════════════════════════════════════════════
COMO HTTP FUNCIONA (simplificado)
──────────────────────────────────
Cliente (Navegador) ←──────────────→ Servidor (Flask)

1. GET / → "me dê a página inicial"
   Resposta: HTML da página

2. POST /calcular → "processe estes dados"
   Corpo: { "valor": 5000, "periodo": 10, "tipo": "cdb" }
   Resposta: { "valor_final": "15.937,42", "lucro": ... }

Métodos HTTP principais:
  GET → Buscar dados (sem corpo, parâmetros na URL)
  POST → Enviar dados para processamento
  PUT → Atualizar um recurso completo
  PATCH → Atualizar parcialmente
  DELETE → Deletar um recurso

Status Codes HTTP:
  200 OK → Sucesso
  201 Created → Recurso criado
  400 Bad Request → Dados inválidos enviados pelo cliente
  401 Unauthorized → Não autenticado
  403 Forbidden → Sem permissão
  404 Not Found → Recurso não encontrado
  500 Server Error → Erro interno no servidor

══════════════════════════════════════════════════════════════
ESTRUTURA DE ARQUIVOS FLASK
─────────────────────────────
bank2you/
├── app.py ← este arquivo
├── requirements.txt ← dependências
├── templates/ ← Flask procura HTML aqui
│ └── index.html
└── static/ ← Flask serve automaticamente
    └── style.css

Regra: templates/ para HTML com Jinja2
        static/ para CSS, JS, imagens (arquivos puros)

══════════════════════════════════════════════════════════════
COMO INSTALAR E RODAR
──────────────────────
# 1. Crie e ative um ambiente virtual (boa prática)
python -m venv venv # cria a pasta venv/
source venv/bin/activate # Linux/Mac
venv\\Scripts\\activate # Windows

# 2. Instale as dependências
pip install flask

# 3. Execute o servidor
python app.py

# 4. Acesse no navegador
http://127.0.0.1:5000
══════════════════════════════════════════════════════════════
"""

# ══════════════════════════════════════════════
# IMPORTAÇÕES
# ══════════════════════════════════════════════

from flask import Flask, render_template, request, jsonify

"""
Explicação de cada import:

Flask
  → A classe principal. Usada para criar a aplicação web.
  → app = Flask(__name__) instancia o servidor.

render_template('arquivo.html')
  → Lê o arquivo da pasta templates/
  → Processa as tags Jinja2: {{ variavel }}, {% if %}, {% for %}
  → Retorna o HTML completo para o navegador

request
  → Objeto que representa a REQUISIÇÃO recebida.
  → Disponível globalmente durante uma requisição.
  
  Atributos úteis:
  request.method → 'GET' ou 'POST' ou 'PUT' etc.
  request.get_json() → Lê o corpo JSON da requisição
  request.form → Dados de form HTML (application/x-www-form-urlencoded)
  request.args → Query params da URL (?chave=valor)
  request.files → Arquivos enviados via upload
  request.headers → Cabeçalhos HTTP da requisição
  request.remote_addr → IP do cliente

jsonify(dicionario)
  → Converte dict Python → resposta HTTP com JSON
  → Define automaticamente o header Content-Type: application/json
  → O JavaScript recebe e usa resposta.json() para converter de volta
"""


# ══════════════════════════════════════════════
# CRIANDO A APLICAÇÃO
# ══════════════════════════════════════════════

app = Flask(__name__)

"""
Flask(__name__) — por que __name__?

__name__ é uma variável especial do Python:
  - Quando você executa o arquivo: __name__ == '__main__'
  - Quando outro arquivo importa este: __name__ == 'app'

Flask usa __name__ para determinar:
  - Onde está o arquivo atual (app.py)
  - Onde procurar a pasta templates/ (relativo ao app.py)
  - Onde procurar a pasta static/ (relativo ao app.py)

Configurações opcionais do app:
  app.config['SECRET_KEY'] = 'chave-secreta' # para sessões/cookies
  app.config['DEBUG'] = True # modo debug
  app.config['JSON_SORT_KEYS'] = False # não ordena JSON por padrão
"""


# ══════════════════════════════════════════════
# DADOS DOS INVESTIMENTOS
# Dicionário Python com as informações de cada tipo.
# As chaves correspondem ao value do radio button no HTML.
# ══════════════════════════════════════════════

INVESTIMENTOS = {
    'poupanca': {
        'nome': 'Poupança',
        'taxa_anual': 6.17,
    },
    'cdb': {
        'nome': 'CDB',
        'taxa_anual': 12.00,
    },
    'tesouro': {
        'nome': 'Tesouro Selic',
        'taxa_anual': 12.15,
    },
    'lci': {
        'nome': 'LCI / LCA',
        'taxa_anual': 10.80,
    },
    'fundo': {
        'nome': 'Fundo Multimercado',
        'taxa_anual': 14.00,
    }
}

"""
Tipos de dados em Python (revisão rápida):

str → texto: 'olá', "Bank2You"
int → inteiro: 5, 100, -3
float → decimal: 12.50, 3.14
bool → booleano: True, False
list → lista: [1, 2, 3], ['a', 'b']
dict → dicionário: {'chave': 'valor', 'nome': 'Ana'}
None → nulo: None (equivalente ao null de outras linguagens)

Operações com dicionários:
  d = {'a': 1, 'b': 2}
  d['a'] → 1 (acessa pelo índice)
  d.get('c', 0) → 0 (acessa com valor padrão)
  d.keys() → dict_keys(['a', 'b'])
  d.values() → dict_values([1, 2])
  'd' in d → False (verifica se chave existe)
  'a' in d → True
"""


# ══════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ══════════════════════════════════════════════

def calcular_juros_compostos(capital, taxa_anual_percentual, anos):
    """
    Calcula o montante usando juros compostos.
    
    ┌─────────────────────────────────────────────┐
    │ FÓRMULA: M = C × (1 + i)^t │
    │ │
    │ M = Montante final │
    │ C = Capital inicial (quanto você investiu) │
    │ i = taxa em decimal (12% → 0.12) │
    │ t = tempo em anos │
    └─────────────────────────────────────────────┘
    
    Juros compostos = juros sobre juros.
    No mês 2, você ganha juros sobre (capital + juros do mês 1).
    Por isso o montante cresce exponencialmente, não linearmente.
    
    Exemplo:
    R$ 1.000 a 12% ao ano por 5 anos:
    M = 1000 × (1 + 0.12)^5
    M = 1000 × 1.7623
    M = R$ 1.762,34
    
    Parâmetros:
    -----------
    capital : float — valor inicial investido (R$)
    taxa_anual_percentual : float — taxa em %, ex: 12.0
    anos : int — período em anos
    
    Retorna:
    --------
    tuple: (montante, lucro, rendimento_percentual)
    
    tuple = múltiplos valores retornados de uma vez:
    montante, lucro, rend = calcular_juros_compostos(1000, 12, 5)
    """
    
    # Converte percentual para decimal
    # 12% → 12/100 → 0.12
    taxa_decimal = taxa_anual_percentual / 100
    
    # Aplica a fórmula
    # ** → operador de potência em Python: 2**3 = 8
    montante = capital * (1 + taxa_decimal) ** anos
    
    # Lucro = quanto a mais você terá além do investido
    lucro = montante - capital
    
    # Rendimento percentual total
    # Fórmula: ((M / C) - 1) × 100
    # Exemplo: ((1762 / 1000) - 1) × 100 = 76.2%
    rendimento_percentual = ((montante / capital) - 1) * 100
    
    return montante, lucro, rendimento_percentual
    # return com múltiplos valores → retorna uma tupla automaticamente


def formatar_moeda_br(valor):
    """
    Formata float no padrão brasileiro: 1234567.89 → '1.234.567,89'
    
    f-strings (f"..."):
    ──────────────────
    Forma moderna de formatar strings em Python (Python 3.6+).
    Permite inserir expressões dentro de {}.
    
    Especificadores de formato:
    f"{valor:,.2f}"
            │└──── .2f = 2 casas decimais, tipo float
            └───── , = separador de milhar (padrão americano)
    
    Exemplo: f"{1234567.89:,.2f}" → "1,234,567.89"
    
    Como convertemos para o padrão BR:
    1. Geramos "1,234,567.89" (americano)
    2. , → X (temporário): "1X234X567.89"
    3. . → , (ponto→vírgula): "1X234X567,89"
    4. X → . (X→ponto): "1.234.567,89" ✓
    """
    formatado = f"{valor:,.2f}" # "1,234,567.89"
    formatado = formatado.replace(',', 'X') # "1X234X567.89"
    formatado = formatado.replace('.', ',') # "1X234X567,89"
    formatado = formatado.replace('X', '.') # "1.234.567,89"
    return formatado


# ══════════════════════════════════════════════
# ROTAS (ROUTES)
# 
# O que é uma Rota?
# ──────────────────
# Uma rota mapeia uma URL a uma função Python.
# Quando o navegador acessa uma URL, Flask chama
# a função correspondente e retorna o que ela retornar.
#
# Sintaxe:
# @app.route('/caminho', methods=['GET', 'POST'])
# def minha_funcao():
# return 'resposta'
#
# @app.route() é um DECORADOR:
# → Modifica o comportamento da função abaixo dele.
# → Registra a função como responsável por aquela URL.
# → @ indica decorador em Python.
# ══════════════════════════════════════════════


@app.route('/')
def pagina_inicial():
    """
    ROTA: GET /
    ───────────────────────────────────────────────
    Serve a página HTML principal do simulador.
    
    Chamada quando:
    → Usuário digita http://localhost:5000/ no navegador
    → Ou http://localhost:5000 (/ é implícito)
    
    methods não especificado → aceita apenas GET (padrão)
    
    GET = requisição de leitura: "me dê este recurso"
    Não tem corpo. Parâmetros vão na URL: /busca?q=flask
    ───────────────────────────────────────────────
    render_template():
    
    1. Procura templates/index.html
    2. Lê o arquivo
    3. Processa as tags Jinja2 ({{ }}, {% %})
    4. Retorna o HTML processado como resposta HTTP
    
    Você pode passar variáveis para o template:
    render_template('index.html', usuario='Ana', saldo=1500.00)
    
    No HTML (Jinja2):
    <p>Olá, {{ usuario }}!</p> → Olá, Ana!
    <p>Saldo: R$ {{ saldo }}</p> → Saldo: R$ 1500.0
    
    Estruturas de controle Jinja2:
    {% if usuario %}Logado{% endif %}
    {% for item in lista %}<li>{{ item }}</li>{% endfor %}
    """
    return render_template('index.html')


@app.route('/calcular', methods=['POST'])
def calcular():
    """
    ROTA: POST /calcular
    ───────────────────────────────────────────────
    Recebe os dados de investimento, calcula e retorna JSON.
    
    FLUXO COMPLETO:
    ┌─────────────────────────────────────────────┐
    │ 1. JS faz fetch('/calcular', {POST, JSON}) │
    │ 2. Flask recebe a requisição │
    │ 3. Flask chama esta função │
    │ 4. Extraímos os dados com request.get_json()│
    │ 5. Validamos os dados │
    │ 6. Calculamos com juros compostos │
    │ 7. Retornamos jsonify({resultado}) │
    │ 8. JS recebe resposta.json() e exibe │
    └─────────────────────────────────────────────┘
    
    methods=['POST'] → aceita APENAS requisições POST.
    POST = envia dados no corpo (body) da requisição.
    Ideal para: cálculos, criação de recursos, formulários.
    ───────────────────────────────────────────────
    """
    
    # try/except → tratamento de erros em Python
    # Equivalente ao try/catch do JavaScript
    try:
        
        # ── Lendo os dados enviados pelo JavaScript ──
        dados = request.get_json()
        """
        request.get_json():
          → Lê o corpo da requisição HTTP
          → Interpreta como JSON
          → Converte para dicionário Python
          
          Equivalente a: JSON.parse(body) no JavaScript
          
          Se o Content-Type não for application/json,
          ou o JSON for inválido → retorna None
          
          Parâmetro silent=True → retorna None ao invés de erro:
          dados = request.get_json(silent=True)
        """
        
        # Verifica se chegaram dados
        if not dados:
            # Retorna erro com status 400 (Bad Request)
            return jsonify({'erro': 'Nenhum dado recebido'}), 400
            """
            jsonify({'erro': '...'}) → cria resposta JSON
            , 400 → define o status code HTTP da resposta
            
            O Flask usa a tupla (resposta, status_code) para
            criar respostas HTTP customizadas.
            """
        
        # ── Extraindo os campos ──
        valor = dados.get('valor')
        periodo = dados.get('periodo')
        tipo = dados.get('tipo')
        """
        dict.get('chave', padrao):
          → Retorna o valor se a chave existe
          → Retorna padrao se não existe (default: None)
          
          Mais seguro que dict['chave'] que lança KeyError
          se a chave não existir.
        """
        
        # ── Validações ──
        
        # all([a, b, c]) → True somente se todos forem "truthy"
        # None, 0, '', [], {} são "falsy" em Python
        if not all([valor is not None, periodo, tipo]):
            return jsonify({'erro': 'Campos obrigatórios ausentes: valor, periodo, tipo'}), 400
        
        if tipo not in INVESTIMENTOS:
            return jsonify({'erro': f'Investimento "{tipo}" não encontrado'}), 400
            """
            f-string com variável:
            f'Investimento "{tipo}" não encontrado'
            Se tipo = 'bitcoin' → 'Investimento "bitcoin" não encontrado'
            """
        
        # Conversão de tipos
        valor = float(valor)
        periodo = int(periodo)
        """
        float('1000') → 1000.0
        int('10') → 10
        int(10.9) → 10 (trunca, não arredonda)
        
        Podem lançar ValueError se a conversão falhar:
        float('abc') → ValueError: could not convert string to float
        Por isso estamos dentro do try/except.
        """
        
        # ── Validações de valor ──
        if valor <= 0:
            return jsonify({'erro': 'O valor deve ser maior que R$ 0'}), 400
        
        if valor > 100_000_000:
            # _ em números: separador visual (Python 3.6+)
            # 100_000_000 = 100000000 (cem milhões)
            return jsonify({'erro': 'Valor máximo: R$ 100.000.000'}), 400
        
        if not (1 <= periodo <= 50):
            # Expressão encadeada: 1 <= periodo <= 50
            # Python permite isso! Em outras linguagens precisaria de and
            return jsonify({'erro': 'Período deve ser entre 1 e 50 anos'}), 400
        
        # ── Busca as informações do investimento ──
        investimento = INVESTIMENTOS[tipo]
        taxa = investimento['taxa_anual']
        
        # ── Cálculo principal ──
        montante, lucro, rendimento_pct = calcular_juros_compostos(
            capital=valor,
            taxa_anual_percentual=taxa,
            anos=periodo
        )
        """
        Chamando a função com argumentos nomeados (keyword arguments):
        calcular_juros_compostos(capital=1000, taxa_anual_percentual=12, anos=5)
        
        Vantagens:
        → Código mais legível (sabe o que é cada parâmetro)
        → Ordem não importa quando usamos nomes
        → Evita bugs de ordem de argumentos
        """
        
        # ── Monta a resposta ──
        resposta = {
            # Valores formatados para exibição
            'valor_inicial': formatar_moeda_br(valor),
            'valor_final': formatar_moeda_br(montante),
            'lucro': formatar_moeda_br(lucro),
            
            # Valores brutos para uso no JS
            'taxa': taxa,
            'periodo': periodo,
            'nome_investimento': investimento['nome'],
            
            # Rendimento com 2 casas decimais
            # f"{valor:.2f}" → formata float com 2 casas
            'rendimento_percentual': f"{rendimento_pct:.2f}",
        }
        
        # Retorna o dicionário como JSON com status 200 (OK)
        return jsonify(resposta)
        # Status 200 é o padrão, não precisa especificar
    
    except ValueError as e:
        """
        except TipoDoErro as variavel:
          → Captura erros do tipo específico
          → 'as e' guarda o erro na variável e para inspecionar
        
        ValueError: erro de valor inválido
        Ex: float('abc'), int('xyz')
        
        Hierarquia de exceções Python:
        Exception
        ├── ValueError → valor inválido
        ├── TypeError → tipo errado
        ├── KeyError → chave não encontrada em dict
        ├── IndexError → índice fora do range em list
        ├── ZeroDivisionError → divisão por zero
        └── FileNotFoundError → arquivo não encontrado
        """
        return jsonify({'erro': f'Valor inválido enviado: {str(e)}'}), 400
    
    except Exception as e:
        """
        Exception → captura QUALQUER erro não tratado acima.
        Sempre coloque por último (é o mais genérico).
        
        Em produção:
        → Não exponha detalhes do erro (segurança)
        → Faça log do erro:
            import logging
            logging.error(f"Erro inesperado: {e}")
        → Retorne mensagem genérica ao cliente
        """
        print(f"ERRO INESPERADO: {e}") # Aparece no terminal durante desenvolvimento
        return jsonify({'erro': 'Erro interno. Tente novamente.'}), 500


# ══════════════════════════════════════════════
# PONTO DE ENTRADA DA APLICAÇÃO
# ══════════════════════════════════════════════

if __name__ == '__main__':
    """
    if __name__ == '__main__':
    ──────────────────────────
    Quando você executa: python app.py
      __name__ é '__main__'
      → Entra no if → app.run() é chamado ✓
    
    Quando outro arquivo faz: import app
      __name__ é 'app' (nome do arquivo)
      → NÃO entra no if → app.run() NÃO é chamado ✓
    
    Isso evita que o servidor inicie automaticamente ao importar.
    Padrão Python para scripts executáveis.
    """
    
# ══════════════════════════════════════════════
    # PONTO DE ENTRADA DA APLICAÇÃO
    # ══════════════════════════════════════════════
    app.run(
        # debug=True — MODO DE DESENVOLVIMENTO:
        #   ✓ Hot reload: reinicia automaticamente ao salvar o arquivo
        #   ✓ Debugger interativo no navegador em caso de erro
        #   ✓ Mensagens de erro detalhadas e logs no terminal
        #   ⚠️ NUNCA use debug=True em produção! Expõe informações sensíveis.
        debug=True,
        
        # host — qual interface de rede o servidor escuta:
        #   '127.0.0.1' (padrão/loopback): Só aceita conexões do próprio computador.
        #   '0.0.0.0': Aceita conexões de QUALQUER IP na rede (bom para testar no celular).
        host='127.0.0.1',
        
        # port — número da porta onde o servidor roda (padrão Flask: 5000).
        #   3000 -> React | 8000 -> Django/FastAPI | 5000 -> Flask
        port=5000
    )