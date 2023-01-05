#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import numpy as np
from shroomdk import ShroomDK
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.ticker as ticker
import numpy as np
import altair as alt
sdk = ShroomDK("679043b4-298f-4b7f-9394-54d64db46007")


# In[2]:


import time
my_bar = st.progress(0)

for percent_complete in range(100):
    time.sleep(0.1)
    my_bar.progress(percent_complete + 1)


# In[4]:


st.title('Ethereum NFTs in 2022')
st.write('')
st.markdown('**NFT** stands for _Non-Fungible Token_, a non-fungible token. Tokens are units of value that are assigned to a business model, such as cryptocurrencies. NFTs are closely related to cryptocurrencies, at least technologically, although they are opposites, since a Bitcoin is a fungible good, and an NFT is a non-fungible good, but in essence, they are like the two sides of a technological coin.')
st.markdown('They are powered by blockchain technology. This is the same technology as cryptocurrencies, which operate through a decentralised computer network, with blocks or nodes linked and secured using cryptography. Each block links to a previous block, as well as a date and transaction data, and by design they are resistant to data modification.')
st.markdown('NFTs are assigned a kind of digital certificate of authenticity, a set of metadata that cannot be modified. This metadata guarantees their authenticity, records the starting value and any purchases or transactions that have been made, as well as their author. This means that if you buy digital content tokenised with NFT, there will always be a record of the first value it had, and how much you bought it for. It is like when you buy a painting and it keeps track of where it moves.')
st.markdown('In general, most tokens or NFTs are based on the standards of the **Ethereum** network and its blockchain. Because they use a well-known and popular technology, it is easy to trade them to buy and sell them using certain wallets that also work with Ethereum. However, we are talking about single works, so there is no active buying and selling as in digital currencies.')
st.write('This dashboard comprehens the following sections:')
st.markdown('1. NFTs activity')
st.markdown('2. Mints')
st.markdown('3. Sales')
st.write('')
st.subheader('1. NFTs activity during this year')
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the NFTs activity during this year. More specifically, we will analyze the following data:')
st.markdown('● Total number of sales/mints')
st.markdown('● NFT volume in 2022')
st.markdown('● NFT distribution of sales by their volume')
st.markdown('● Total number of sales/mints by month')
st.markdown('● NFT volume by month')
st.write('')

sql="""
select 'Mints' as type,
count (distinct tx_hash) as TX_Count,
count (distinct nft_address) as Projects_Count,
count (distinct tokenid) as Tokens_Count,
count (distinct nft_to_address) as Users_Count,
sum (mint_price_usd) as Total_Volume,
avg (mint_price_usd) as Average_Volume,
median (mint_price_usd) as Median_Volume,
max (mint_price_usd) as Maximum_Volume
from ethereum.core.ez_nft_mints
where block_Timestamp::date >= '2022-01-01' and block_timestamp::date < '2023-01-01'

union all

select 'Secondary Sales' as type,
count (distinct tx_hash) as TX_Count,
count (distinct nft_address) as Projects_count,
count (distinct tokenid) as Tokens_Count,
count (distinct buyer_address) as Users_Count,
sum (price_usd) as Total_Volume,
avg (price_usd) as Average_Volume,
median (price_usd) as Median_Volume,
max (price_usd) as Maximum_Volume
from ethereum.core.ez_nft_sales
where block_Timestamp::date >= '2022-01-01' and block_timestamp::date < '2023-01-01'

"""

st.experimental_memo(ttl=50000)
def memory(code):
    data=sdk.query(code)
    return data

results = memory(sql)
df = pd.DataFrame(results.records)
df.info()
    
sql2="""
select case when price_usd < 100 then 'Less Than $100'
when price_usd >= 100 and price_usd < 1000 then '$100 - $1000'
when price_usd >= 1000 and price_usd < 10000 then '$1000 - $10000'
when price_usd >= 10000 and price_usd < 100000 then '$10000 - $100000'
when price_usd >= 100000 and price_usd < 1000000 then '$100000 - $1000000'
when price_usd >= 1000000 and price_usd < 10000000 then '$1000000 - $10000000'
else 'More Than $10000000' end as type,
count (distinct tx_hash) as tx_count
from ethereum.core.ez_nft_sales
where price_usd > 0
and block_Timestamp::date >= '2022-01-01' and block_timestamp::date < '2023-01-01'
group by 1
order by 2 desc

"""
             
