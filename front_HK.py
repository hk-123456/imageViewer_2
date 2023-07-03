import streamlit as st
from PIL import Image
import os
import re
import pandas as pd
import datetime as dt

class Sample():
    def __init__(self, path) -> None:
        self.name = path
        self.files = os.listdir(f'data/{path}')
        self.suggestion = [re.findall(r'(?<=\d_).+(?=\=Proc)', f)[0] for f in self.files]
    
    def return_images(self):
        return [Image.open(f'data/{self.name}/{file}') for file in self.files]

def main():

    # ========= Define functions =========
    def push_tbl():
        df_var = pd.DataFrame({'Query name': [sample.name for _ in range(len(sample.suggestion) - 1)],
                               'Suggested file': sample.suggestion[1:],
                               '山田先生': [v for k, v in st.session_state.items() if 'p1' in k],
                               '山田さん': [v for k, v in st.session_state.items() if 'p2' in k],
                               '近藤': [v for k, v in st.session_state.items() if 'p3' in k],
                               '撮像モード': [v for k, v in st.session_state.items() if 'p4' in k]})
        st.session_state.df = pd.concat([df_var, st.session_state.df])
        st.session_state.log[st.session_state.counter] = 1

    def minus_counter():
        if st.session_state.counter:
            st.session_state['counter'] -= 1
        else:
            # TODO "最初のクエリです"というポップアップダイアログを出したい
            pass

    def plus_counter():
        if (st.session_state.counter + 1) < len(st.session_state.samples):
            st.session_state['counter'] += 1
        else:
            # TODO "最後のクエリです"というポップアップダイアログを出したい
            pass


    # ========= Initializing app state =========
    if 'samples' not in st.session_state: 
        st.session_state.samples = [path for path in os.listdir('data') if os.path.isdir(os.path.join('data', path))]
        st.session_state.log = [0 for _ in range(len(st.session_state.samples))]
        st.session_state.counter = 0
        st.session_state.df = pd.DataFrame({'Query name': [], 
                                            'Suggested file': [],
                                            '山田先生': [], 
                                            '山田さん':[], 
                                            '近藤':[], 
                                            '撮像モード':[]})

    sample = Sample(st.session_state.samples[st.session_state.counter])
    pictures = sample.return_images()


    # ======== Viewer =========
    ## >>>> Page setting <<<<<
    st.set_page_config(layout='wide')

    ## >>>> Ttitle <<<<
    st.title('内視鏡 類似画像供覧ツール VGG19')

    ## >>>> Query name <<<<
    if st.session_state.log[st.session_state.counter]:
        st.markdown(f'Query file is: {sample.name} **:red[供覧済みです!]**')
    else:
        st.markdown(f'Query file is: {sample.name}')

    ## >>>> Pictures with tile-like viewing <<<<
    for row in range(-(-len(pictures)) // 3):
        for i, col in enumerate(st.columns(3)):
            k = row * 3 + i
            
            if k==0:
               col.subheader('Query:  '+ sample.suggestion[k])
               col.image(pictures[k])
            
            else:
               col.subheader(str(k) + ':   ' + sample.suggestion[k])
               col.image(pictures[k])

    ## >>>> Input form <<<<
    with st.form('供覧結果', clear_on_submit=True):
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            c1.subheader('山田先生')
            for i in range(1, len(pictures)):
                c1.radio(str(i) + ':   ' + sample.suggestion[i], ('OK', 'Bad'), key = f'p1{i}', horizontal=True, args=[1, 0])
        with c2:
            c2.subheader('山田さん')
            for i in range(1, len(pictures)):
                c2.radio(str(i) + ':   ' + sample.suggestion[i], ('OK', 'Bad'), key = f'p2{i}', horizontal=True, args=[1, 0])
        with c3:
            c3.subheader('近藤')
            for i in range(1, len(pictures)):
                c3.radio(str(i) + ':   ' + sample.suggestion[i], ('OK', 'Bad'), key = f'p3{i}', horizontal=True, args=[1, 0])
        with c4:
            c4.subheader('撮像モード')
            for i in range(1, len(pictures)):
                c4.radio(str(i) + ':   ' + sample.suggestion[i], ('BLI', 'Indigo', 'LCI', 'NBI', 'WLI'), key = f'p4{i}', horizontal=True, args=[1, 0])
        with c5:
            st.form_submit_button(label = '供覧結果を転記', on_click = push_tbl)

    ## >>>> Move next and previous buttons <<<<
    col1, col2 =st.columns(2)
    with col1:
        st.button('<< 前の画像へ', on_click=minus_counter)
    with col2:
        st.button('次の画像へ >>', on_click=plus_counter)

    ## >>>> Data table of reviewing results <<<<
    edited_df = st.data_editor(st.session_state.df, num_rows='dynamic')

    ## >>>> Download button <<<<
    st.download_button(label = 'Download csv file',
                       data = edited_df.to_csv().encode('shift-jis'),
                       mime = 'text/csv',
                       file_name = 'output/' + dt.datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv')

if __name__ == '__main__':
    main()
