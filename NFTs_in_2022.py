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


# In[7]:


st.title('Solana Staking Megadashboard')
st.write('')
st.markdown('One of the main features that has emerged from cryptocurrencies is **_staking_**. In principle, staking consists of logging and blocking your cryptocurrencies from the wallet of a particular crypto and earning rewards for doing so. However, in the case of Solana, when you start staking, the first thing you do is create a Solana holding account. A **Solana** stake account can be used to delegate tokens to network validators to earn potential rewards for the owner of the stake account. Stake accounts are created and managed differently from a traditional wallet address, known as a system account.')
st.markdown('Each stake account has two signing authorities specified by their respective address, each of which is authorised to perform certain transactions on the stake account. The stake authority is used to sign transactions for the following operations:')
st.markdown('● Stake delegation')
st.markdown('● Deactivation of stake delegation')
st.markdown('● Splitting the stake account, creating a new stake account with a portion of the funds from the first account')
st.markdown('● Merging two participation accounts into a single account')
st.markdown('● Establish a new stake authority')
st.write('')
st.markdown('Another aspect that will be analysed in this dashboard is the term Marinade Staked SOL (mSOL). It is the first liquid betting protocol created in Solana and is supported by the Solana Foundation. Users bet their SOL tokens with Marinade, which uses automatic betting strategies to delegate the SOL to validators, and the user receives staked SOL tokens called mSOL that can be used in the DeFi world or exchanged at any time. to the original SOL tokens to undo the bet.')
st.markdown('1. Staking contribution on Solana')
st.markdown('2. Staking SOL on Marinade')
st.markdown('3. Staking development')
st.write('')
st.subheader('1. How is staking contributing to Solana progression?')
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the% of Solana stake. More specifically, we will analyze the following data:')
st.markdown('● Total Solana transactions')
st.markdown('● Total delegate transactions')
st.markdown('● Percentage of transactions for Delegate')
st.markdown('● All transactions involving staking actions')
st.markdown('● Percentage of transactions involving staking actions')
st.markdown('● Total vs staked transactions over time')
st.markdown('● Cumulative total vs staked transactions over time')
st.markdown('● Transactions involving staking over time')
st.markdown('● Average amount staked per transaction')
st.write('')

sql="""
WITH
all_txs as (
SELECT
sum(1) as txs
from solana.core.fact_events where succeeded='TRUE' and event_type is not null
),
staked_txs as (
SELECT
sum(1) as txs
from solana.core.fact_events where succeeded='TRUE' and event_type='delegate' and event_type is
not null
)
SELECT
x.txs as total_txs,
y.txs as staked_txs,
(staked_txs/total_txs)*100 as pcg_staking_txs
from all_txs x, staked_txs y
"""

st.experimental_memo(ttl=50000)
def memory(code):
    data=sdk.query(code)
    return data

results = memory(sql)
df = pd.DataFrame(results.records)
df.info()
    
sql2="""
WITH
txs as (
SELECT
sum(1) as all_txs
from solana.core.fact_events where succeeded='TRUE' and event_type is not null
),
staked_txs as (
SELECT
sum(1) as staked_txs
from solana.core.fact_events
where succeeded='TRUE' and (instruction:programId='Stake11111111111111111111111111111111111111' or event_type='delegate' or event_type='deactivate')
)
SELECT
all_txs,
staked_txs,
(staked_txs/all_txs)*100 as pcg_staked_txs
from txs, staked_txs
"""
             
results2 = memory(sql2)
df2 = pd.DataFrame(results2.records)
df2.info()

