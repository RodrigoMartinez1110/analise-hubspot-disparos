import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

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

# Função principal do Streamlit
def main():
    st.title('Análise de Dados de HubSpot e Disparos')

    # Upload de arquivos
    uploaded_files = st.file_uploader("Carregar arquivos", accept_multiple_files=True)
    if len(uploaded_files) == 2:
        hubspot_file = uploaded_files[0]
        disparos_file = uploaded_files[1]

        # Leitura dos arquivos CSV
        hubspot_data = pd.read_csv(hubspot_file)
        disparos_data = pd.read_csv(disparos_file)

        # Tratamento e normalização dos dados
        hubspot_data.columns = ['id', 'cliente', 'data_criado', 'cpf', 'telefone', 'convenio_completo',
                                'origem', 'campanha', 'proprietario', 'produto', 'equipe', 'etapa',
                                'motivo_perda', 'data_pago', 'comissao_total_projetada', 'valor_pago']

        hubspot_data = hubspot_data.loc[~hubspot_data['origem'].isin(['HYPERFLOW', 'Tallos', 'DISPARO'])]
        hubspot_data['data_criado'] = pd.to_datetime(hubspot_data['data_criado']).dt.date
        hubspot_data['convenio'] = hubspot_data['campanha'].str.split("_").str[0].str.upper()

        disparos_data['Convênio'] = disparos_data['Convênio'].str.replace(" ","")
        disparos_data['Data'] = pd.to_datetime(disparos_data['Data'], dayfirst=True).dt.date

        hubspot_data['data_criado'] = pd.to_datetime(hubspot_data['data_criado'])  # Garante que a coluna é datetime64
        hubspot_data = hubspot_data.loc[hubspot_data['data_criado'] > pd.Timestamp("2025-02-10")]
        hubspot_data['origem'] = hubspot_data['origem'].replace("Whatsapp Grow", "RCS")

        # Normalizando o produto
        hubspot_data["produto2"] = hubspot_data["produto"].apply(normalizar_produto)
        
        disparos_data.columns = ['data_criado', 'convenio', 'produto2', 'quantidade', 'origem', 'gasto', 'mql', 'pagos', 'receita']
        disparos_data['data_criado'] = pd.to_datetime(disparos_data['data_criado'])  # Converte para datetime64
        disparos_data = disparos_data.loc[disparos_data['data_criado'] > pd.Timestamp("2025-02-10")]

        # Gráfico 1
        dados_agrupados = hubspot_data.groupby(["data_criado", "origem"])['cpf'].size().reset_index(name='Quantidade')
        fig1 = px.bar(dados_agrupados, x="data_criado", y="Quantidade", color="origem", title="Quantidade de Registros por Data de Criação e Origem", text="Quantidade", labels={"criado": "Data de Criação", "Quantidade": "Quantidade de Registros", "origem": "Origem"}, barmode="group")
        fig1.update_layout(xaxis_title="Data de Criação", yaxis_title="Quantidade de Registros", legend_title="Origem", width=1400, height=700, template="plotly_dark", margin=dict(l=40, r=40, t=60, b=40))
        st.plotly_chart(fig1)

        # Gráfico 2
        data = hubspot_data.groupby(['data_criado', 'convenio', 'produto2', 'origem'])['id'].size().reset_index(name='leads')
        merged_data = data.merge(disparos_data, on=['data_criado', 'convenio', 'produto2', 'origem'], how='inner')
        df_grouped = merged_data.groupby(['convenio', 'produto2'])[['quantidade', 'leads']].sum().reset_index()
        df_grouped['proporcao %'] = ((df_grouped['leads'] / df_grouped['quantidade']) * 100).round(2)
        df_grouped = df_grouped.sort_values(by='proporcao %', ascending=False)
        fig2 = go.Figure(data=[go.Table(header=dict(values=["<b>Convênio</b>", "<b>Produto</b>", "<b>Quantidade Disparada</b>", "<b>Leads Gerados</b>", "<b>Proporção %</b>"], fill_color='lightblue', align='center', font=dict(size=14, color='black'), height=40), cells=dict(values=[df_grouped['convenio'], df_grouped['produto2'], df_grouped['quantidade'], df_grouped['leads'], df_grouped['proporcao %'].round(2)], fill_color=[['white', '#f2f2f2'] * (len(df_grouped) // 2)], align='center', font=dict(size=18, color='black'), height=30))])
        fig2.update_layout(title="<b>Tabela de Disparos e Leads por Convênio e Produto</b>", height=1000)
        st.plotly_chart(fig2)

        # Gráfico 3
        hubspot_data_semperda = hubspot_data.loc[hubspot_data['etapa'] != 'PERDA']
        grouped_data = hubspot_data_semperda.groupby(['etapa', 'origem'])['cpf'].size().reset_index(name='Quantidade')
        fig3 = px.bar(grouped_data, x='etapa', y='Quantidade', color='origem', barmode='group', title='Distribuição de CPF por Etapa e Origem', labels={'etapa': 'Etapa', 'Quantidade': 'Quantidade de CPFs', 'origem': 'Origem'})
        fig3.update_layout(xaxis=dict(title='Etapa', tickangle=45), yaxis=dict(title='Quantidade de CPFs'), barmode='group', template='plotly_dark', height=800)
        st.plotly_chart(fig3)

        # Gráfico 4
        hubspot_data_perda = hubspot_data.loc[hubspot_data['etapa'] != 'PERDA']
        grouped_data = hubspot_data_perda.groupby(['etapa', 'origem'])['cpf'].size().reset_index(name='Quantidade')
        fig4 = px.bar(grouped_data, x='etapa', y='Quantidade', color='origem', barmode='group', title='Distribuição de CPF por Etapa e Origem', labels={'etapa': 'Etapa', 'Quantidade': 'Quantidade de CPFs', 'origem': 'Origem'})
        fig4.update_layout(xaxis=dict(title='Etapa', tickangle=45, tickfont=dict(size=14)), yaxis=dict(title='Quantidade de CPFs'), barmode='group', template='plotly_dark', height=800)
        st.plotly_chart(fig4)

        # Gráfico 5
        grouped_data = hubspot_data.groupby(['convenio', 'origem'])['cpf'].size().reset_index(name='Quantidade')
        fig5 = px.bar(grouped_data, y='convenio', x='Quantidade', color='origem', orientation='h', title='Quantidade de CPFs por Convênio e Origem', labels={'convenio': 'Convênio', 'Quantidade': 'Quantidade de CPFs', 'origem': 'Origem'})
        fig5.update_layout(yaxis=dict(title='Convênio', tickfont=dict(size=18), automargin=True), xaxis=dict(title='Quantidade de CPFs', tickfont=dict(size=12)), template='plotly_dark', height=1200)
        st.plotly_chart(fig5)

if __name__ == "__main__":
    main()
