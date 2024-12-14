import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout='wide',page_title='StartUp Analysis')

df = pd.read_csv('startup_cleaned.csv')
df['date'] = pd.to_datetime(df['date'],errors='coerce')
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year

def load_overall_analysis():
    st.title('Overall Analysis')

    total = round(df['amount'].sum())
    # max amount infused in a startup
    max_funding = df.groupby('startup')['amount'].max().sort_values(ascending=False).head(1).values[0]
    # avg ticket size
    avg_funding = df.groupby('startup')['amount'].sum().mean()
    # total funded startups
    num_startups = df['startup'].nunique()

    col1,col2,col3,col4 = st.columns(4)
    with col1:
        st.metric('Total',str(total) + 'Cr')
    with col2:
        st.metric('Max', str(max_funding) + 'Cr')
    with col3:
        st.metric('Avg', str(round(avg_funding)) + ' Cr')

    with col4:
        st.metric('Funded Startups', num_startups)

    st.header('MoM graph')

    selected_option = st.selectbox('Select Type',['Total','Count'])
    if selected_option == 'Total':
        temp_df = df.groupby(['year', 'month'])['amount'].sum().reset_index()
    else:
        temp_df = df.groupby(['year', 'month'])['amount'].count().reset_index()

    temp_df['x_axis'] = temp_df['month'].astype('str') + '-' + temp_df['year'].astype('str')

    fig3, ax3 = plt.subplots(figsize=(8, 4))
    ax3.plot(temp_df['x_axis'], temp_df['amount'])

    st.pyplot(fig3)

    col1, col2 = st.columns(2)
    with col1:
        st.header('Top 10 Funded Company')
        all_funds = df.groupby('startup')['amount'].sum()
        top10_funded = all_funds.sort_values(ascending=False).head(10)
        fig, ax = plt.subplots()
        ax.bar(top10_funded.index, top10_funded.values)
        ax.tick_params(axis='x', labelrotation=90)
        ax.set_ylabel('Total Fund')
        ax.set_xlabel('Funded Company')
        st.pyplot(fig)

    with col2:
        st.header('Top 10 Funded Company - Year Wise ')
        df['year'] = pd.to_datetime(df['date']).dt.year
        top_startups_yearwise = (
            df.loc[df.groupby('year')['amount'].idxmax()]  # Select the row with the maximum 'amount' for each 'year'
                .reset_index(drop=True)
        )
        top_startups_yearwise[['year', 'startup', 'amount']].head()

        fig1, ax1 = plt.subplots(figsize=(12, 8))
        sns.barplot(x='amount', y='year', data=top_startups_yearwise, ax=ax1, orient='h', color='skyblue')
        for i, row in top_startups_yearwise.iterrows():
            ax1.text(row['amount'] + 0.1, i, row['startup'], color='black', va='center', fontsize=10)
        ax1.set_title('Year-wise Investment in Top Startups')
        ax1.set_xlabel('Investment Amount')
        ax1.set_ylabel('Year')
        st.pyplot(fig1)

    col1,col2 = st.columns(2)
    with col1:
        st.header('Top 10 Funded Sectors')
        df['vertical'] = df['vertical'].str.replace(r'\b[eE]-?[Cc]ommerce\b', 'E-commerce', regex=True)
        top_sectors = (df.groupby('vertical')['startup'].count().sort_values(ascending=False).head().reset_index())
        fig1, ax1 = plt.subplots()
        ax1.pie(
            top_sectors['startup'],
            labels=top_sectors['vertical'],
            autopct='%1.1f%%',
            startangle=90
        )
        ax1.axis('equal')
        st.pyplot(fig1)
    with col2:
        st.header('Top Funded City')
        top_startups_citywise = (
            df.groupby('city')
                .apply(lambda x: x.sort_values(by='amount', ascending=False).iloc[0])  # Top startup based on 'amount'
                .reset_index(drop=True)
        )

        top_startups_citywise = top_startups_citywise[['city', 'amount']].sort_values(by='amount', ascending=False).head()
        fig2, ax2 = plt.subplots()
        x = top_startups_citywise['city']
        y = top_startups_citywise['amount']

        # Plot the bar chart
        ax2.bar(x, y, color='skyblue')

        # Customize the plot
        ax2.tick_params(axis='x', labelrotation=90)  # Rotate x-axis labels for readability
        ax2.set_ylabel('Total Fund')
        ax2.set_xlabel('City')
        ax2.set_title('Top Funded Cities')
        st.pyplot(fig2)