with st.expander("Check the analysis"):
    col1,col2,col3=st.columns(3)
    with col1:
        st.metric('Total Solana transactions',df['total_txs'][0])
    col2.metric('Total staking transactions',df['staked_txs'][0])
    col3.metric('% of staking actions',df['pcg_staking_txs'][0])
    st.write('')

    col1,col2=st.columns(2)
    with col1:
        st.metric('All transactions involving staking actions',df2['all_txs'][0])
    col2.metric('% of transactions involving staking actions',df2['pcg_staked_txs'][0])
    
    
    sql="""
    WITH
    all_txs as (
    SELECT
    trunc(block_timestamp,'day') as date,
    sum(1) as txs
    from solana.core.fact_events where block_timestamp>='2022-01-01' and event_type is not null
    group by 1
    ),
    staked_txs as (
    SELECT
    trunc(block_timestamp,'day') as date,
    sum(1) as txs
    from solana.core.fact_events where block_timestamp>='2022-01-01' and event_type='delegate' and
    event_type is not null
    group by 1
    )
    SELECT
    x.date,
    x.txs as total_txs,
    sum(total_txs) over (order by x.date) as cum_txs,
    y.txs as staked_txs,
    sum(staked_txs) over (order by x.date) as cum_staked_txs,
    (staked_txs/total_txs)*100 as pcg_staking_txs,
    100-pcg_staking_txs as pcg_non_staking_txs
    from all_txs x, staked_txs y where x.date = y.date
    order by 1 asc

    """

    results = memory(sql)
    df = pd.DataFrame(results.records)
    df.info()
    
    base=alt.Chart(df).encode(x=alt.X('date:O', axis=alt.Axis(labelAngle=325)))
    line=base.mark_line(color='blue').encode(y=alt.Y('total_txs:Q', axis=alt.Axis(grid=True),scale=alt.Scale(type="log")))
    bar=base.mark_line(color='orange').encode(y='staked_txs:Q')
    st.altair_chart((bar + line).properties(title='Evolution of Solana transactions vs staking',width=600))
    
    base=alt.Chart(df).encode(x=alt.X('date:O', axis=alt.Axis(labelAngle=325)))
    line=base.mark_line(color='blue').encode(y=alt.Y('cum_txs:Q', axis=alt.Axis(grid=True),scale=alt.Scale(type="log")))
    bar=base.mark_line(color='orange').encode(y='cum_staked_txs:Q')
    st.altair_chart((bar + line).properties(title='Evolution of total Solana transactions vs staking',width=600))
    
    base=alt.Chart(df).encode(x=alt.X('date:O', axis=alt.Axis(labelAngle=325)))
    line=base.mark_line(color='blue').encode(y=alt.Y('pcg_non_staking_txs:Q', axis=alt.Axis(grid=True),scale=alt.Scale(type="log")))
    bar=base.mark_line(color='orange').encode(y='pcg_staking_txs:Q')
    st.altair_chart((bar + line).properties(title='Percentage of staking transactions on Solana',width=600))


# In[10]:


st.subheader("2. Staking SOL on Marinade")
st.markdown('**Marinade** is a DAO that makes Solana even more censorship-resistant and composable through liquid staking. Marinade delegates staked SOL through a permissionless algorithmic delegation strategy to more than 400 validators to support the networks decentralization.')
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the staking SOL on Marinade. More specifically, we will analyze the following data over the past 3 months:')
st.markdown('● mSOL staked')
st.markdown('● Cumulative mSOL staked')
st.markdown('● Average mSOL staked per transaction')
st.markdown('● Top 10 largest transactions')
st.markdown('● Most popular tokens from which mSOL is swapped for')
st.markdown('● Most popular tokens from which mSOL is swapped to')
st.markdown('● Most popular tokens swapped for and to mSOL')


