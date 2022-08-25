import streamlit as st
import dhlab.text as dh
from urllib.parse import quote
import dhlab.api.dhlab_api as api
import pandas as pd
from PIL import Image
import urllib

# for excelnedlastning
from io import BytesIO
#from pyxlsb import open_workbook as open_xlsb



st.set_page_config(page_title="NAOB", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)


@st.cache(suppress_st_warning=True, show_spinner=False)
def to_excel(df):
    """Make an excel object out of a dataframe as an IO-object"""
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    worksheet = writer.sheets['Sheet1']
    writer.save()
    processed_data = output.getvalue()
    return processed_data

@st.cache(suppress_st_warning=True, show_spinner = False)
def konk(corpus = None, query = None):
    """Create a concordance from a corpus"""
    # exit if corpus is empty
    if corpus.corpus.empty:
        return pd.DataFrame()
    
    conc = dh.Concordance(corpus, query, limit = 10000)
    return conc

def konks_csv(conc, corpus):
    konks = pd.merge(conc.show(n=conc.size, style=False), corpus.corpus[['urn', 'year', 'authors', 'title']], on = 'urn')
    konks = konks[['urn','year','authors', 'title', 'concordance']]
    #konks['concordance'] = konks['concordance'].apply(lambda c: c.replace('<b>', '**').replace('</b>','**'))
    #konks = konks[['link','authors','year', 'title', 'concordance']].sort_values(by='year')
    return konks.sort_values('year')

def display_konks(conc, search, size, corpus):
    konks = pd.merge(conc.show(n=int(size), style=False), corpus.corpus[['urn', 'year', 'authors', 'title']], on = 'urn')
    konks = konks[['urn','year','authors', 'title', 'concordance']]
    
    search = quote(search)
    konks['link'] = konks['urn'].apply(lambda c: f"""[{c.split('_')[2]}](https://www.nb.no/items/{c}?searchText="{search}") """)
    konks['concordance'] = konks['concordance'].apply(lambda c: c.replace('<b>', '**').replace('</b>','**'))
    konks = konks[['link','year','authors', 'title', 'concordance']].sort_values(by='year')
    return '\n\n'.join(
        [' '.join([str(x[1])] + [" **—** "] + [str(y) for y in x[2:-1]] + [" **—** " + str(x[-1])]) for x in 
         konks.sample(min(int(size), len(konks))).sort_values(by='year').itertuples()])

@st.cache(suppress_st_warning=True, show_spinner = False)
def korpus():
    df = pd.read_csv('naob.csv', header = 0, index_col = 0)
    return dh.CorpusFromIdentifiers(identifiers=list(set(df.urn.values)))


naob = korpus()
#naob = naob[naob.corpus == 'naob_hele']

image = Image.open('NB-logo-no-eng-svart.png')
st.image(image, width = 200)
st.markdown('Les mer om DH på [NBs DHLAB-side](https://nb.no/dhlab)')


st.title('Søk i NAOBs korpus')

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)
col5, col6 = st.columns(2)

with col3:
    samplesize = st.number_input("Vis maks antall konkordanser:", 150, help = "Angi maks antall konkordanser som skal vises i gangen.")

with col4:
    filename = st.text_input("Angi et filnavn for konkordansene:", "konkordanser.xlsx", help="Filen vil sannlygvis ligge i mappen ved navn Nedlastninger.")
    
with col1:
    search = st.text_input('Ord og fraser', """ leksikografi """, help= """Skriv inn ord for å finne match i avsnitt. For alternativer sett OR imellom: 'spise OR spise' men utelat anførselstegn. Grupper ord i fraser ved å omslutte dem med anførselstegn:"spise opp" vil matche når ordene følger på hverandre. Ord kan stå vilkårlig nær hverandre med nøkkelordet NEAR: NEAR(spise opp, 2) får match når ordene maks skilles med to ord. Ord med bindestrek eller punktum må settes i anførselstegn: "Nord-Norge" og "dr.art.". Om to eller flere ord skrives uten anførselstegn rundt vil det bli match i alle avsnitt som inneholder de to ordene. Trunker søke med *, for eksempel spise*.""")

with col2:
        periode = st.values = st.slider(
     'Velg en periode',
     1814, 2020, (1814, 2020))

corpus = naob
if periode != []:
    corpus_id = naob.corpus[(naob.corpus.year >= periode[0]) & (naob.corpus.year <= periode[1])]
    corpus = dh.CorpusFromIdentifiers(list(corpus_id.urn))

if not search == "":
    konks = konk(corpus, query=search)
    with col5:
        st.markdown(f"Antall konkordanser totalt:{konks.size}")
    with col6:
        
        if st.download_button(f'Last ned alle konkordansene til en Excel-fil', to_excel(konks_csv(konks, corpus)), filename, help = "CSV-formatet kan åpnes i excel og andre program"):
            
            st.write(f'Lastet ned til {filename} ')
            
    if (samplesize < konks.size):
        konkordanser = display_konks(konks, search, samplesize, corpus)

        if st.button(f"Klikk her for flere konkordanser. Viser et utvalg på {samplesize}"):
            konkordanser = display_konks(konks, search, samplesize, corpus)


    else:
        if konks.size == 0:
            st.write(f"Ingen treff")
            konkordanser = "-- ingen --"
        else:
            st.write(f"Viser alle konkordansene")
            konkordanser =  display_konks(konks, search, samplesize, corpus)

    st.markdown(konkordanser)

        
    