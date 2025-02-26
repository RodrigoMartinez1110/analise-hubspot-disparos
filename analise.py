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

# Função para exibir gráficos em containers
def exibir_graficos(hubspot_data, disparos_data, graficos_selecionados):
    # Criar containers vazios para os gráficos
    grafico_container = st.container()

    with grafico_container:
        if "Quantidade de Registros por Origem" in graficos_selecionados:
            st.write('---')
            with st.container():  # Adiciona um container para este gráfico
                st.plotly_chart(grafico_quantidade_registros_por_origem(hubspot_data))
                st.write('---')

        # Organizar "Tabela de Disparos e Leads" e "Tabela Geral" lado a lado
        if "Tabela de Disparos e Leads" in graficos_selecionados or "Tabela Geral" in graficos_selecionados:
            with st.container():  # Adiciona um container para as tabelas
                col1, col2 = st.columns(2)
                with col1:
                    if "Tabela de Disparos e Leads" in graficos_selecionados:
                        st.plotly_chart(grafico_tabela_disparos_leads(hubspot_data, disparos_data))

                with col2:
                    if "Tabela de Disparos e Leads" in graficos_selecionados:
                        st.plotly_chart(grafico_tabela(hubspot_data, disparos_data))
                st.write('---')

        if "Etapas por Origem" in graficos_selecionados:
            with st.container():  # Adiciona um container para este gráfico
                st.plotly_chart(grafico_etapas_origem(hubspot_data))
                st.write('---')

        if "Quantidade de CPFs por Convênio" in graficos_selecionados:
            with st.container():  # Adiciona um container para este gráfico
                st.plotly_chart(grafico_cpf_por_convenio(hubspot_data))
                st.write('---')

# Função principal
def main():
    st.title('Análise de Dados de HubSpot e Disparos')
    
    # Adicionar um espaçamento entre o conteúdo e o file uploader
    st.sidebar.header("Filtros")

    # Carregar arquivos
    uploaded_files = st.sidebar.file_uploader("Carregar arquivos", accept_multiple_files=True, key="file_uploader_1", label_visibility='hidden')
    
    # Mostrar arquivos carregados
    if uploaded_files:
        st.sidebar.write("Arquivos carregados!")

    st.sidebar.write("---")

    if len(uploaded_files) == 2:
        # Verifica a ordem dos arquivos e carrega-os
        hubspot_file = [file for file in uploaded_files if 'hubspot' in file.name.lower()]
        disparos_file = [file for file in uploaded_files if 'disparos' in file.name.lower()]

        if hubspot_file and disparos_file:
            hubspot_data, disparos_data = carregar_dados(hubspot_file[0], disparos_file[0])
            
            # Obtém a data mínima e máxima de disparos
            min_date_disparo = disparos_data['data_criado'].min().date()
            max_date_disparo = disparos_data['data_criado'].max().date()

            # Filtro de data com slider
            data_inicio, data_fim = st.sidebar.slider(
                "Selecione o período",
                min_value=min_date_disparo,
                max_value=max_date_disparo,
                value=(min_date_disparo, max_date_disparo),
                format="DD/MM/YYYY"
            )

            st.write(f"Período selecionado: {data_inicio} até {data_fim}")

            # Filtra os dados conforme o intervalo selecionado
            hubspot_data = hubspot_data.loc[
                (hubspot_data['data_criado'].dt.date >= data_inicio) & 
                (hubspot_data['data_criado'].dt.date <= data_fim)
            ]
            disparos_data = disparos_data.loc[
                (disparos_data['data_criado'].dt.date >= data_inicio) & 
                (disparos_data['data_criado'].dt.date <= data_fim)
            ]

            st.sidebar.write("---")


            graficos_selecionados = st.sidebar.multiselect(
                "Selecione os gráficos", 
                [
                    "Quantidade de Registros por Origem", 
                    "Tabela de Disparos e Leads", 
                    "Etapas por Origem", 
                    "Quantidade de CPFs por Convênio"
                ], 
                default=[
                    "Quantidade de Registros por Origem", 
                    "Tabela de Disparos e Leads",
                    "Etapas por Origem", 
                    "Quantidade de CPFs por Convênio"
                ]
            )
            

            st.sidebar.write("---")

            # Filtra os dados pelos convênios  
            convenios = disparos_data['convenio'].unique().tolist()
            convenios = ['Todos'] + convenios  # Adiciona a opção "Todos"
            convenio_selecionado = st.sidebar.multiselect(
                "Selecione os convênios", convenios, default='Todos'
            )

            # Se "Todos" for selecionado, remove o filtro
            if 'Todos' in convenio_selecionado:
                convenio_selecionado = disparos_data['convenio'].unique().tolist()

            hubspot_data = hubspot_data.loc[hubspot_data['convenio'].isin(convenio_selecionado)]
            disparos_data = disparos_data.loc[disparos_data['convenio'].isin(convenio_selecionado)]

            st.sidebar.write("---")

            # Filtra os dados pelos produtos
            produtos = disparos_data['produto2'].unique().tolist()
            produtos = ['Todos'] + produtos  # Adiciona a opção "Todos"
            produto_selecionado = st.sidebar.multiselect(
                "Selecione os produtos", produtos, default='Todos'
            )

            # Se "Todos" for selecionado, remove o filtro
            if 'Todos' in produto_selecionado:
                produto_selecionado = disparos_data['produto2'].unique().tolist()

            hubspot_data = hubspot_data.loc[hubspot_data['produto2'].isin(produto_selecionado)]
            disparos_data = disparos_data.loc[disparos_data['produto2'].isin(produto_selecionado)]

            st.sidebar.write("---")

            # Filtra os dados pelos produtos
            etapas = hubspot_data['etapa'].unique().tolist()
            etapas = ['Todos'] + etapas  # Adiciona a opção "Todos"
            etapa_selecionado = st.sidebar.multiselect(
                "Selecione as etapas", etapas, default='Todos'
            )

            # Se "Todos" for selecionado, remove o filtro
            if 'Todos' in etapa_selecionado:
                etapa_selecionado = hubspot_data['etapa'].unique().tolist()
            hubspot_data = hubspot_data.loc[hubspot_data['etapa'].isin(etapa_selecionado)]


            exibir_graficos(hubspot_data, disparos_data, graficos_selecionados)

            

if __name__ == "__main__":
    main()