results2 = memory(sql2)
df2 = pd.DataFrame(results2.records)
df2.info()
    
    
sql3="""
select 'Mints' as type,
date_trunc (month,block_timestamp) as date,
case when date = '2022-01-01 00:00:00.000' then '1.January'
when date = '2022-02-01 00:00:00.000' then '2.February'
when date = '2022-03-01 00:00:00.000' then '3.March'
when date = '2022-04-01 00:00:00.000' then '4.April'
when date = '2022-05-01 00:00:00.000' then '5.May'
when date = '2022-06-01 00:00:00.000' then '6.June'
when date = '2022-07-01 00:00:00.000' then '7.July'
when date = '2022-08-01 00:00:00.000' then '8.August'
when date = '2022-09-01 00:00:00.000' then '9.September'
when date = '2022-10-01 00:00:00.000' then '10.October'
when date = '2022-11-01 00:00:00.000' then '11.November'
when date = '2022-12-01 00:00:00.000' then '12.December' end as month_name,
count (distinct tx_hash) as TX_Count,
count (distinct nft_address) as Projects_Count,
count (distinct tokenid) as Tokens_Count,
count (distinct nft_to_address) as Users_Count,
sum (mint_price_usd) as Total_Volume,
avg (mint_price_usd) as Average_Volume,
median (mint_price_usd) as Median_Volume,
max (mint_price_usd) as Maximum_Volume,
sum (tx_count) over (order by date) as Cumulative_TX_Count,
sum (total_volume) over (order by date) as Cumulative_Volume
from ethereum.core.ez_nft_mints
where block_Timestamp::date >= '2022-01-01' and block_timestamp::date < '2023-01-01'
group by 1,2,3

union all

select 'Secondary Sales' as type,
date_trunc (month,block_timestamp) as date,
case when date = '2022-01-01 00:00:00.000' then '1.January'
when date = '2022-02-01 00:00:00.000' then '2.February'
when date = '2022-03-01 00:00:00.000' then '3.March'
when date = '2022-04-01 00:00:00.000' then '4.April'
when date = '2022-05-01 00:00:00.000' then '5.May'
when date = '2022-06-01 00:00:00.000' then '6.June'
when date = '2022-07-01 00:00:00.000' then '7.July'
when date = '2022-08-01 00:00:00.000' then '8.August'
when date = '2022-09-01 00:00:00.000' then '9.September'
when date = '2022-10-01 00:00:00.000' then '10.October'
when date = '2022-11-01 00:00:00.000' then '11.November'
when date = '2022-12-01 00:00:00.000' then '12.December' end as month_name,
count (distinct tx_hash) as TX_Count,
count (distinct nft_address) as Projects_count,
count (distinct tokenid) as Tokens_Count,
count (distinct buyer_address) as Users_Count,
sum (price_usd) as Total_Volume,
avg (price_usd) as Average_Volume,
median (price_usd) as Median_Volume,
max (price_usd) as Maximum_Volume,
sum (tx_count) over (order by date) as Cumulative_TX_Count,
sum (total_volume) over (order by date) as Cumulative_Volume
from ethereum.core.ez_nft_sales
where block_Timestamp::date >= '2022-01-01' and block_timestamp::date < '2023-01-01'
group by 1,2,3

"""

results3 = memory(sql3)
df3 = pd.DataFrame(results3.records)
df3.info()

with st.expander("Check the analysis"):
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='type:N', y='tx_count:Q',color='type')
        .properties(title='Mints and sales',width=600))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='type:N', y='users_count:Q',color='type')
        .properties(title='Minters and sellers',width=600))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='date:N', y='tx_count:Q',color='type')
        .properties(title='Mints and sales over time',width=600))
    
    col2.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='date:N', y='users_count:Q',color='type')
        .properties(title='Minters and sellers over time',width=600))
    
    col3,col4=st.columns(2)
    
    with col3:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='type:N', y='total_volume:Q',color='type')
        .properties(title='Volume minted and sold',width=600))
    
    col4.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='type:N', y='median_volume:Q',color='type')
        .properties(title='Median volume minted and sold',width=600))
    
    with col3:
        st.altair_chart(alt.Chart(df3)
        .mark_area()
        .encode(x='date:N', y='total_volume:Q',color='type')
        .properties(title='Volume minted and sold over time',width=600))
    
    col4.altair_chart(alt.Chart(df3)
        .mark_line()
        .encode(x='date:N', y='median_volume:Q',color='type')
        .properties(title='Median volume minted and sold over time',width=600))
    
    st.altair_chart(alt.Chart(df2)
        .mark_bar()
        .encode(x='type:N', y='tx_count:Q',color='type')
        .properties(title='Distribution of sales by volume',width=600))


