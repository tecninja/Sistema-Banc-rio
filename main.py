import streamlit as st
from datetime import datetime
import pytz
import pandas as pd

class Sistema:
    
    
    def __init__(self) -> None:
        self.saldo = 0
        self.limite_saques = 3
        self.limite_valor_saque = 500
        self.limite_deposito = 2000
        self.transacoes = []
    
    def deposito(self, valor: float):
        try:
            if valor == 0:
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
        try:
            if valor == 0:
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
        
    def extrato(cliente_id: int):
        ...
    
    
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
        valor = st.number_input("Informe o valor a ser sacado: ")
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
        df = pd.DataFrame(st.session_state.transacoes)
        if not df.empty:
            df.valor = list(map( lambda x: f'R$ {x:,.2f}', df.valor))
            df.saldo_anterior = list(map( lambda x: f'R$ {x:,.2f}', df.saldo_anterior))
            df.saldo = list(map( lambda x: f'R$ {x:,.2f}', df.saldo))
            st.table(df)
        else:
            st.info("Você não tem transações registradas")
    
