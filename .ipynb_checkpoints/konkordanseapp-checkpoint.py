import streamlit as st
import dhlab_v2 as d2
import pandas as pd
from PIL import Image
import urllib

@st.cache(suppress_st_warning=True, show_spinner = False)
def konk(corpus = None, query = None): 
    conc = d2.Concordance(corpus, query)
    #conc['link'] = conc['urn'].apply(lambda c: "[{display}](https://www.nb.no/items/{x}?searchText={q})".format(x = c, display = c.split('_')[2], q = urllib.parse.quote(query)))
    return conc

@st.cache(suppress_st_warning=True, show_spinner = False)
def korpus():
    return pd.read_csv('naob.csv', header = 0, index_col = 0)

naob = korpus()
naob = naob[naob.corpus == 'naob_hele']

image = Image.open('NB-logo-no-eng-svart.png')
st.image(image, width = 200)
st.markdown('Se mer om å drive analytisk DH på [DHLAB-siden](https://nbviewer.jupyter.org/github/DH-LAB-NB/DHLAB/blob/master/DHLAB_ved_Nasjonalbiblioteket.ipynb), og korpusanalyse via web [her](https://beta.nb.no/korpus/)')


st.title('Søk i NAOB')

words = st.text_input('Søk etter ord og fraser', """ "arbeid* på" """)


#st.write(subject_ft, ddk_ft, doctype, period_slider, " ".join(allword))


conc = konk(corpus = naob, query = words)
st.write("antall treff:", conc.size)
samplesize = st.number_input("Maks antall konkordanser (klikk +/- for å se nye grupper eller velg hele størrelsen):", 50)

st.markdown(f"## Konkordanser for __{words}__")

st.write('\n\n'.join(
    [
        f""" [{r[1][1]}](https://urn.nb.no/{r[1][1]}) {r[1][2]}""" 
        for r in 
        conc.show(10, style = False).iterrows()
    ]
).replace('<b>','**').replace('</b>', '**')
        )

#st.write(conc.show(10))