# In[8]:


st.subheader("2. NFT mints")
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the NFTs mints. More specifically, we will analyze the following data:')
st.markdown('● NFT project with the most total mint volume')
st.markdown('● NFT project with the largest mint volume')



sql="""
    select nft_address,
case when nft_address = '0xc36442b4a4522e871399cd717abdd847ab11fe88' then 'Uniswap V3: Positions NFT (UNI-V3-POS)'
when nft_address = '0x58a3c68e2d3aaf316239c003779f71acb870ee47' then 'Curve SynthSwap (CRV/SS)'
when nft_address = '0x218615c78104e16b5f17764d35b905b638fe4a92' then 'Omni Derivative Token DOODLE (nDOODLE)'
when nft_address = '0xa2caea05ff7b98f10ad5ddc837f15905f33feb60' then 'WMasterChef'
when nft_address = '0x80825c93a9e7c9fbf05ee32d629636e4bfb2c9fe' then 'Team.Finance Lock (TFL)'
when nft_address = '0x25cd67e2dfec471acd3cdd3b22ccf7147596dd8b' then 'Metroverse Blackout City Block (METROBLOCk)'
when nft_address = '0x5660e206496808f7b5cdb8c56a696a96ae5e9b23' then 'NFTfi Promissory Note (PNNFI)'
when nft_address = '0x06799a1e4792001aa9114f0012b9650ca28059a3' then 'Uniswap V2: Positions NFT (UNI-V2-POS)'
else coalesce (initcap(project_name),initcap(address_name),initcap(nft_address)) end as Project_Title,
sum (mint_price_usd) as Total_Volume,
avg (mint_price_usd) as Average_Volume,
median (mint_price_usd) as Median_Volume,
max (mint_price_usd) as Maximum_Volume
from ethereum.core.ez_nft_mints t1 left outer join ethereum.core.dim_labels t2 on t1.nft_address = t2.address
where mint_price_usd > 0
and block_Timestamp::date >= '2022-01-01' and block_timestamp::date < '2023-01-01'
group by 1,2
order by 3 DESC
limit 10
    """