with st.expander("Check the analysis"):

    sql="""
    WITH
    msol_staked as (
    select
    trunc(block_timestamp,'day') as date,
    sum(case when inner_instruction:instructions[1]:parsed:info:amount/1000000000 is not null
    then inner_instruction:instructions[1]:parsed:info:amount/1000000000
    else inner_instruction:instructions[2]:parsed:info:amount/1000000000 end) as
    msol_amount_staked
    from solana.core.fact_events
    where date >=current_date-interval '3 MONTHS'
    -- on Solana we *always* add a small date range for query efficiency!
    and (instruction:programId = 'MarBmsSgKXdrN1egZf5sqe1TMai9K1rChYNDJgjq7aD' or
    instruction:programId = 'mRefx8ypXNxE59NhoBqwqb3vTvjgf8MYECp4kgJWiDY')
    and (inner_instruction:instructions[0]:parsed:info:source =
    '7GgPYjS5Dza89wV6FpZ23kUJRG5vbQ1GM25ezspYFSoE' or
    inner_instruction:instructions[1]:parsed:info:source =
    '7GgPYjS5Dza89wV6FpZ23kUJRG5vbQ1GM25ezspYFSoE')
    group by 1
    order by 1
    ),
    msol_unstaked as (
    select
    trunc(block_timestamp,'day') as date,
    sum(inner_instruction:instructions[0]:parsed:info:amount/1000000000) as
    msol_amount_unstaked,
    avg(inner_instruction:instructions[0]:parsed:info:amount/1000000000) as
    avg_msol_unstaked
    from solana.core.fact_events
    where date >=current_date-interval '3 MONTHS'
    -- on Solana we *always* add a small date range for query efficiency!
    and instruction:programId = 'MarBmsSgKXdrN1egZf5sqe1TMai9K1rChYNDJgjq7aD'
    and inner_instruction:instructions[0]:parsed:info:source =
    '7GgPYjS5Dza89wV6FpZ23kUJRG5vbQ1GM25ezspYFSoE'
    group by 1
    order by 1
    )
    SELECT
    x.date,
    msol_amount_staked,
    sum(msol_amount_staked) over (order by x.date) as cum_msol_staked,
    avg(msol_amount_staked) over (order by x.date) as avg_msol_staked
    from msol_staked x, msol_unstaked y where x.date=y.date
    order by 1 asc

    """

    results = memory(sql)
    df = pd.DataFrame(results.records)
    df.info()


    base=alt.Chart(df).encode(x=alt.X('date:O', axis=alt.Axis(labelAngle=325)))
    line=base.mark_line(color='dark_blue').encode(y=alt.Y('cum_msol_staked:Q', axis=alt.Axis(grid=True)))
    bar=base.mark_bar(color='blue',opacity=0.5).encode(y='msol_amount_staked:Q')
    st.altair_chart((bar + line).resolve_scale(y='independent').properties(title='Evolution of mSOL staked on Marinade',width=600))

    st.altair_chart(alt.Chart(df)
        .mark_line()
        .encode(x='date:N', y='avg_msol_staked:Q')
        .properties(title='Average mSOL staked',width=600))

    sql="""
    select
    case when inner_instruction:instructions[1]:parsed:info:amount/1000000000 is not null then
    inner_instruction:instructions[1]:parsed:info:amount/1000000000
    else inner_instruction:instructions[2]:parsed:info:amount/1000000000 end as msol_staked,
    block_timestamp
    from solana.core.fact_events
    where block_timestamp >=current_date-interval '3 MONTHS'
    -- on Solana we *always* add a small date range for query efficiency!
    and (instruction:programId = 'MarBmsSgKXdrN1egZf5sqe1TMai9K1rChYNDJgjq7aD' or
    instruction:programId = 'mRefx8ypXNxE59NhoBqwqb3vTvjgf8MYECp4kgJWiDY')
    and (inner_instruction:instructions[0]:parsed:info:source =
    '7GgPYjS5Dza89wV6FpZ23kUJRG5vbQ1GM25ezspYFSoE' or
    inner_instruction:instructions[1]:parsed:info:source =
    '7GgPYjS5Dza89wV6FpZ23kUJRG5vbQ1GM25ezspYFSoE')
    and msol_staked is not null
    order by 1 DESC
    limit 10

    """

    results = memory(sql)
    df = pd.DataFrame(results.records)
    df.info()


    st.table(df)
    
    sql="""
    with swaps_to as(
    Select
    distinct swap_from_mint,
    address_name,
    count(distinct tx_id) as swapcount,
    sum(swap_from_amount) as volume
    From solana.core.fact_swaps s
    LEFT OUTER JOIN solana.core.dim_labels b ON s.swap_from_mint =b.address
    Where block_timestamp >=current_date-interval '3 MONTHS' And succeeded = 'True'
    and swap_program like '%jupiter%' and swap_to_mint in
    ('mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So')
    Group by 1,2
    ),
    swaps_from as (
    select
    distinct swap_to_mint,
    address_name,
    count(distinct tx_id) as swapcount,
    sum(swap_to_amount) as volume
    From solana.core.fact_swaps s
    LEFT OUTER JOIN solana.core.dim_labels b ON s.swap_to_mint =b.address
    Where block_timestamp >=current_date-interval '3 MONTHS' And succeeded = 'True'
    and swap_program like '%jupiter%' and swap_from_mint in
    ('mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So')
    Group by 1,2
    )
    select
    x.address_name,
    sum(x.swapcount) as total_swaps
    from swaps_from x, swaps_to y where x.address_name=y.address_name
    group by 1
    order by 2 desc

    """

    results = memory(sql)
    df = pd.DataFrame(results.records)
    df.info()


    st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='address_name:N', y='total_swaps:Q',color=alt.Color('address_name', scale=alt.Scale(scheme='dark2')))
        .properties(title='Top 10 most swapped tokens for and to mSOL',width=600))
    
    sql="""
    with swaps_to as(
    Select
    distinct swap_from_mint,
    address_name,
    count(distinct tx_id) as swapcount,
    sum(swap_from_amount) as volume
    From solana.core.fact_swaps s
    LEFT OUTER JOIN solana.core.dim_labels b ON s.swap_from_mint =b.address
    Where block_timestamp >=current_date-interval '3 MONTHS' And succeeded = 'True'
    and swap_program like '%jupiter%' and swap_to_mint in
    ('mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So')
    Group by 1,2
    ),
    swaps_from as (
    select
    distinct swap_to_mint,
    address_name,
    count(distinct tx_id) as swapcount,
    sum(swap_to_amount) as volume
    From solana.core.fact_swaps s
    LEFT OUTER JOIN solana.core.dim_labels b ON s.swap_to_mint =b.address
    Where block_timestamp >=current_date-interval '3 MONTHS' And succeeded = 'True'
    and swap_program like '%jupiter%' and swap_from_mint in
    ('mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So')
    Group by 1,2
    )
    select
    x.address_name,
    sum(x.swapcount) as total_swaps
    from swaps_from x
    group by 1
    order by 2 desc

    """

    results = memory(sql)
    df = pd.DataFrame(results.records)
    df.info()


    st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='address_name:N', y='total_swaps:Q',color=alt.Color('address_name', scale=alt.Scale(scheme='dark2')))
        .properties(title='Top 10 most swapped tokens for mSOL',width=600))
    
    sql="""
    with swaps_to as(
    Select
    distinct swap_from_mint,
    address_name,
    count(distinct tx_id) as swapcount,
    sum(swap_from_amount) as volume
    From solana.core.fact_swaps s
    LEFT OUTER JOIN solana.core.dim_labels b ON s.swap_from_mint =b.address
    Where block_timestamp >=current_date-interval '3 MONTHS' And succeeded = 'True'
    and swap_program like '%jupiter%' and swap_to_mint in
    ('mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So')
    Group by 1,2
    ),
    swaps_from as (
    select
    distinct swap_to_mint,
    address_name,
    count(distinct tx_id) as swapcount,
    sum(swap_to_amount) as volume
    From solana.core.fact_swaps s
    LEFT OUTER JOIN solana.core.dim_labels b ON s.swap_to_mint =b.address
    Where block_timestamp >=current_date-interval '3 MONTHS' And succeeded = 'True'
    and swap_program like '%jupiter%' and swap_from_mint in
    ('mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So')
    Group by 1,2
    )
    select
    address_name,
    sum(swapcount) as total_swaps
    from swaps_to
    group by 1
    order by 2 desc

    """

    results = memory(sql)
    df = pd.DataFrame(results.records)
    df.info()


    st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='address_name:N', y='total_swaps:Q',color=alt.Color('address_name', scale=alt.Scale(scheme='dark2')))
        .properties(title='Top 10 most swapped tokens to mSOL',width=600))


