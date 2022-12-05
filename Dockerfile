FROM ubuntu:22.04
ENV DEBIAN_FRONTEND noninteractive
ENV QT_QPA_PLATFORM=offscreen
RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
RUN apt update
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt update 
RUN apt install python3.8 -y
RUN apt install python3-pip -y
RUN pip3 install pandas
RUN add-apt-repository universe -y
RUN apt-get update
RUN apt-get upgrade -y
RUN pip3 install streamlit==1.14
RUN pip3 install streamlit-ext==0.1.4
RUN pip3 install streamlit-option-menu
RUN pip3 install streamlit-aggrid
RUN pip3 install jinja2==3.0.1
RUN apt install git -y
RUN pip3 install gspread==3.1.0
RUN pip3 install google-auth==2.12.0
RUN pip3 install google-auth-oauthlib
RUN pip3 install apiclient
RUN pip3 install oauth2client
RUN pip3 install google-api-python-client
RUN pip3 install hydralit
RUN pip3 install tabulate
RUN echo 16
RUN git clone https://github.com/mahendrachandrasekhar/SocietyApp.git
RUN mkdir .banner
COPY /.banner/Banner.png /SocietyApp/.banner/Banner.png
RUN mkdir .config
RUN cd .config
RUN mkdir gspread
RUN cd gspread
COPY /.config/gspread/service_account.json /SocietyApp/.config/gspread/service_account.json
COPY /.config/gspread/token.pickle /SocietyApp/.config/gspread/token.pickle
WORKDIR /SocietyApp
ENTRYPOINT ["streamlit", "run", "--server.port=8502", "--server.address=0.0.0.0","--server.enableXsrfProtection=false","main.py"]
EXPOSE 8502