sql2="""
select nft_address,
case when nft_address = '0xc36442b4a4522e871399cd717abdd847ab11fe88' then 'Uniswap V3: Positions NFT (UNI-V3-POS)'
when nft_address = '0x58a3c68e2d3aaf316239c003779f71acb870ee47' then 'Curve SynthSwap (CRV/SS)'
when nft_address = '0x218615c78104e16b5f17764d35b905b638fe4a92' then 'Omni Derivative Token DOODLE (nDOODLE)'
when nft_address = '0xa2caea05ff7b98f10ad5ddc837f15905f33feb60' then 'WMasterChef'
when nft_address = '0x80825c93a9e7c9fbf05ee32d629636e4bfb2c9fe' then 'Team.Finance Lock (TFL)'
when nft_address = '0x25cd67e2dfec471acd3cdd3b22ccf7147596dd8b' then 'Metroverse Blackout City Block (METROBLOCk)'
when nft_address = '0x5660e206496808f7b5cdb8c56a696a96ae5e9b23' then 'NFTfi Promissory Note (PNNFI)'
when nft_address = '0x06799a1e4792001aa9114f0012b9650ca28059a3' then 'Uniswap V2: Positions NFT (UNI-V2-POS)'
when nft_address = '0xdbe09a801e19c6568c515b0e24cc2337442d4f41' then 'WireNode'
when nft_address = '0x2b1c7b41f6a8f2b2bc45c3233a5d5fb3cd6dc9a8' then 'KyberSwap v2 NFT Positions Manager (KS2-NPM)'
when nft_address = '0x4757f744ec0cf2e3500dc655f55100c943a59cbb' then 'short Squeeth (sSQU)'
when nft_address = '0x5663e3e096f1743e77b8f71b5de0cf9dfd058523' then 'Pooly - Judge (POOLY3)'
when nft_address = '0x2a0408ceb664148718e1ef6082acea9fe257ef19' then 'ApeX OG NFT (APEX-OG)'
when nft_address = '0xeb6c5accafd8515c1b9e4c794bdc41532c5543ec' then 'DGFamily (DGFAM)'
when nft_address = '0xa8384862219188a8f03c144953cf21fc124029ee' then 'LUSDBondNFT (LUSDBOND)'
when nft_address = '0x5520eebb6585c1bd9b32cb9c7456301ee647f278' then 'Awesome Collection, Patek Philippe... (5131R)'
when nft_address = '0xda564f21bd3f9f5240ade363a0b33adb138d3996' then 'Awesome Collection, Richard Mille ... (RM055)'
when nft_address = '0x2c5a6db2288d7b59882752854c00d3fbe1e3b89b' then 'Awesome Collection, Patek Philippe... (5650G)'
when nft_address = '0x6c415673c79b31aca38669ad9fb5cdb7012c0e8e' then 'Bound NFT WPUNKS (boundWPUN...)'
when nft_address = '0x54522da62a15225c95b01bd61ff58b866c50471f' then 'Primitive RMM'
when nft_address = '0xc49b65e5a350292afda1f239ebefe562668717c2' then 'Hyphen Liquidity Token (Hyphen-LP)'
else coalesce (initcap(project_name),initcap(address_name),initcap(nft_address)) end as Project_Title,
sum (mint_price_usd) as Total_Volume,
avg (mint_price_usd) as Average_Volume,
median (mint_price_usd) as Median_Volume,
max (mint_price_usd) as Maximum_Volume
from ethereum.core.ez_nft_mints t1 left outer join ethereum.core.dim_labels t2 on t1.nft_address = t2.address
where mint_price_usd > 0
and block_Timestamp::date >= '2022-01-01' and block_timestamp::date < '2023-01-01'
group by 1,2
order by Maximum_Volume DESC
limit 10


"""

results = memory(sql)
df = pd.DataFrame(results.records)
df.info()

results2 = memory(sql2)
df2 = pd.DataFrame(results2.records)
df2.info()

with st.expander("Check the analysis"):
    st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='project_title:N', y='total_volume:Q',color=alt.Color('project_title', scale=alt.Scale(scheme='dark2')))
        .properties(title='Top 10 NFT collection by total volume',width=600))
    
    st.altair_chart(alt.Chart(df2)
        .mark_bar()
        .encode(x='project_title:N', y='maximum_volume:Q',color=alt.Color('project_title', scale=alt.Scale(scheme='dark2')))
        .properties(title='Top 10 NFT collections with highest price in a sale',width=600))


# In[13]:


st.subheader("3. NFT sales")
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the NFTs sales. More specifically, we will analyze the following data:')
st.markdown('● Marketplaces: volume of sales')
st.markdown('● Total active users on Marketplaces')
st.markdown('● NFT project with the most total mint volume') 
st.markdown('● NFT project with the largest mint volume')
st.markdown('● Top 10 NFT project gained the most value this year')
st.markdown('● Top 10 NFT project lost the most value this year')
st.markdown('● Top 10 NFT project with longest average holding time')
st.markdown('● Top 10 NFT Projects With Most Number of Sold Tokens')



sql="""
select platform_name,
count (distinct tx_hash) as TX_Count,
count (distinct nft_address) as Projects_count,
count (distinct tokenid) as Tokens_Count,
count (distinct buyer_address) as Users_Count,
sum (price_usd) as Total_Volume,
avg (price_usd) as Average_Volume,
median (price_usd) as Median_Volume,
max (price_usd) as Maximum_Volume
from ethereum.core.ez_nft_sales
where block_Timestamp::date >= '2022-01-01' and block_timestamp::date < '2023-01-01'
group by 1


"""


