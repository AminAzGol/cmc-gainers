from sqlalchemy import MetaData, create_engine, inspect
import pandas as pd
import psycopg2
import numpy as np
import glob
import os
import time


db_engine = create_engine(os.environ['DATABASE_URL'])


def start_job_scheduler():
    print('starting job scheduler')
    while(1):
        check_all_and_to_sql()
        time.sleep(100)

def check_all_and_to_sql():
    data_dir = '../data'
    all_files = glob.glob(data_dir + "/*.csv")
    all_files = sorted(all_files)
    print(f'{len(all_files)} files found in {data_dir}')
    not_visited_files = get_not_visited_files(all_files)
    print(f'saving {len(not_visited_files)} new files')
    chunk = []
    for i, file_name in enumerate(not_visited_files):
        chunk.append(file_name)
        if(i % 100 == 0):
            files_chunk_to_pandas_to_sql(chunk)
            chunk = []
    files_chunk_to_pandas_to_sql(chunk)
    print(f'{len(not_visited_files)} new files saved to sql')


def get_not_visited_files(files_list):
    visite_df = pd.read_sql('select file from cmc.visited', db_engine)
    fdf = pd.DataFrame(files_list)
    fdf = fdf[~fdf.apply(tuple,1).isin(visite_df.apply(tuple,1))]
    li = fdf[0].to_list()
    return li

def files_chunk_to_pandas_to_sql(files_chunk):
    li = []
    visited_frame = pd.DataFrame(columns=['file', 'corrupt'])
    
    for fname in files_chunk:
        df = pd.read_csv(fname, index_col=None, header=0)
        
        # check data values are in right order
        if not ('5' in df and (df['5'] == '%').all() and 'Unnamed: 0' in df):
            visited_frame = visited_frame.append([{'file': fname, 'corrupt': True}])
        else:
            visited_frame = visited_frame.append([{'file': fname, 'corrupt': False}])
            
        
        li.append(df)
    
    frame = pd.concat(li)
    
    # keep only the ones with right value order
    frame = frame[frame['5'] == '%']
    
    
    frame = frame.drop('5', 1)
    frame = frame.drop('Unnamed: 0', 1)
    frame = frame.rename(columns={'0': 'num', '1': 'name', '2':'symbol', '3': 'price', '4': 'gain', '6': 'vol', '7': 'time'})
    frame.to_sql('gainers', db_engine, schema='cmc', if_exists='append', index=False)
    visited_frame.to_sql('visited', db_engine, schema='cmc', if_exists='append', index=False)
    return visited_frame

def init_db():
    db_engine.execute('create schema if not exists cmc')
    db_engine.execute('create table if not exists cmc.visited \
    ( \
    id serial \
    constraint visited_pk \
    primary key, \
    file varchar(100), \
    corrupt boolean default false \
    );')
    db_engine.execute('create table if not exists cmc.gainers \
    ( \
    id serial \
    constraint gainers_pk \
    primary key, \
    num integer, \
    symbol varchar(100), \
    price varchar(100), \
    gain double precision, \
    vol varchar(100), \
    time timestamp \
    );')
    db_engine.execute('create index if not exists visited_file_index \
    on cmc.visited (file); \
    ')
    print('db init done')

init_db()
start_job_scheduler()