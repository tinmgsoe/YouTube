import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import requests, lxml, time,json, tldextract
from bs4 import BeautifulSoup
from streamlit_tags import st_tags

# Specify User Agent 
headers = {
"User-Agent":
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3538.102 Safari/537.36 Edge/18.19582"
}

def adScraper(numberOfTimes,listOfKeywords):
    st.subheader('Progress:')
    my_bar = st.progress(0)
    resultDict = {}
    progress = 0
    for keyword in listOfKeywords:
        companyList = []
        numOfTopAds = 0
        numOfBottomAds = 0
        resultDict[keyword] = {}
        absolute_top = 0 
        print(keyword)
        for i in range(numberOfTimes):
            payload = {'q': keyword}
            html = requests.get("https://www.google.com/search?q=",params=payload,headers=headers)
            status_code = html.status_code

            if status_code == 200:
                response = html.text
                soup = BeautifulSoup(response, 'lxml')
                print('----------------Top Ads-------------------')
                topAds = soup.find(id='tvcap')
                if (topAds):
                    if len(topAds.findAll('div',class_='uEierd')) > 0:
                        numOfTopAds += 1
                    absolute_top = 0
                    for container in topAds.findAll('div',class_='uEierd'):
                        try:
                            advertisementTitle = container.find('div',class_='CCgQ5 vCa9Yd QfkTvb MUxGbd v0nnCb').span.text
                        except:
                            advertisementTitle = 'N/A'

                        company = container.find('div',class_='v5yQqb').find('span',class_='x2VHCd OSrXXb nMdasd qzEoUe').text
                        company = tldextract.extract(company).domain

                        if company not in companyList:
                            companyList.append(company)
                            if absolute_top == 0:
                                resultDict[keyword][company] = {'absolute-top':1, 'top':0, 'bottom':0}
                            else:
                                resultDict[keyword][company] = {'absolute-top':0, 'top':1, 'bottom':0}
                        else:
                            if absolute_top == 0:
                                resultDict[keyword][company]['absolute-top'] += 1
                            else:
                                resultDict[keyword][company]['top'] += 1

                        productDescription = container.find('div',class_='MUxGbd yDYNvb lyLwlc').text

                        print(advertisementTitle)
                        print(company)
                        print(productDescription)
                        print()
                        absolute_top += 1
                    progress += (0.5/(len(listOfKeywords)*numberOfTimes))
                    my_bar.progress(progress)
                    
                
                time.sleep(5)
                print('------------------------------------------')
                print('----------------Bottom Ads-------------------')
                bottomAds = soup.find(id='bottomads')
                if (bottomAds):
                    if len(bottomAds.findAll('div',class_='uEierd')) > 0:
                        numOfBottomAds += 1
                    for container in bottomAds.findAll('div',class_='uEierd'):
                        try:
                            advertisementTitle = container.find('div',class_='CCgQ5 vCa9Yd QfkTvb MUxGbd v0nnCb').span.text
                        except:
                            advertisementTitle = 'N/A'
                            
                        company = container.find('div',class_='v5yQqb').find('span',class_='x2VHCd OSrXXb nMdasd qzEoUe').text
                        company = tldextract.extract(company).domain

                        if company not in companyList:
                            companyList.append(company)
                            resultDict[keyword][company] = {'absolute-top':0, 'top':0, 'bottom':1}
                        else:
                            resultDict[keyword][company]['bottom'] += 1

                        productDescription = container.find('div',class_='MUxGbd yDYNvb lyLwlc').text

                        print(advertisementTitle)
                        print(company)
                        print(productDescription)
                        print()
                    progress += (0.5/(len(listOfKeywords)*numberOfTimes))
                    my_bar.progress(round(progress,1))

                with open("output.html","w") as file:
                    file.write(str(soup))



        keys = list(resultDict[keyword].keys())
        for name in ['bottom','top','absolute-top']:
            keys.sort(key=lambda k: resultDict[keyword][k][name],reverse=True)

        resultDict[keyword]['top performers'] = keys
        resultDict[keyword]['total top ads'] = numOfTopAds
        resultDict[keyword]['total bottom ads'] = numOfBottomAds

    print(json.dumps(resultDict,indent=4))
    st.success('Google Ads Scraping completed successfully.')
    return resultDict

def jsonToDataFrame(resultDict,listOfKeywords):
    resultList = []
    for keyword in listOfKeywords:
        if (resultDict[keyword]["top performers"] != []):
            for company in resultDict[keyword]["top performers"]:
                topPercentage = 0
                bottomPercentage = 0
                if resultDict[keyword]["total top ads"] != 0:
                    topPercentage = round((resultDict[keyword][company]["top"]+resultDict[keyword][company]["absolute-top"])/resultDict[keyword]["total top ads"] * 100,1)
                if resultDict[keyword]["total bottom ads"] != 0:
                    bottomPercentage = round(resultDict[keyword][company]["bottom"]/resultDict[keyword]["total bottom ads"] * 100,1)

                resultList.append(
                    [
                    keyword,
                    company,
                    resultDict[keyword][company]["absolute-top"],
                    resultDict[keyword][company]["top"],
                    resultDict[keyword][company]["bottom"],
                    topPercentage,
                    bottomPercentage,
                    round((resultDict[keyword]["total top ads"] + resultDict[keyword]["total bottom ads"])/(numberOfTimes*2) * 100,1),
                    ]
                )
        else:
            resultList.append([keyword,None,0,0,0,0,0,0])

    df = pd.DataFrame(resultList,columns=["Keyword","Company","absolute-top","top","bottom","top(%)","bottom(%)","Keyword Ads Percentage(%)"])
    return df

def displayScraperResult():
    st.title(':bar_chart: Analysis Visualizer')


# title
st.title(":male-detective: Google Ads Keyword Dashboard")

numberOfTimes = st.slider('How many times do you want this keyword scraping to be run?', 1, 100, 10)
listOfKeywords = ["nft","crypto","etf"]

col1, col2 = st.columns(2)

with col1:
    chosen_keywords = st_tags(
                label='Add Keywords here!',
                text='Press enter to add more',
                value=listOfKeywords,
                suggestions=['blockchain', 'web 3.0', 'insurance', 'loans'],
                maxtags=10,
                key="aljnf"
            )
with col2:
    st.caption('Current List of Keywords')
    st.write((chosen_keywords))


submitted = st.button("Submit")
    
if submitted:
    st.write('Google Ads Scraping for the following keywords:',str(chosen_keywords),' for ', numberOfTimes,' times.')

    resultDict = adScraper(numberOfTimes,chosen_keywords)
    rawOutput = jsonToDataFrame(resultDict,chosen_keywords)
    # rawOutput.to_csv('AdScrapeResult.csv',index=False)    
    

displayResult = st.button("Display Result")
if displayResult:
    displayScraperResult()