# In[12]:


st.subheader("3. Staking development")
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the staking activity over the past 3 months considering the crash after FTX bad news. More specifically, we will analyze the following information:')
st.markdown('● Daily staking events per period')
st.markdown('● Average transactions by period')
st.markdown('● Daily staking users per period')
st.markdown('● Average users by period')
st.markdown('● Staking transactions by pool')
st.markdown('● Unstaking transactions by pool')
st.markdown('● Netflow staking transactions by pool')
st.markdown('● Stakers by pool')
st.markdown('● Unstaking users by pool')
st.markdown('● Stakers users by pool')
st.markdown('● Net staking actions by pool since crash')
st.markdown('● Net staking volume by pool since crash')


sql="""
SELECT
trunc (x.block_timestamp,'day') as date,
--label,
case when x.block_timestamp < '2022-11-08' then 'Previous to FTX/Alameda news'
else 'After the FTX/Alameda news' end as period,
count(distinct x.tx_id) as txs,
count(distinct signers[0]) as users
from solana.core.fact_events x
join solana.core.fact_transactions y on x.tx_id=y.tx_id
--join solana.core.dim_labels on program_id = address
WHERE event_type='delegate' and event_type is not null AND x.block_timestamp >=
current_date-INTERVAL '3 MONTHS'
GROUP BY 1, 2
order by 1 asc

"""

