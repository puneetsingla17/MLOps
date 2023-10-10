import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import regex as re
import faiss
import pickle
from rapidfuzz.distance import DamerauLevenshtein,Levenshtein,Hamming,Jaro

pat1="[a-z][0-9][a-z]\s[0-9][a-z][0-9]"
pat2="[a-z][0-9][a-z][0-9][a-z][0-9]"
f=open("static/staticfiles.pkl",'rb')
d1,onehouse_pincode,vectorizer=pickle.load(f)
f.close()

title_temp="""
<div style ="background-color:#46405f;margin:5px;padding:5px"> 
<h4 style="color:white;text-align:center">{}</h4>
</div>
"""

title_temp1="""
<div style ="background-color:#46405f;margin:5px;padding:5px"> 
<h4 style="color:white;text-align:center">{} ! Score {}</h4>
</div>
"""

postalcode_state={"on":["k","l","m","n","p"],"mb":['r']}
postal_list=list(d1.keys())
count=[len(d1[k][1]) for k in postal_list]
df=pd.DataFrame(data={"PostalCode":postal_list,"Counts":count})

regex = r"[!\"#\$%&\(\)\*\+,-\./:;<=>\?@\[\\\]\^_{\|}~]"

def main():
    algo=st.sidebar.radio("Select algorithm",['FuzzyWuzzy',"Tfidf-Faiss","Rapidfuzz","View"])
#     if algo=="Rapidfuzz":
#         algo1=st.sidebar.selectbox("Select Type",['Levenshtein','DamerauLevenshtein','Hamming','Jaro'])
#     st.header("Address Matching")
#     postalcode=""
#     address=st.text_input("Enter your Address",placeholder="Type Here")
#     housepat=r'^(\d+)\s*[a-z]+'
#     st.text(address)
#     address=address.lower()
    
    if algo=="View":
        st.dataframe(df.sort_values("Counts",ascending=False))
        postc=st.text_input("Enter Postal Code",placeholder="Type Here")
        if postc in d1:
            st.dataframe(d1[postc][1])
        else:
            st.error("Please enter postalcodes present in the data")
    else: 
        if algo=="Rapidfuzz":
            algo1=st.sidebar.selectbox("Select Type",['Levenshtein','DamerauLevenshtein','Hamming','Jaro'])
        st.header("Address Matching")
        postalcode=""
        address=st.text_input("Enter your Address",placeholder="Type Here")
        housepat=r'^(\d+)\s*[a-z]+'
        st.text(address)
        
        # preprocessing on country
        address=re.sub(r"[\s,][cC][aA][\s,]","",address)
        address=re.sub(r"[\s,][cC][aA][\s,]*$","",address)
        address=address.lower()
        address=address.replace("canada","")
        address=address.replace("ontario","")
        address=address.replace(" on"," ")
        address=re.sub(regex,"",address)
        address=re.sub("\s+"," ",address)
        st.text("Preprocessed Address:-"+address)
        
        if st.button("Submit"):
            if len(re.findall(pat1,address))!=0:
                postalcode=re.findall(pat1,address)[0]

            elif len(re.findall(pat2,address))!=0:

                postalcode=re.findall(pat2,address)[0]
                postalcode=postalcode[:3]+" "+postalcode[3:]

            else:
                st.error(" Please include postalcode inside the Address")


        if postalcode and len(postalcode)==7:
            postalcode=postalcode.lower()

            if algo=="FuzzyWuzzy":
                from fuzzywuzzy import fuzz
                from fuzzywuzzy import process
                if postalcode in d1:
                    query=address.replace(postalcode,"")
                    if len(query)<5:
                        st.error("Please enter valid address")
                    else:
                        result=process.extract(query,d1[postalcode][1].to_list())
                        for s in result:
                            st.markdown(title_temp1.format(s[0]+","+postalcode,s[1]),unsafe_allow_html=True)

                else:
                    st.error("Data with postalcode is not present")


            elif algo=="Rapidfuzz":
                if postalcode in d1:
                    query=address.replace(postalcode,"")
                    if len(query)<5:
                        st.error("Please enter valid address")
                    else:
                        if algo1=='Levenshtein':
                            result=sorted([(k,Levenshtein.normalized_similarity(query,k)) for k in d1[postalcode][1].to_list()],key=lambda x:x[1],reverse=True)[:5]
                            for s in result:
                                st.markdown(title_temp1.format(s[0]+","+postalcode,s[1]),unsafe_allow_html=True)
                        elif algo1=='DamerauLevenshtein':
                            result=sorted([(k,DamerauLevenshtein.normalized_similarity(query,k)) for k in d1[postalcode][1].to_list()],key=lambda x:x[1],reverse=True)[:5]
                            for s in result:
                                st.markdown(title_temp1.format(s[0]+","+postalcode,s[1]),unsafe_allow_html=True)

                        elif algo1=='Hamming':
                            result=sorted([(k,Hamming.normalized_similarity(query,k)) for k in d1[postalcode][1].to_list()],key=lambda x:x[1],reverse=True)[:5]
                            for s in result:
                                st.markdown(title_temp1.format(s[0]+","+postalcode,s[1]),unsafe_allow_html=True)

                        else:
                            result=sorted([(k,Jaro.normalized_similarity(query,k)) for k in d1[postalcode][1].to_list()],key=lambda x:x[1],reverse=True)[:5]
                            for s in result:
                                st.markdown(title_temp1.format(s[0]+","+postalcode,s[1]),unsafe_allow_html=True)
                else:
                    st.error("Data with postalcode is not present")

            else:

                if postalcode in d1:
                    query=address.replace(postalcode,"")
                    if len(query)<5:
                        st.error("Please enter valid address")
                    else:
                        index=d1[postalcode][0]
                        query=vectorizer.transform([query]).toarray()
                        istances,neighbours=index.search(query,5)
                        for s in d1[postalcode][1].values[neighbours][0]:
                            st.markdown(title_temp.format(s+","+postalcode),unsafe_allow_html=True)

                elif postalcode in onehouse_pincode:
                    st.write(onehouse_pincode[postalcode])

                else:
                    st.error("Data with postalcode is not present")
    
            

if __name__=="__main__":
    main()