sql2="""
select nft_address,
coalesce (initcap(project_name),initcap(address_name),initcap(nft_address))  as Project_Title,
sum (price_usd) as Total_Volume
from ethereum.core.ez_nft_sales t1 left outer join ethereum.core.dim_labels t2 on t1.nft_address = t2.address
where price_usd > 0
and block_Timestamp::date >= '2022-01-01' and block_timestamp::date < '2023-01-01'
group by 1,2
order by 3 DESC
limit 10

"""


sql3="""
select nft_address,
case when nft_address = '0x22c36bfdcef207f9c0cc941936eff94d4246d14a' then 'Bored Ape Chemistry Club (BACC)'
else coalesce (initcap(project_name),initcap(address_name),initcap(nft_address)) end as Project_Title,
max (price_usd) as Maximum_Volume
from ethereum.core.ez_nft_sales t1 left outer join ethereum.core.dim_labels t2 on t1.nft_address = t2.address
where price_usd > 0
and block_Timestamp::date >= '2022-01-01' and block_timestamp::date < '2023-01-01'
group by 1,2
order by Maximum_Volume DESC
limit 10

"""

sql4="""
with mintable as (
select nft_address,
min (date_trunc(month,block_timestamp)) as mindate
from ethereum.core.ez_nft_sales
where block_timestamp::date >= '2022-01-01' and block_timestamp::date < '2023-01-01'
group by 1),

maxtable as (
select nft_address,
max (date_trunc(month,block_timestamp)) as maxdate
from ethereum.core.ez_nft_sales
where block_timestamp::date >= '2022-01-01' and block_timestamp::date < '2023-01-01'
group by 1),

previous_table as (
select t1.nft_address,
coalesce (initcap(project_name),initcap(address_name),initcap(t1.nft_address)) as Project_Title,
median (price_usd) as Previous_Price
from ethereum.core.ez_nft_sales t1 left outer join ethereum.core.dim_labels t2 on t1.nft_address = t2.address
join mintable t3 on t1.nft_address = t3.nft_address
where price_usd > 0
and date_trunc(month,block_timestamp) = mindate
group by 1,2)	

select Project_Title,
case when project_title = '0x45b5e0a3c6dae8c8170fd78268f807758226b67f' then 'AnifruktNFT (AFT)'
when project_title = '0x6d1b09ae12adeaa3aa5d6b574dbcfaf7343a0b04' then 'Space Eggs (SPACE EGGS)'
when project_title = '0x3f427073af2e9a26b0d5897435af9edd8b00efa6' then 'Ethnology (ETL)'
when project_title = '0xb77bb4bda2e4cfec036f214594e758ac380d0f45' then 'Cool Cats Research Lab (CCLAB)'
when project_title = '0xf22b1af401ff439728f426190e0b3e7b354ff9fa' then 'Gates Of Oxya - Colony (GoOC)'
when project_title = '0x4483fcb6c4ba5614b5a3b9a2ebf2410901ebe507' then 'MKSM'
when project_title = '0x8d25f9f4cd1c42d817e619f334848db47ccc8dca' then 'Tiny Tears (CRY)'
when project_title = '0xa18cb1cdeb75eda5ad4a0922331723451dbcf5ed' then 'TheSaudisGoblin (TSG)'
else Project_Title end as project_title1,
count (distinct tx_hash) as Sales_Count,
(avg(price_usd - Previous_Price)/avg(Previous_Price)) * 100 as Price_Change_Ratio
from ethereum.core.ez_nft_sales t1 join previous_table t2 on t1.nft_address = t2.nft_address 
join maxtable t3 on t1.nft_address = t3.nft_address
where block_timestamp::date >= '2022-01-01' and block_timestamp::date < '2023-01-01'
and date_trunc(month,block_timestamp) = maxdate
and price_usd > 0
group by 1,2 having sales_count > 10
order by Price_Change_Ratio desc 
limit 10
"""