results = memory(sql)
df = pd.DataFrame(results.records)
df.info()

with st.expander("Check the analysis"):

    st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='txs:Q',color=alt.Color('period', scale=alt.Scale(scheme='dark2')))
        .properties(title='Daily staking actions',width=600))
    st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='users:Q',color=alt.Color('period', scale=alt.Scale(scheme='dark2')))
        .properties(title='Daily active stakers',width=600))


    sql="""
    WITH
    transactions as (
    SELECT
    trunc (x.block_timestamp,'day') as date,
    --label,
    case when x.block_timestamp < '2022-11-08' then 'a. Previous to FTX/Alameda
    news' else 'b. After the FTX/Alameda news' end as period,
    count(distinct x.tx_id) as txs,
    count(distinct signers[0]) as users
    from solana.core.fact_events x
    join solana.core.fact_transactions y on x.tx_id=y.tx_id
    --join solana.core.dim_labels on program_id = address
    WHERE x.block_timestamp >= current_date - INTERVAL '3 MONTHS' and event_type='delegate' and event_type is
    not null
    GROUP BY 1, 2
    order by 1 asc
    )
    SELECT
    period,
    avg(txs) as avg_transactions,
    avg(users) as avg_active_users
    from transactions
    group by 1 order by 1 asc
    """

    results = memory(sql)
    df = pd.DataFrame(results.records)
    df.info()

    st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='avg_transactions:Q',color=alt.Color('period', scale=alt.Scale(scheme='dark2')))
        .properties(title='Average daily staking actions by period',width=600))
    st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='avg_active_users:Q',color=alt.Color('period', scale=alt.Scale(scheme='dark2')))
        .properties(title='Average active stakers by period',width=600))


    sql="""
    WITH
    staking as (
    SELECT
    trunc (block_timestamp,'day') as date,
    stake_pool_name as pool,
    count(distinct tx_id) as staking_txs,
    count(distinct address) as staking_users
    from solana.core.fact_stake_pool_actions
    WHERE block_timestamp >= current_date - INTERVAL '3 MONTHS' and succeeded=TRUE and action in
    ('deposit','deposit_stake')
    GROUP BY 1, 2
    order by 1 asc
    ),
    unstaking as (
    SELECT
    trunc (block_timestamp,'day') as date,
    stake_pool_name as pool,
    count(distinct tx_id) as unstaking_txs,
    count(distinct address) as unstaking_users
    from solana.core.fact_stake_pool_actions
    WHERE block_timestamp >= current_date - INTERVAL '3 MONTHS' and succeeded=TRUE and action in
    ('withdraw','withdraw_stake')
    GROUP BY 1, 2
    order by 1 asc
    )
    SELECT
    ifnull(x.date,y.date) as dates,
    ifnull(x.pool,y.pool) as pools,
    ifnull(staking_txs,0) as staking_transactions,ifnull(unstaking_txs,0) as
    unstaking_transactions,
    staking_transactions-unstaking_transactions as net_txs,
    ifnull(staking_users,0) as staking_user,ifnull(unstaking_users,0) as unstaking_user,
    staking_user-unstaking_user as net_users
    from staking x
    left outer join unstaking y on x.date=y.date and x.pool=y.pool
    order by 1 asc
    """

    results = memory(sql)
    df = pd.DataFrame(results.records)
    df.info()
    
    st.write('**Staking activity by pool**')

    st.altair_chart(alt.Chart(df)
        .mark_line()
        .encode(x='dates:N', y='staking_transactions:Q',color=alt.Color('pools', scale=alt.Scale(scheme='Dark2')))
        .properties(title='Staking transactions by pool',width=600))
    st.altair_chart(alt.Chart(df)
        .mark_line()
        .encode(x='dates:N', y='unstaking_transactions:Q',color=alt.Color('pools', scale=alt.Scale(scheme='Dark2')))
        .properties(title='Unstaking transactions by pool',width=600))
    st.altair_chart(alt.Chart(df)
        .mark_line()
        .encode(x='dates:N', y='net_txs:Q',color=alt.Color('pools', scale=alt.Scale(scheme='Dark2')))
        .properties(title='Net staking actions by pool',width=600))
    st.altair_chart(alt.Chart(df)
        .mark_line()
        .encode(x='dates:N', y='staking_user:Q',color=alt.Color('pools', scale=alt.Scale(scheme='Dark2')))
        .properties(title='Active stakers by pool',width=600))
    st.altair_chart(alt.Chart(df)
        .mark_line()
        .encode(x='dates:N', y='unstaking_user:Q',color=alt.Color('pools', scale=alt.Scale(scheme='Dark2')))
        .properties(title='Active unstakers by pool',width=600))
    st.altair_chart(alt.Chart(df)
        .mark_line()
        .encode(x='dates:N', y='net_users:Q',color=alt.Color('pools', scale=alt.Scale(scheme='Dark2')))
        .properties(title='Net stakers by pool',width=600))

    sql="""
    WITH
    t1 as (
    select
    stake_pool_name,
    count (distinct tx_id) as txs,
    count (distinct address) as users,
    sum (amount/1e9) as volume,
    avg ((amount/1e9)) as avg_volume
    from solana.core.fact_stake_pool_actions
    where succeeded = 'TRUE'
    and block_timestamp >= current_date - INTERVAL '3 MONTHS' 
    and action ilike '%deposit%'
    group by 1
    ),
    t2 as (
    select
    stake_pool_name,
    count (distinct tx_id) as txs,
    count (distinct address) as users,
    sum (amount/1e9) as volume,
    avg ((amount/1e9)) as avg_volume
    from solana.core.fact_stake_pool_actions
    where succeeded = 'TRUE'
    and block_timestamp >= current_date - INTERVAL '3 MONTHS' 
    and (action ilike '%withdraw%' or action ilike '%unstake%' or action ilike '%claim%')
    group by 1
    )
    SELECT
    x.stake_pool_name,
    x.txs as staking_txs, y.txs*(-1) as unstaking_txs, staking_txs+unstaking_txs as
    net_staking_actions,
    x.users as stakers, y.users*(-1) as unstakers,stakers+unstakers as net_stakers,
    x.volume as volume_staked, y.volume*(-1) as volume_unstaked,
    volume_staked+volume_unstaked as net_volume
    from t1 x join t2 y on x.stake_pool_name=y.stake_pool_name
    """

    results = memory(sql)
    df = pd.DataFrame(results.records)
    df.info()

    st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='stake_pool_name:N', y='net_staking_actions:Q',color=alt.Color('stake_pool_name', scale=alt.Scale(scheme='dark2')))
        .properties(title='Total netflow actions by pool',width=600))
    st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='stake_pool_name:N', y='net_stakers:Q',color=alt.Color('stake_pool_name', scale=alt.Scale(scheme='dark2')))
        .properties(title='Total netflow users by pool',width=600))
    st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='stake_pool_name:N', y='net_volume:Q',color=alt.Color('stake_pool_name', scale=alt.Scale(scheme='dark2')))
        .properties(title='Total netflow volume by pool',width=600))


# In[13]:


st.markdown('This dashboard has been done by _Cristina Tintó_ powered by **Flipside Crypto** data and carried out for **MetricsDAO**.')


# In[ ]:




