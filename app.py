from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

INVESTIMENTOS = {
    'poupanca': {
        'nome': 'Poupança',
        'taxa_anual': 6.17
    },
    'cdb': {
        'nome': 'CDB',
        'taxa_anual': 12.00
    },
    'tesouro': {
        'nome': 'Tesouro Selic',
        'taxa_anual': 12.15
    },
    'lci': {
        'nome': 'LCI / LCA',
        'taxa_anual': 10.80
    },
    'fundo': {
        'nome': 'Fundo Multimercado',
        'taxa_anual': 14.00
    }
}


def calcular_juros_compostos(capital, taxa_anual_percentual, anos):
    taxa_decimal = taxa_anual_percentual / 100
    montante = capital * (1 + taxa_decimal) ** anos
    lucro = montante - capital
    rendimento_percentual = ((montante / capital) - 1) * 100
    return montante, lucro, rendimento_percentual


def formatar_moeda_br(valor):
    formatado = f"{valor:,.2f}"
    formatado = formatado.replace(',', 'X').replace('.', ',').replace('X', '.')
    return formatado


@app.route('/')
def pagina_inicial():
    return render_template('simulador_investimentos.html')


@app.route('/calcular', methods=['POST'])
def calcular():
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({'erro': 'Nenhum dado recebido'}), 400

        valor = dados.get('valor')
        periodo = dados.get('periodo')
        tipo = dados.get('tipo')

        if not all([valor is not None, periodo, tipo]):
            return jsonify({'erro': 'Campos obrigatórios ausentes: valor, periodo, tipo'}), 400

        if tipo not in INVESTIMENTOS:
            return jsonify({'erro': f'Investimento "{tipo}" não encontrado'}), 400

        valor = float(valor)
        periodo = int(periodo)

        if valor <= 0:
            return jsonify({'erro': 'O valor deve ser maior que R$ 0'}), 400

        if not (1 <= periodo <= 50):
            return jsonify({'erro': 'Período deve ser entre 1 e 50 anos'}), 400

        investimento = INVESTIMENTOS[tipo]
        taxa = investimento['taxa_anual']

        montante, lucro, rendimento_pct = calcular_juros_compostos(
            capital=valor,
            taxa_anual_percentual=taxa,
            anos=periodo
        )

        resposta = {
            'valor_inicial': formatar_moeda_br(valor),
            'valor_final': formatar_moeda_br(montante),
            'lucro': formatar_moeda_br(lucro),
            'taxa': taxa,
            'periodo': periodo,
            'nome_investimento': investimento['nome'],
            'rendimento_percentual': f"{rendimento_pct:.2f}"
        }

        return jsonify(resposta)

    except ValueError as e:
        return jsonify({'erro': f'Valor inválido: {str(e)}'}), 400

    except Exception as e:
        print(f"ERRO: {e}")
        return jsonify({'erro': 'Erro interno. Tente novamente.'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
    