sql5="""
with mintable as (
select nft_address,
min (date_trunc(month,block_timestamp)) as mindate
from ethereum.core.ez_nft_sales
where block_timestamp::date >= '2022-01-01' and block_timestamp::date < '2023-01-01'
group by 1),

maxtable as (
select nft_address,
max (date_trunc(month,block_timestamp)) as maxdate
from ethereum.core.ez_nft_sales
where block_timestamp::date >= '2022-01-01' and block_timestamp::date < '2023-01-01'
group by 1),

previous_table as (
select t1.nft_address,
coalesce (initcap(project_name),initcap(address_name),initcap(t1.nft_address)) as Project_Title,
median (price_usd) as Previous_Price
from ethereum.core.ez_nft_sales t1 left outer join ethereum.core.dim_labels t2 on t1.nft_address = t2.address
join mintable t3 on t1.nft_address = t3.nft_address
where price_usd > 0
and date_trunc(month,block_timestamp) = mindate
group by 1,2)	

select Project_Title,
case when project_title = '0x45b5e0a3c6dae8c8170fd78268f807758226b67f' then 'AnifruktNFT (AFT)'
when project_title = '0x6d1b09ae12adeaa3aa5d6b574dbcfaf7343a0b04' then 'Space Eggs (SPACE EGGS)'
when project_title = '0x3f427073af2e9a26b0d5897435af9edd8b00efa6' then 'Ethnology (ETL)'
when project_title = '0xb77bb4bda2e4cfec036f214594e758ac380d0f45' then 'Cool Cats Research Lab (CCLAB)' 
when project_Title = '0xeb6c5accafd8515c1b9e4c794bdc41532c5543ec' then 'DGFamily (DGFAM)'
when project_Title = '0xd7e97cb08bb8f2ce9e984b6295272286d6424717' then 'MoonPings (MPINGS)'
when project_Title = '0x030ca311c3a971afed275329945cd88c4f74dfcc' then 'MUKYO'
when project_Title = '0xff063937523c4514179a4d9a6769694baab357a8' then '888 Inner Circle - Pink Realm (888P)'
when project_Title = '0x05da517b1bf9999b7762eaefa8372341a1a47559' then 'Keepers (KPR)'
when project_Title = '0x9d7caf9ff78b1edad4500bccfb8e52ffc15dafce' then 'LOOK LABS End Game (EG)'
when project_Title = '0xc84c588d4d9861a2ada2c34ae60460ff14e2d69f' then 'Tiny Bees'
when project_Title = '0xb896c17c8e5e06ea393c4b2b79d5842fabcd3b94' then 'Stewie the Stick (STS)'
else Project_Title end as project_title1,
count (distinct tx_hash) as Sales_Count,
(avg(price_usd - Previous_Price)/avg(Previous_Price)) * 100 as Price_Change_Ratio
from ethereum.core.ez_nft_sales t1 join previous_table t2 on t1.nft_address = t2.nft_address 
join maxtable t3 on t1.nft_address = t3.nft_address
where block_timestamp::date >= '2022-01-01' and block_timestamp::date < '2023-01-01'
and date_trunc(month,block_timestamp) = maxdate
and price_usd > 0
group by 1,2 having sales_count > 10
order by Price_Change_Ratio asc 
limit 10

"""

sql6="""
with receivet as (
select nft_address,
tokenid,
project_name,
nft_to_address as receiver,
nft_from_address as sender,
block_timestamp as receive_date
from ethereum.core.ez_nft_transfers
where block_timestamp::date >= '2022-01-01' and block_timestamp::date < '2023-01-01'
and nft_to_address != '0x0000000000000000000000000000000000000000'),

sendt as (
select t1.nft_address,
t1.tokenid,
t1.project_name,
nft_to_address as receiver,
nft_from_address as sender,
block_timestamp as send_date,
receive_date
from ethereum.core.ez_nft_transfers t1 join receivet t2 on t1.nft_address = t2.nft_address and t1.tokenid = t2.tokenid and t1.nft_from_address = t2.receiver and t1.block_timestamp > t2.receive_date
where block_timestamp::date >= '2022-01-01' and block_timestamp::date < '2023-01-01')

select coalesce (initcap(project_name),initcap(address_name),nft_address) as Project_Title,
case when project_title = '0x5a44ff097652acaa29d0ab52dd25343f213326c6' then 'Metabad Donuts'
when project_title = '0x5f9283a06e86ae04391fad38f76ac84e078b4270' then 'Portals'
when project_title = '0xba4a96b53d73232eb4b3f8fb02b62e8f4d65f887' then 'Therese Isabel Herzog (RESI)'
when project_title = '0x9cca06462f995edd0fedc72a99501367684f30f3' then 'Basic. (BASIC)'
when project_title = '0x279b1d26dfe55332a7b70324ce05b51f8a4fa078' then 'Funy Monki (FYMI)'
when project_title = '0x141ee909f4de4e198c3287e061e3ce95f28d3441' then 'MiamiHome (MIA)'
when project_title = '0xc151e527ac4c5beb7cbb23db5975058efeb646aa' then 'HexApeYachtClub (HAYC)'
else project_title end as project_title1,
avg (datediff(day,receive_date,send_date)) as Holding_Time
from sendt t1 left outer join ethereum.core.dim_labels t2 on t1.nft_address = t2.address
group by 1,2
order by 3 DESC
limit 10

"""

