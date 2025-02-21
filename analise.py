import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from graficos import (
    grafico_quantidade_registros_por_origem,
    grafico_tabela_disparos_leads,
    grafico_tabela,
    grafico_etapas_origem,
    grafico_cpf_por_convenio
)

# Função para normalizar os produtos
def normalizar_produto(nome_produto):
    mapeamento_produto = {
        "NOVO": ["novo", "credito novo", "negativos", 'sefaz', 'pmesp', 'spprev', "tomador", "super", "hubspot", "resgate", "carteira", "menor50", "menor 50", "virada"],
        "AMBOS CARTÕES": ["cartões", "cartoes", "benef & cartao", "cartões consignados", 'benefício e cartão'],
        "CARTÃO": ["cartão", "cartao", "consignado"],
        "BENEFICIO": ["benef", "beneficio", "complementar", 'temporario', 'tempo', 'temp', 'comlurb', 'Benefício'],
        "NQB": ["nqb"]
    }

    if pd.notna(nome_produto):
        nome_produto = nome_produto.lower().strip()
        for produto, nomes_possiveis in mapeamento_produto.items():
            if any(nome in nome_produto for nome in nomes_possiveis):
                return produto
    return "OUTROS"

# Função para carregar e processar dados
def carregar_dados(hubspot_file, disparos_file):
    hubspot_data = pd.read_csv(hubspot_file)
    disparos_data = pd.read_csv(disparos_file)

    # Tratamento HubSpot
    hubspot_data.columns = [
        'id', 'cliente', 'data_criado', 'cpf', 'telefone', 'convenio_completo',
        'origem', 'campanha', 'proprietario', 'produto', 'equipe', 'etapa',
        'motivo_perda', 'data_pago', 'comissao_total_projetada', 'valor_pago'
    ]
    hubspot_data = hubspot_data.loc[hubspot_data['equipe'].notna() & hubspot_data['equipe'].str.contains("Sales", case=False)]
    hubspot_data['data_criado'] = pd.to_datetime(hubspot_data['data_criado']).dt.date
    hubspot_data['convenio'] = hubspot_data['campanha'].str.split("_").str[0].str.upper()
    hubspot_data = hubspot_data.loc[~hubspot_data['origem'].isin(['HYPERFLOW', 'Tallos', 'DISPARO', 'Duplicação Negócio App'])]
    hubspot_data['origem'] = hubspot_data['origem'].replace("Whatsapp Grow", "RCS")
    hubspot_data['produto2'] = hubspot_data['produto'].apply(normalizar_produto)
    hubspot_data['data_criado'] = pd.to_datetime(hubspot_data['data_criado'])

    # Tratamento Disparos
    disparos_data['Data'] = pd.to_datetime(disparos_data['Data'], dayfirst=True).dt.date
    disparos_data['Convênio'] = disparos_data['Convênio'].str.replace(" ", "")
    disparos_data.columns = ['data_criado', 'convenio', 'produto2', 'quantidade', 'origem', 'gasto', 'mql', 'pagos', 'receita']
    disparos_data['data_criado'] = pd.to_datetime(disparos_data['data_criado'])

    return hubspot_data, disparos_data

# Função para exibir gráficos
def exibir_graficos(hubspot_data, disparos_data):
    st.plotly_chart(grafico_quantidade_registros_por_origem(hubspot_data))
    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(grafico_tabela_disparos_leads(hubspot_data, disparos_data))
    with col2:
        st.plotly_chart(grafico_tabela(hubspot_data, disparos_data))
    st.write("---")

    st.plotly_chart(grafico_etapas_origem(hubspot_data))
    st.write("---")

    st.plotly_chart(grafico_cpf_por_convenio(hubspot_data))

# Função principal
def main():
    st.title('Análise de Dados de HubSpot e Disparos')
    uploaded_files = st.file_uploader("Carregar arquivos", accept_multiple_files=True)

    st.sidebar.header("Filtros")
    
    if len(uploaded_files) == 2:
        # Verifica a ordem dos arquivos e carrega-os
        hubspot_file = [file for file in uploaded_files if 'hubspot' in file.name.lower()]
        disparos_file = [file for file in uploaded_files if 'disparos' in file.name.lower()]

        if hubspot_file and disparos_file:
            hubspot_data, disparos_data = carregar_dados(hubspot_file[0], disparos_file[0])
            
            # Obtém a data mínima e máxima de disparos
            min_date_disparo = disparos_data['data_criado'].min()
            max_date_disparo = disparos_data['data_criado'].max()

            # Filtro de data
            data_inicio = st.sidebar.date_input("Data Início", min_value=min_date_disparo, max_value=max_date_disparo, value=min_date_disparo)
            data_fim = st.sidebar.date_input("Data Fim", min_value=data_inicio, max_value=max_date_disparo, value=max_date_disparo)

            st.write(data_inicio,data_fim)

            hubspot_data = hubspot_data.loc[(hubspot_data['data_criado'] >= pd.Timestamp(data_inicio)) & (hubspot_data['data_criado'] <= pd.Timestamp(data_fim))]
            disparos_data = disparos_data.loc[(disparos_data['data_criado'] >= pd.Timestamp(data_inicio)) & (disparos_data['data_criado'] <= pd.Timestamp(data_fim))]

            exibir_graficos(hubspot_data, disparos_data)

if __name__ == "__main__":
    main()
