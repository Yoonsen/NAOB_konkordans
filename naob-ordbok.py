import streamlit as st
import dhlab.text as dh
import dhlab.api.dhlab_api as api
import pandas as pd
from PIL import Image
import urllib

@st.cache(suppress_st_warning=True, show_spinner = False)
def konk(corpus = None, query = None): 
    conc = dh.Concordance(corpus, query)
    #conc['link'] = conc['urn'].apply(lambda c: "[{display}](https://www.nb.no/items/{x}?searchText={q})".format(x = c, display = c.split('_')[2], q = urllib.parse.quote(query)))
    return conc

@st.cache(suppress_st_warning=True, show_spinner = False)
def korpus():
    df = pd.read_csv('naob.csv', header = 0, index_col = 0)
    return dh.CorpusFromIdentifiers(identifiers=list(set(df.urn.values))).corpus

def do_concordance(urns=None, words = None, samplesize=10):
    if urns != [] and not urns is None:
        conc = api.concordance(urns=urns, words = words, limit = 5000)
        st.write("antall treff:", len(conc))


        st.markdown(f"## Konkordanser for _{words}_")

        st.write('\n\n'.join(
            [
                f""" [{r[1][1]}](https://urn.nb.no/{r[1][1]}) {r[1][2]}""" 
                for r in 
                conc.sample(min(samplesize, len(conc))).iterrows()
            ]
        ).replace('<b>','**').replace('</b>', '**')
                )
    else:
        st.write('ingen konkordanser')



naob = korpus()
#naob = naob[naob.corpus == 'naob_hele']

image = Image.open('NB-logo-no-eng-svart.png')
st.image(image, width = 200)
st.markdown('Les mer om DH på [DHLAB-siden](https://nb.no/dhlab)')


st.title('Søk i NAOBs korpus')
author = st.text_input("Angi forfatter", "")
corpus = naob
if author != "":
    corpus = naob[naob.authors.str.contains(author)]
    
words = st.text_input('Søk etter ord og fraser (ord med bindestrek eller punktum må settes i anførselstegn)', """ "titt-tei" """)


#st.write(subject_ft, ddk_ft, doctype, period_slider, " ".join(allword))

samplesize = st.number_input("Maks antall konkordanser (klikk +/- for å se nye grupper eller velg hele størrelsen):", 50)

do_concordance(urns = list(corpus.urn.values), words = words, samplesize= int(samplesize))

#st.write(conc.show(10))
