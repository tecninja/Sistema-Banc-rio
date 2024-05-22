import streamlit as st
from datetime import datetime
import pytz
import pandas as pd

class Sistema:
    """
    Classe que representa o sistema bancário e encapsula as informações e operações da conta.

    Atributos:
        saldo (float): Saldo atual da conta.
        limite_saques (int): Limite máximo de saques por dia.
        limite_valor_saque (float): Limite máximo de valor por saque.
        limite_deposito (float): Limite máximo de valor por depósito.
        transacoes (list[dict]): Lista de registros de transações.

    Métodos:
        deposito(valor: float) -> tuple[str, bool]:
            Realiza um depósito na conta.

        saque(valor: float) -> tuple[str, bool]:
            Realiza um saque na conta.

        extrato(cliente_id: int) -> str:
            Exibe o extrato da conta do cliente.
    """
    0
    
    def __init__(self) -> None:
        """
        Construtor da classe Sistema.
        
        Inicializa os atributos da conta.
        """
        self.saldo = 0
        self.limite_saques = 3
        self.limite_valor_saque = 500
        self.limite_deposito = 2000
        self.transacoes = []
    
    def deposito(self, valor: float):
        """
        Realiza um depósito na conta.

        Argumentos:
            valor (float): Valor a ser depositado.

        Retorna:
            tuple[str, bool]: Mensagem de resposta e status da operação (True para sucesso, False para falha).
        """
        try:
            if valor <= 0:
                return f"Não é possível depositar R$ {valor:.2f}!", False
            elif valor > self.limite_deposito:
                return f"Valor a ser depositado excede limites! \
                    Neste canal o valor máximo por depósito é de: R$ {self.limite_deposito:.2f}", False
            else:
                valor_anterior = self.saldo
                self.saldo += valor
                self.transacoes.append({
                    "data":datetime.now(tz=pytz.timezone("America/Sao_Paulo")),
                    "acao":"deposito",
                    "valor":valor,
                    "saldo_anterior": valor_anterior,
                    "saldo": self.saldo
                })
                st.session_state.saldo = self.saldo
        except Exception as e:
            return f"Erro no Depósito! {e}", False
        else:
            return f"""
SISTEMA BANCÁRIO\n
{"- " * 20}
Depósito efetuado com sucesso!\n
Valor depositado: R$ {valor:.2f}\n
Saldo em conta: R$ {st.session_state.saldo:.2f}
                       """, True
        
        
    def saque(self, valor: float):
        """
        Realiza um saque na conta.

        Argumentos:
            valor (float): Valor a ser sacado.

        Retorna:
            tuple[str, bool]: Mensagem de resposta e status da operação (True para sucesso, False para falha).
        """
        try:
            df = self.extrato()
            if not df.empty:
                tem_saque = df.acao.unique().tolist()
                if 'saque' not in tem_saque:
                    qtd_saques = 0
                else:
                    hoje = datetime.now().strftime("%Y-%m-%d")
                    df.data = df.data.apply(lambda x: x.strftime("%Y-%m-%d"))
                    df = df[df.data == hoje]
                    df = df.groupby(df[df.acao == 'saque'].data)['acao'].count().values
                    qtd_saques = df[0]
            else:
                qtd_saques = 0

            if qtd_saques >= self.limite_saques:
                return "Você atingiu o seu limite máximo de saques hoje", False
            elif valor <= 0:
                return f"Não é possível sacar R$ {valor:.2f}!", False
            elif valor > self.saldo:
                return "Saldo insuficiente para o valor solicitado!", False
            elif valor > self.limite_valor_saque:
                return "Saque superior ao limite deste canal.\nLimite do canal R$ {:.2f}".format(self.limite_valor_saque), False
            else:
                valor_anterior = self.saldo
                self.saldo -= valor
                self.transacoes.append({
                    "data":datetime.now(tz=pytz.timezone("America/Sao_Paulo")),
                    "acao":"saque",
                    "valor":valor,
                    "saldo_anterior": valor_anterior,
                    "saldo": self.saldo
                })
                st.session_state.saldo = self.saldo
        except Exception as e:
            return f"Erro no Saque! {e}", False
        else: 
            return f"""
SISTEMA BANCÁRIO\n
{"-" * 20}\n
Saque efetuado com sucesso!\n
Valor sacado: R$ {valor:.2f}\n
Saldo em conta: R$ {st.session_state.saldo:.2f}
                       """, True
        
    def extrato(self):
        """
        Gera um DataFrame contendo o extrato (histórico de transações) da conta.

        Retorna:
            pd.DataFrame: DataFrame contendo as transações da conta, 
                          incluindo data, ação (depósito ou saque), valor, 
                          saldo anterior e saldo após a transação.
        """
        df = pd.DataFrame(self.transacoes)
        if not df.empty:
            df.valor = list(map( lambda x: f'R$ {x:,.2f}', df.valor))
            df.saldo_anterior = list(map( lambda x: f'R$ {x:,.2f}', df.saldo_anterior))
            df.saldo = list(map( lambda x: f'R$ {x:,.2f}', df.saldo))
        return df
        
    
st.title("Internet Banking")
st.divider()

banco = Sistema()


######################################################## Gravação dos dados na memória #############################################
if 'saldo' not in st.session_state:
    st.session_state.saldo = banco.saldo
else:
    banco.saldo = st.session_state.saldo
    
if 'transacoes' not in st.session_state:
    st.session_state.transacoes = banco.transacoes
else:
    banco.transacoes = st.session_state.transacoes
####################################################################################################################################

opcoes = ["Saque",'Depósito','Extrato']

acao = st.selectbox(options=opcoes, label="Selecione uma Ação")
   
match acao:
    case 'Saque': 
        st.divider()
        st.write("### Sistema de Saque", unsafe_allow_html=True)
        valor = st.number_input("Informe o valor a ser sacado: ", min_value=0)
        resposta = st.empty()
        if st.button("Sacar"):
            response = banco.saque(valor=valor)
            if response[1]:
                resposta.success(response[0])
            else:
                resposta.error(response[0])
    
        
    case 'Depósito':
        st.divider()
        st.write("### Sistema de Depósito")
        valor = st.number_input("Informe o valor a ser depositado: ")
        resposta = st.empty()
        if st.button("Depositar"):
            response = banco.deposito(valor=valor)
            if response[1]:
                resposta.success(response[0])
            else:
                resposta.error(response[0])
        

                
    case 'Extrato':
        st.divider()
        st.write("### Sistema de Extrato")
        st.divider()
        st.write("#### Saldo em conta R$ {:,.2f}".format(st.session_state.saldo), unsafe_allow_html=True)
        st.divider()
        st.write("#### Transações")
        extrato = banco.extrato()
        if not extrato.empty:
            st.table(extrato)
        else:
            st.info("Você não tem transações registradas")
    
