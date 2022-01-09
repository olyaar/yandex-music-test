import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd

def on_repeat(df: pd.DataFrame, year: int, n_tracks: int) -> pd.DataFrame:
    '''
    Возвращает DataFrame, который содержит id треков, количество повторных проигрываний и суммарную длительность проигрывания,
    отсортированный по убыванию по количеству повторов. 
    '''
    # Фильтруем по году, при условии, что тип start_timestamp и end_timestamp - datetime64
    df = df.query(f'start_timestamp >= {year}0101 & end_timestamp < {year}1231 ')
    
    # Сортируем по пользователям и началу проигрывания трека
    df = df.sort_values(by=['user_id', 'start_timestamp']) \
        .reset_index()
    
    # Создаем колонку длительности прослушивания трека в секундах
    df['play_duration'] = (df.end_timestamp - df.start_timestamp) / np.timedelta64(1, 's') 

    # Создаем колонку, куда будем записывать повторения 
    df['n_repeats'] = 0

    '''
    Собираем повторения. Прослушивание засчитывается за повтор, если выполнены три условия:
    1. Длительность прослушивания больше 30 секунд. Альтернативно, здесь можно использовать соотношение длительности проигрывания к 
    длительности трека df.play_duration/df.duration и задать условием для повтора проигрывание половины трека (>=0.5), трека целиком (==1) и т.д.
    2. ID пользователя должен совпадать с предыдущим ID (т.е. это один и тот же пользователь)
    3. ID трека должен совпадать с предыдущим ID (т.е. это один и тот же трек)
    '''
    for i in range(1, df.index.max()+1):
        if (df.play_duration[i-1] > 30) & (df.user_id[i] == df.user_id[i-1]) & (df.track_id[i] == df.track_id[i-1]):
            df['n_repeats'][i] = 1
    
    # Группируем по ID трека и считаем повторения и суммарное время проигрывания для каждого трека, сортируем по убыванию
    on_repeat_df = df.groupby('track_id').agg({'n_repeats': 'count', 'play_duration': 'sum'}) \
        .sort_values(by= 'n_repeats', ascending=False) \
        .reset_index() 
    
    on_repeat_df.index = on_repeat_df.index + 1 # Начинаем отсчет с 1, чтобы красиво вывести топ треков :)

    # Выводим необходимое количество треков в топе
    print(f'Top {n_tracks} tracks on repeat:\n{on_repeat_df.head(n_tracks)}')

    # При необходимости возвращаем датафрейм
    return on_repeat_df