sql7="""
select nft_address,
coalesce (initcap(project_name),initcap(address_name),initcap(nft_address)) as Project_Title,
count (Distinct tokenid) as Sold_tokens
from ethereum.core.ez_nft_sales t1 left outer join ethereum.core.dim_labels t2 on t1.nft_address = t2.address
where block_timestamp::date >= '2022-01-01' and block_timestamp::date < '2023-01-01'
and project_name != 'opensea'
group by 1,2
order by 3 desc
limit 10

"""

results = memory(sql)
df = pd.DataFrame(results.records)
df.info()

results2 = memory(sql2)
df2 = pd.DataFrame(results2.records)
df2.info()

results3 = memory(sql3)
df3 = pd.DataFrame(results3.records)
df3.info()

results4 = memory(sql4)
df4 = pd.DataFrame(results4.records)
df4.info()

results5 = memory(sql5)
df5 = pd.DataFrame(results5.records)
df5.info()

results6 = memory(sql6)
df6 = pd.DataFrame(results6.records)
df6.info()

results7 = memory(sql7)
df7 = pd.DataFrame(results7.records)
df7.info()


with st.expander("Check the analysis"):

    st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='platform_name:N', y='tx_count:Q',color=alt.Color('platform_name', scale=alt.Scale(scheme='dark2')))
        .properties(title='Number of sales by marketplace',width=600))
    st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='platform_name:N', y='users_count:Q',color=alt.Color('platform_name', scale=alt.Scale(scheme='dark2')))
        .properties(title='Active users by marketplace',width=600))
    st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='platform_name:N', y='total_volume:Q',color=alt.Color('platform_name', scale=alt.Scale(scheme='dark2')))
        .properties(title='Total volume by marketplace',width=600))

    st.altair_chart(alt.Chart(df2)
        .mark_bar()
        .encode(x='project_title:N', y='total_volume:Q',color=alt.Color('project_title', scale=alt.Scale(scheme='dark2')))
        .properties(title='Top 10 NFT collection by sales volume',width=600))
    
    st.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='project_title:N', y='maximum_volume:Q',color=alt.Color('project_title', scale=alt.Scale(scheme='dark2')))
        .properties(title='Top 10 NFT collection by highest sale price',width=600))
    
    st.altair_chart(alt.Chart(df4)
        .mark_bar()
        .encode(x='project_title1:N', y='price_change_ratio:Q',color=alt.Color('project_title1', scale=alt.Scale(scheme='dark2')))
        .properties(title='Top 10 NFT collection by gain',width=600))
    
    st.altair_chart(alt.Chart(df5)
        .mark_bar()
        .encode(x='project_title1:N', y='price_change_ratio:Q',color=alt.Color('project_title1', scale=alt.Scale(scheme='dark2')))
        .properties(title='Top 10 NFT collection by price change lose',width=600))
    
    st.altair_chart(alt.Chart(df6)
        .mark_bar()
        .encode(x='project_title1:N', y='holding_time:Q',color=alt.Color('project_title1', scale=alt.Scale(scheme='dark2')))
        .properties(title='Top 10 NFT collection by most holding time',width=600))
    
    st.altair_chart(alt.Chart(df7)
        .mark_bar()
        .encode(x='project_title:N', y='sold_tokens:Q',color=alt.Color('project_title', scale=alt.Scale(scheme='dark2')))
        .properties(title='Top 10 NFT collection by most tokens sold',width=600))
    
    


# In[14]:


st.markdown('This dashboard has been done by _Cristina Tintó_ powered by **Flipside Crypto** data and carried out for **MetricsDAO**.')
