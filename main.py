import itertools
import getopt
import sys
import numpy as np
from urllib import response
from pytz import timezone 
import streamlit as st
import numpy as np
import pandas as pd
from st_aggrid import AgGrid
import io 
from operator import index, mod
from ssl import SSLSession
import streamlit_ext as ste
import gsheetData
import pandas as pd
from datetime import datetime
from streamlit.web.server.websocket_headers import _get_websocket_headers
import gdrive
import os
import random
import hashlib
currTime = datetime.now(timezone("Asia/Kolkata"))

try:
    opts, args = getopt.getopt(sys.argv[1:], "hg:", ["gSheetName="])
except getopt.GetoptError:
    print('main.py -g <GSheetName>')
    sys.exit(2)

gSheetName = ''

for opt, arg in opts:
    if opt == '-h':
        print('main.py -g <GSheetName>')
        sys.exit()
    elif opt in ("-g", "--gSheetName"):
        gSheetName = arg
if gSheetName == '':
    sys.exit(2)
    
sh = gsheetData.init_gsheet(gSheetName)
Message = gsheetData.get_gsheet(sh,"Message")
Banner = gsheetData.get_gsheet(sh,"BannerName")['Name'][0]
st.set_page_config(page_title=Banner)
st.image(".banner/Banner.png", caption=None, width=500, use_column_width=True, clamp=False, channels="RGB", output_format="auto")
headers = _get_websocket_headers()

username = headers.get('X-Ms-Client-Principal-Name')
if username == None:
    username = headers.get('Host')
    displayUserName = "unknown@unknown.com"
else:
    displayUserName = username
gsheetData.set_gsheet(sh,"ActivityLog",[str(currTime),username])

entry = False

UserList = gsheetData.get_gsheet(sh,"Access")
for myuser in UserList['Username']:
    if username == myuser:
        entry = True
        lineItem = UserList.loc[(UserList['Username'] == myuser)]
        flatNumber = (lineItem['FlatNumber']).to_string(index=False).strip()

outFileSuffix = currTime.strftime("%Y%m%d%w%H%M%S%f")

def renderTabContentsFromGdrive(tabNumber):
    a = gdrive.list_files(tabList[tabNumber])
    for m in a.values:
        keyHash = hashlib.md5((m[0]+str(random.random)+str(tabNumber)).encode()).hexdigest()
        if st.button(m[0],key=keyHash):
            ste.download_button("File Fetched Successfully - Click Here to Download", gdrive.get_file(m[1]), m[0])

def uploadTab():
    try:
        SheetName = gsheetData.get_gsheet(sh,"CurrentUploadFolder")['Name'][0]
    except(KeyError):
        SheetName = ""

    #uploaded_files = st.file_uploader("Choose a file to upload your",  accept_multiple_files=True)
    uploaded_file = st.file_uploader("Choose a file to upload your " + SheetName)

    if uploaded_file is not None:
        bytes_data = uploaded_file.read()
        st.write("Reading File:", uploaded_file.name)
        st.write("filename:", uploaded_file.name)
        with open(os.path.join("",uploaded_file.name),"wb") as f:
            f.write(uploaded_file.getbuffer())

        gdrive.upload_file(SheetName,os.path.join("",uploaded_file.name),flatNumber)

def voting():
    with st.form(key='my_form'):
        st.error('Vote for the appropriate option:')
        email = st.text(displayUserName + ' -  Flat Number: '+flatNumber)
        try:
            SheetName = gsheetData.get_gsheet(sh,"CurrentVote")['Name'][0]
        except(KeyError):
            SheetName = ""
        if SheetName == "":
            st.write("Nothing to vote for now")
        else:
            Options = gsheetData.get_gsheet(sh,SheetName)
            answer = []
            question = []
            for ind in Options.index:
                if (Options['Question'][ind] == ""):
                    break
                else:
                    question.append(Options['Question'][ind])
                    answer.append(st.selectbox(Options['Question'][ind],(Options['Option'][ind]).split("|"),index=0,key="Option"+str(ind)))
    
        submitted = st.form_submit_button('Submit')

        ########
        if submitted & (SheetName != ""):
            for i in range(len(question)):
                gsheetData.set_gsheet(sh,SheetName,[displayUserName,flatNumber,question[i],answer[i],str(currTime)])
            st.write("Thank you for your vote")  
def votingOutput():
        try:
            SheetName = gsheetData.get_gsheet(sh,"CurrentVote")['Name'][0]
        except(KeyError):
            SheetName = ""
        if SheetName != "":
            mydata = gsheetData.get_gsheet(sh,SheetName)
            st.dataframe(mydata, width=1500, height=1500)


if not entry:
    st.write("")
    with st.form(key='AccessRequest'):
        st.error("Sorry you don't have access. Please enter your flat number below and Submit the request for access. The Managing Committee will reach out to you for confirmation")
        email = st.text(displayUserName)
        flatNumber = st.text_input("Your Flat Number", value="",max_chars=None, key="flatNumber")
        request_access = st.form_submit_button('Request Access')
    if request_access:
        gsheetData.set_gsheet(sh,"AccessRequest",[displayUserName,flatNumber])
        st.write("Thank you. We will get back to you")

else:
    TabDF = gsheetData.get_gsheet(sh,"Tabs")

    tabList =  TabDF['TabName'].to_list()
    tabTypeList = TabDF['TabType'].to_list()
    print(tabList)
    headers = _get_websocket_headers()

    username = headers.get('X-Ms-Client-Principal-Name')
    if username == None:
        username = headers.get('Host')
        displayUserName = "unknown@unknown.com"
    else:
        displayUserName = username


    if "tabs" not in st.session_state:
        st.session_state["tabs"] = tabList

    tabs = st.tabs(st.session_state["tabs"])
    for i in range(len(tabs)):
        with tabs[i]:
            if tabTypeList[i] == "GdriveDocument":
                renderTabContentsFromGdrive(i)
            if tabTypeList[i] == "Table":
                st.dataframe(gsheetData.get_gsheet(sh,tabList[i]), width=1500, height=1500)
            if tabTypeList[i] == "Upload":
                uploadTab()
            if tabTypeList[i] == "VotingTemplate":
                voting()
            if tabTypeList[i] == "VotingResults":
                votingOutput()


    
    ###Formatting Options
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)