def load_investor_details(investor):
    st.title(investor)

    # load the recent 5 investments of the investor
    last5_df = df[df['investors'].str.contains(investor)].head()[['date','startup','vertical','city','round','amount']]
    st.subheader('Most Recent Investments')
    st.dataframe(last5_df)

    col1, col2 = st.columns(2)
    with col1:
        # biggest investments
        big_series = df[df['investors'].str.contains(investor)].groupby('startup')['amount'].sum().sort_values(
            ascending=False).head()
        st.subheader('Biggest Investments')
        fig, ax = plt.subplots()
        ax.bar(big_series.index, big_series.values)

        st.pyplot(fig)

    with col2:
        verical_series = df[df['investors'].str.contains(investor)].groupby('vertical')['amount'].sum()

        st.subheader('Sectors invested in')
        fig1, ax1 = plt.subplots()
        ax1.pie(verical_series, labels=verical_series.index, autopct="%0.01f%%")

        st.pyplot(fig1)


    df['year'] = df['date'].dt.year
    year_series = df[df['investors'].str.contains(investor)].groupby('year')['amount'].sum()
    st.subheader('YoYo invested in')
    fig2, ax2 = plt.subplots()
    ax2.plot(year_series.index,year_series.values)

    st.pyplot(fig2)

    city_series = df[df['investors'].str.contains(investor)].groupby('city')['amount'].sum()
    st.subheader('City invested in')
    fig3, ax3 = plt.subplots()
    ax3.bar(city_series.index, city_series.values)
    ax3.set_xlabel('City')
    ax3.set_ylabel('Total Investment Amount')
    ax3.set_title('Investments by City')
    ax3.tick_params(axis='x', labelrotation=90)
    st.pyplot(fig3)

def load_startup_details(startup):
    st.title(startup)

    startup_data = df[df['startup'].str.contains(startup, case=False)]
    
    st.subheader('Startup Details')
    if not startup_data.empty:
        details = startup_data[[ 'vertical', 'subvertical', 'city', 'round']].iloc[0]
        st.write(f"**Industry:** {details['vertical']}")
        st.write(f"**Subindustry:** {details['subvertical']}")
        st.write(f"**Location:** {details['city']}")
        st.write(f"**Stage:** {details['round']}")

     # Display funding rounds
        st.subheader('Funding Rounds')
        funding_rounds = startup_data[['date', 'investors', 'round', 'amount']]
        st.dataframe(funding_rounds) 

    # Visualization: Funding over time
        st.subheader('Funding Over Time')
        funding_over_time = startup_data.groupby('date')['amount'].sum()
        fig, ax = plt.subplots()
        ax.plot(funding_over_time.index, funding_over_time.values, marker='o')
        ax.set_title('Funding Amount Over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel('Funding Amount')
        ax.tick_params(axis='x', labelrotation=45)
        st.pyplot(fig)    

    # Visualization: Top Investors
        st.subheader('Top Investors')
        top_investors = startup_data['investors'].value_counts().head(5)
        fig2, ax2 = plt.subplots()
        ax2.bar(top_investors.index, top_investors.values, color='skyblue')
        ax2.set_title('Top Investors')
        ax2.set_xlabel('Investors')
        ax2.set_ylabel('Number of Investments')
        ax2.tick_params(axis='x', labelrotation=45)
        st.pyplot(fig2)     
    
    else:
        st.write("No data available for this startup.")



st.sidebar.title('Startup Funding Analysis')

option = st.sidebar.selectbox('Select One', ['Overall Analysis', 'StartUp', 'Investor'])

if option == 'Overall Analysis':
    load_overall_analysis()

elif option == 'StartUp':
    select_startup = st.sidebar.selectbox('Select StartUp', sorted(df['startup'].unique().tolist()))
    btn1 = st.sidebar.button('Find StartUp Details')
    st.title('StartUp Analysis')
    if btn1:
        load_startup_details(select_startup)
else:
    selected_investor = st.sidebar.selectbox('Select StartUp', sorted(set(df['investors'].str.split(',').sum())))
    btn2 = st.sidebar.button('Find Investor Details')
    if btn2:
        load_investor_details(selected_investor)