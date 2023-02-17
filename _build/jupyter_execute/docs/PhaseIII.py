#!/usr/bin/env python
# coding: utf-8

# # Final Project Phase 3 Summary
# This Jupyter Notebook (.ipynb) will serve as the skeleton file for your submission for Phase 3 of the Final Project. Complete all sections below as specified in the instructions for the project, covering all necessary details. We will use this to grade your individual code (Do this whether you are in a group or not). Good luck! <br><br>
# 
# Note: To edit a Markdown cell, double-click on its text.

# 

# ## Jupyter Notebook Quick Tips
# Here are some quick formatting tips to get you started with Jupyter Notebooks. This is by no means exhaustive, and there are plenty of articles to highlight other things that can be done. We recommend using HTML syntax for Markdown but there is also Markdown syntax that is more streamlined and might be preferable. 
# <a href = "https://towardsdatascience.com/markdown-cells-jupyter-notebook-d3bea8416671">Here's an article</a> that goes into more detail. (Double-click on cell to see syntax)
# 
# # Heading 1
# ## Heading 2
# ### Heading 3
# #### Heading 4
# <br>
# <b>BoldText</b> or <i>ItalicText</i>
# <br> <br>
# Math Formulas: $x^2 + y^2 = 1$
# <br> <br>
# Line Breaks are done using br enclosed in < >.
# <br><br>
# Hyperlinks are done with: <a> https://www.google.com </a> or 
# <a href="http://www.google.com">Google</a><br>

# # Data Collection and Cleaning
# 
# 
# Transfer/update the data collection and cleaning you created for Phase II below. You may include additional cleaning functions if you have extra datasets. If no changes are necessary, simply copy and paste your phase II parsing/cleaning functions.
# 

# In[1]:


import pandas as pd
import numpy as np
import requests, time, re, json
from bs4 import BeautifulSoup
import plotly.express as px
import plotly.graph_objects as go

from pprint import pprint


# ## Web Collection Requirement #1
# 

# In[2]:


def html_parser(url_list):
    full_dict = {}
    for url in url_list:
        soup=BeautifulSoup(open(url))
        table = soup.find_all('td', {'class': ['hc_rank', 'hc_name', 'hc_value hc_selected_v']})
        adict = {}
        for i in range(0,len(table), 3):
            adict[table[i].text] = table[i+1].text , table[i+2].text
        key = url[:-5]
        full_dict[key] = adict
    return(full_dict)

    
#USE THE BELOW STATEMENT TO EXPLAIN WHY WE ARE USING THE HTML THIS WAY    
#the website we were going to use had a forbidden error, so we downloaded the html files and implemented the beautiful soup we would have.


############ Function Call ############
html_parser(['KidneyDisease.html', 'Malaria.html', 'SkinCancer.html',])


# In[3]:


data=html_parser(['KidneyDisease.html', 'Malaria.html', 'SkinCancer.html',])
kidney_df = pd.DataFrame(data['KidneyDisease']).transpose().reset_index()
kidney_df['index'] = kidney_df['index'].astype(int)
kidney_df.sort_values(by='index', inplace=True)
kidney_df.rename(columns = {'index': 'Rank', 0: 'Country', 1: 'Rate'}, inplace=True)
kidney_df.set_index('Rank', inplace=True)
kidney_df


# In[4]:


data=html_parser(['KidneyDisease.html', 'Malaria.html', 'SkinCancer.html',])
malaria_df = pd.DataFrame(data['Malaria']).transpose().reset_index()
malaria_df['index'] = malaria_df['index'].astype(int)
malaria_df.sort_values(by='index', inplace=True)
malaria_df.rename(columns = {'index': 'Rank', 0: 'Country', 1: 'Rate'}, inplace=True)
malaria_df.set_index('Rank', inplace=True)
malaria_df


# In[5]:


data=html_parser(['KidneyDisease.html', 'Malaria.html', 'SkinCancer.html',])
cancer_df = pd.DataFrame(data['SkinCancer']).transpose().reset_index()
cancer_df['index'] = cancer_df['index'].astype(int)
cancer_df.sort_values(by='index', inplace=True)
cancer_df.rename(columns = {'index': 'Rank', 0: 'Country', 1: 'Rate'}, inplace=True)
cancer_df.set_index('Rank', inplace=True)
cancer_df


# In[6]:


writer = pd.ExcelWriter("Diseases.xlsx")
kidney_df.to_excel(writer, sheet_name = "Kidney Disease")
malaria_df.to_excel(writer, sheet_name = "Malaria")
cancer_df.to_excel(writer, sheet_name = "Skin Cancer")
writer.save()


# ## Web Collection Requirement \#2
# 

# In[7]:


def csv_parser():
    data = pd.read_csv('worldcities.csv',on_bad_lines='skip',delimiter=';')
    data=data.drop(['Geoname ID','ASCII Name','LABEL EN','Alternate Names','Feature Class',
                    'Feature Code','Country Code 2','Admin1 Code','DIgital Elevation Model',
                    'Admin2 Code','Admin3 Code','Admin4 Code','Elevation','Timezone',
                    'Modification date',],axis=1)
    lat_long = data['Coordinates'].str.split(',', expand=True)
    data['Latitude'],data['Longitude']=lat_long.values.T
    data.drop(['Coordinates'],axis=1,inplace=True)
    data.rename(columns = {'Country name EN': 'Country'}, inplace = True)
    code_dict = extra('https://sustainablesources.com/resources/country-abbreviations/')
    for i in range(len(data)):
        if data.loc[i,'Country'] is np.nan:
            try:
                country = code_dict[data.loc[i,'Country Code'].lower()]
                data.loc[i,'Country'] = country  
            except:
                continue

    country = data['Country'].str.split(',', expand=True)
    data['Country'],data['else']=country.values.T
    countries1 = set([data.loc[i,'Country'] for i in range(len(data))] )

    kd = pd.read_excel('Diseases.xlsx', sheet_name = 'Kidney Disease')
    countries = [kd.loc[i,'Country'] for i in range(len(kd))]    

    uncommon = [data.loc[i,'Country'] for i in range(len(data)) if data.loc[i,'Country'] not in countries]
    uncommon = list(set([country for country in uncommon if not pd.isna(country)]))
    data = data.set_index('Country')
    data = data.drop(uncommon, axis=0)
    data = data.reset_index()
    data.drop('else', axis =1, inplace=True)

    count = len(set([data.loc[i,'Country'] for i in range(len(data))]))
    data[["Latitude", "Longitude"]] = data[["Latitude", "Longitude"]].apply(pd.to_numeric)
    total_pop = pd.DataFrame(data.groupby("Country")['Population'].sum()).reset_index()
    avg_lat = pd.DataFrame(data.groupby("Country")['Latitude'].mean()).reset_index()
    avg_lon = pd.DataFrame(data.groupby("Country")['Longitude'].mean()).reset_index()

    for i in range(len(avg_lat)):
        avg_lat.loc[i,'Latitude'] = round(avg_lat.loc[i,'Latitude'] ,5)
    for i in range(len(avg_lat)):
        avg_lon.loc[i,'Longitude'] = round(avg_lon.loc[i,'Longitude'] ,5)

    new_data = total_pop.set_index('Country').join(avg_lat.set_index('Country')).join(avg_lon.set_index('Country'))
    new_data.to_csv('clean_countries.csv')

    return new_data

############ Function Call ############
csv_parser()


# ## Web Collection Requirement #3

# In[6]:


def api_parser():
    data = pd.read_csv('clean_countries.csv') 
    new = data.loc[:, ['Latitude', 'Longitude']]
    coordinates = [tuple(new.iloc[row]) for row in range(int(len(new)))]
    data_dict = {}
    for i in range(len(coordinates)):
        url = f'https://api.open-meteo.com/v1/forecast?latitude={coordinates[i][0]}&longitude={coordinates[i][1]}
        &daily=weathercode,temperature_2m_max,temperature_2m_mi,precipitation_sum,rain_sum,shortwave_radiati         on_sum&timezone=auto&start_date=2022-06-12&end_date=2022-12-06'
        r=requests.get(url)
        weather = r.json()
        time.sleep(1)
        data_dict[data.loc[i, 'Country']] = weather
    
    with open('api_dict.json', 'w') as f:
        json.dump(data_dict, f)
    return data_dict
  
pass

# It usually takes 5 minutes to run

############ Function Call ############
api_parser()


# In[8]:


with open('api_dict.json') as f:
    data_dict = json.load(f)

country_dict = {}
for country,nested in data_dict.items():
    country_dict[country] = {}
    if nested == {"reason": "Invalid timezone", "error": True}:
        continue
    else:
        for key in nested['daily']:
            if key == 'time':
                continue
            else:
                country_dict[country][key] = round(sum(nested['daily'][key])/178,2)


with open('avg_api.json', 'w') as f:
    json.dump(country_dict, f)


pprint(country_dict)


# ## Additional Dataset Parsing/Cleaning Functions

# In[8]:


def extra(url):
    r=requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')  
    table=soup.find_all('tr')[2:250]
    code_dict = {}
    str_list = []
    for row in table:
        str_list.append(row.text)
    for country in str_list:
        code_dict[country[0:2].lower()] = country[2:].split(',')[0]
    return code_dict

pass

    
############ Function Call ############
extra('https://sustainablesources.com/resources/country-abbreviations/')


# #Inconsistency Revisions
#  **If you were requested to revise your inconsistency section from Phase II, enter your responses here. Otherwise, ignore this section.**
# 
# For each inconsistency (NaN, null, duplicate values, empty strings, etc.) you discover in your datasets, write at least 2 sentences stating the significance, how you identified it, and how you handled it.
# 
# 1. 
# 
# 2. 
# 
# 3. 
# 
# 4. (if applicable)
# 
# 5. (if applicable)

# ## Data Sources
# 
# Include sources (as links) to your datasets. If any of these are different from your sources used in Phase II, please <b>clearly</b> specify.
# 
# *   Web Collection #1 Source (HTML): https://www.worldlifeexpectancy.com/world-health-rankings 
# *   Web Collection #2 Source (CSV): https://public.opendatasoft.com/explore/dataset/geonames-all-cities-with-a-population-1000/export/?disjunctive.cou_name_en&sort=name
# *   Web Collection #3 Source (API): https://api.open-meteo.com/v1/forecast?latitude={latitudue}&longitude={longitude}&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,shortwave_radiation_sum&timezone=auto&past_days=92
# *   Extra Web Collection Source (HTML): https://sustainablesources.com/resources/country-abbreviations/
# 

# # Data Analysis
# For the Data Analysis section, you are required to utilize your data to complete the following:
# 
# *   Create at least 5 insights
# *   Generate at least 3 data visualizations
# *   Export aggregated data to at least 1 summary file 
# 
# Create a function for each of the following sections mentioned above. Do not forget to fill out the explanation section for each function. 
# 
# Make sure your data analysis is not too simple. Performing complex aggregation and using modules not taught in class shows effort, which will increase the chance of receiving full credit. 

# # Graphical User Interface (GUI) Implementation
# If you decide to create a GUI for Phase II, please create a separate Python file (.py) to build your GUI. You must submit both the completed PhaseII.ipynb and your Python GUI file.

# ## Insights

# In[2]:


# Which are the ten countries with the highest shortwave radiation sum? Which are the ones with a higher 
# skin cancer rate? Do these countries overlap?  SHORTWAVE RADIATION.

def insight1():
    
    with open('avg_api.json') as f:
        data = json.load(f)
    sc = pd.read_excel('Diseases.xlsx', sheet_name = 'Skin Cancer')

    country_data = [(country, data[country]['shortwave_radiation_sum']) for country in data if data[country]!={}]
    country_data = sorted(country_data, key = lambda x: x[1], reverse = True)
    
    sc_data = [(sc.loc[i,'Country'], sc.loc[i,'Rate']) for i in range(len(sc))]
    sc_data = sorted(sc_data, key = lambda x: x[1], reverse = True)
    
    country_list = [country for country,swr in country_data][:10]
    sc_list = [country for country,sc_rate in sc_data][:10]
    
    common = []
    for country in country_list:
        if country in sc_list:
            common.append(country)
        
    print('Countries with the highest shortwave radiation sum: ' + str(sorted(country_list))+'\n')
    print('Countries with the highest skin cancer rates: ' + str(sorted(sc_list))+'\n')
    print('Countries in common: ' + str(sorted(common)))


############ Function Call ############
insight1()


# ### Insight 1 Explanation
# 
# For the first insight, we wanted to check which countries have the highest short-wave radiation and highest skin cancer rates to check if there is a correlation between these two variables. For the code, we first read the 'avg_api.json', and the skin cancer sheet from the 'Diseases.xlsx' excel file. Then, we created separate lists of the countries with the ten highest shortwave radiation sum and the highest skin cancer rates. Finally, we compared the two lists to find which countries have both high shortwave radiation sum and high skin cancer rates. The overlapping countries between these lists were Malawi and Namibia which demonstrates that there is a correlation between countries having high shortwave radiation and skin cancer rates.
# 

# In[3]:


# Are the countries with the highest temperature the ones with the least precipitation? 
# Which are these countries? HIGHEST TEMPERATURE AND PRECIPITATION. Api 

def insight2():
    with open('avg_api.json') as f:
        data = json.load(f)
    
    countries = [(country, data[country]['temperature_2m_max'], data[country]['precipitation_sum']) for country in data if data[country]!={}]

    
    temp = {i:tup[:2] for i,tup in enumerate(sorted(countries, key = lambda x: x[1], reverse=True))}
    prec = {i:tup[:3:2] for i,tup in enumerate(countries)}

    tempdf= pd.DataFrame(temp, index = ['Country', 'Temperature']).transpose()
    precdf = pd.DataFrame(prec, index = ['Country', 'Precipitation']).transpose()
    df = tempdf.set_index('Country').join(precdf.set_index('Country'))
    df['Difference'] = df.apply(lambda x: x['Temperature'] - x['Precipitation'], axis=1)


    return(df)

############ Function Call ############
insight2()


# ### Insight 2 Explanation
# 
# For the second insight, we wanted to check if the countries that have the highest temperatures were the same as the ones that have the least precipitation as there is a lot of debate on whether precipitation relates to lower temperatures. For this code, we loaded the avg API JSON file into the variable data and then created a list of tuples with each country, its maximum temperature, and its precipitation sum. Then we created 2 dictionaries: one with the temperatures for each country, and one with the precipitation. We turned each dictionary into a data frame and joined them together. Then, we found the difference between temperature and precipitation to see if there were major differences. When the difference column for a country shows a larger number, greater than 30, for example, it means the temperature rate is way higher than the precipitation rate, which shows that these countries have low precipitation and high temperatures.
# 

# In[4]:


# How does living near the Equator relates to higher kidney disease rates (hence, higher disease transmission)?
# near equator = latitude close to 0

def insight3():
    df = pd.read_csv('clean_countries.csv')
    sc = pd.read_excel('Diseases.xlsx', sheet_name = 'Kidney Disease')

    
    close_countries = [df.loc[i,'Country'] for i in range(len(df)) if abs(df.loc[i,'Latitude'])<=2]
    far_countries = [df.loc[i,'Country'] for i in range(len(df)) if abs(df.loc[i,'Latitude'])>=57]
    
    kd_rates1 = [(sc.loc[i,'Country'],sc.loc[i,'Rate']) for i in range(len(sc)) if sc.loc[i,'Country'] in close_countries]
    kd_rates2 = [(sc.loc[i,'Country'],sc.loc[i,'Rate']) for i in range(len(sc)) if sc.loc[i,'Country'] in far_countries]
    
    print('Countries near the equator:                  Avg. Kidney Disease Rate: '+str(round(sum([num for country,num in kd_rates1])/len(kd_rates1),2)))
    pprint(kd_rates1)
    print('\nCountries far from the equator:              Avg. Kidney Disease Rate: '+str(round(sum([num for country,num in kd_rates2])/len(kd_rates2),2)))
    pprint(kd_rates2)
    
############ Function Call ############
insight3()


# ### Insight 3 Explanation
# 
# For the third insight, we wanted to check if countries near the equator, which have latitudes close to 0, are related to having higher kidney disease rates. We first read two datasets, the clean countries CSV and the kidney disease sheet from the excel file. Then we created two separate lists containing the countries near the equator and countries far from the equator respectively. We then created A third and fourth list which contains the country and its kidney disease rate for the countries in the close countries list and the countries in the far countries list. Finally, we calculated the average kidney disease rates for these countries. The results show that the average kidney disease rate for countries near the Equator is almost 32%, while for countries far from the Equator, it’s around 4%. This shows that countries located near the Equator have a higher kidney disease rate.
# 

# In[5]:


# How many people are affected by Malaria Disease per country? 

def insight4():
    df = pd.read_csv('clean_countries.csv').set_index('Country')
    sc = pd.read_excel('Diseases.xlsx', sheet_name = 'Malaria')

    data_dict = {sc.loc[i,'Country']:((sc.loc[i,'Rate']),) for i in range(len(sc)) if sc.loc[i,'Rate']!= 0}
    
    sc.set_index('Country', inplace=True)
    
    for country in data_dict:
        try:
            data_dict[country] += (int(df.loc[country,'Population']),)
        except:
            data_dict[country] += ('N/A',)
    
    data = [(country,tup[0],tup[1]) for country,tup in data_dict.items() if 'N/A'!=tup[1]]
    data = sorted(data, key = lambda x: x[1], reverse=True)
    df = pd.DataFrame(data, columns = ['Country', 'Malaria Rate', 'Population'])
    
    df['People Affected'] = df.apply(lambda x: round((x['Malaria Rate']/100) * x['Population'],2), axis=1)
    df['Percentage of Total'] = df.apply(lambda x: str(round(x['People Affected']/round(sum([df.loc[i,'People Affected'] for i in range(len(df))]))*100,2))+'%', axis=1)
    
    df.set_index('Country', inplace= True)

    return df

############ Function Call ############
insight4()


# ### Insight 4 Explanation
# 
# For this insight, we wanted to find how many people were affected with malaria disease in each country, and subsequently the percentage by country of the total people affected with the disease. For the code, we first read the clean countries CSV and the malaria sheet from the excel file. Then, we created a dictionary in which each key is a country and each value is a tuple containing the malaria rate and population, skipping the country if the rate was zero, as this wouldn’t give us any important information. Afterward, we converted the dictionary into a list of tuples, removing all countries with nan population, and then sorted the data by malaria rate from highest to lowest. We put this into a data frame and then calculated the number of people affected by malaria in each country, and the percentage of the total affected people for each country. We found that the percentage of people affected proportionally is really high in some countries that have a lower malaria disease rate. For example, in the top 1 country with a malaria rate of 61, Sierra Leone, only 1.52% of people were affected, whereas in Nigeria, with a malaria rate of 34, 27% of people were affected.
# 

# In[6]:


# What are the kidney disease rates of the countries that have dusty air conditions or sand storms 
# (weather codes between 06-09 and 30-35)? 

def rate(kd_rate):
    if kd_rate>=25:
        return 'High'
    elif kd_rate>10:
        return 'Medium'
    else:
        return 'Low'
    
def insight5():
    with open('avg_api.json') as f:
        data = json.load(f)
    kd = pd.read_excel('Diseases.xlsx', sheet_name = 'Kidney Disease')
    
    clean_data = {country:nested for country,nested in data.items() if nested!={}}
    country_list = [country for country in clean_data if (clean_data[country]['weathercode']>=6 and clean_data[country]['weathercode']<=9) or (clean_data[country]['weathercode']>=30 and clean_data[country]['weathercode']<=35)]

    rates = [(kd.loc[i,'Country'],kd.loc[i,'Rate']) for i in range(len(kd))if kd.loc[i,'Country'] in country_list]
    df = pd.DataFrame(rates, columns = ['Country', 'KD Rate'])
    df["Evaluation"] = df.apply(lambda x : rate(x["KD Rate"]), axis = 1)
    df.set_index('Country', inplace=True)
   
    return df

############ Function Call ############
insight5()


# ### Insight 5 Explanation
# 
# For the fifth insight, we wanted to know what are the kidney disease rates of the countries that have dusty air conditions and sandstorms to check if this affects kidney disease rates. This code creates a data frame that contains the average Kidney Disease rate for countries with weather codes between 6 and 9 and 30 and 35 (which represent dusty air conditions). The function 'rate()' is a helper function that assigns a label to the Kidney Disease rate based on its value: high, medium, or low. With the function 'insight5()' we then created a dataframe from the data loaded from the 'avg_api’ JSON file and the kidney disease sheet from the excel, filtering out countries with the desired weather code, and creating a new column 'Evaluation' which assigns the label to each Kidney Disease rate. We can see that countries with dusty air conditions and sandstorms such as Nicaragua, Pakistan, and Ecuador also have very high kidney disease rates, above 35. However, some of the countries with these weather codes do not have high kidney disease rates such as Tajikistan', 'Italy', and 'Hungary with kidney disease rates between 3 and 8. 
# 

# In[7]:


# EXTRA

# Which country/ies are in the top 20 of at least 2 diseases?

def extra():

    kd = pd.read_excel('Diseases.xlsx', sheet_name = 'Kidney Disease')
    m = pd.read_excel('Diseases.xlsx', sheet_name = 'Malaria')
    sc = pd.read_excel('Diseases.xlsx', sheet_name = 'Skin Cancer')
    
    top20_kd = sorted([kd.loc[i,'Country'] for i in range(20)])
    top20_m = sorted([m.loc[i,'Country'] for i in range(20)])
    top20_sc = sorted([sc.loc[i,'Country'] for i in range(20)])

    common = []
    for country in top20_kd:
        if country in top20_m or country in top20_sc:
            common.append(country)
    for country in top20_m:
        if country in top20_kd or country in top20_sc:
            common.append(country)

    print(sorted(common))
    
    
############ Function Call ############
extra()


# ### Extra Insight Explanation
# 
# We wanted to find which country or countries are in the top twenty for at least two diseases. We first read the excel file to extract the top 20 countries from three sheets: Kidney Disease, Malaria, and Skin Cancer. Then, we stored them in three different lists: top20_kd, top20_m, and top20_sc respectively. Finally, we iterated through each list and compared them to the other lists to find any countries that appear in at least 2 lists. In our common list, we can see that six countries overlap between the top20_kd, top20_m, and top20_sc lists. These countries are 'Angola', 'Lesotho', 'Malawi', 'Mozambique', 'Swaziland', and 'Togo'. 
# 

# ## Data Visualizations

# In[2]:


def visual1():
    csv = pd.read_csv('clean_countries.csv')
    with open('avg_api.json') as f:
        data = json.load(f)
    
    swr = [(country, data[country]['shortwave_radiation_sum']) for country in data if data[country]!={}]
    swr = pd.DataFrame(swr, columns =['Country', 'shortwave_radiation_sum'])
    
    df = csv.set_index('Country').join(swr.set_index('Country'))
    
    fig = px.density_mapbox(df, lat='Latitude', lon='Longitude', z='shortwave_radiation_sum', radius=30,
                        center=dict(lat=25, lon=18), zoom=0.62,
                        mapbox_style="stamen-terrain", labels = {'shortwave_radiation_sum': 'Radiation'},
                           )
    fig.update_layout(
    title={
        'text': "Shortwave Radiation Sum per Country",
        'y':0.95,
        'x':0.48,
        'xanchor': 'center',
        'yanchor': 'top'},font=dict(
        family="Khmer MN",
        size=18,
        color="RebeccaPurple"))

    fig.show()

############ Function Call ############
visual1()


# ### Visualization 1 Explanation
# 
# This code is responsible for showing a map of the average shortwave radiation sum per country. We first read the 'clean_countries.csv', and the 'avg_api.json' file. Then, we created a list of tuples using the data from the JSON file, containing the country, and its shortwave radiation sum. Then, we stored this information in the swr data frame. Afterward, we joined the swr data frame with the clean countries data frame and created a density map from the data using plotly's library, px.density_mapbox(), using the coordinates and the shortwave radiation sum per country.
# 
# We wanted to do this to have a visual of the highest shortwave radiation countries. By the side of the graph we can see the radiation bar which represents the levels of shortwave radiation and the colors that represent each range of radiation on top of the map. Countries with the highest shortwave radiation are covered by yellow, orange color. Countries with average radiation rates are colores in a burgundy color and the ones with low radiation rates are colored in purple or blue. With this visualization we can see that that countries near the Equator have higher shortwave radiation. We can also notice that most of Africa and countries in Eastern Europe and the Middle East also have high radiation rates. 
# 

# In[3]:


def visual2():
    
    kd = pd.read_excel('Diseases.xlsx', sheet_name = 'Kidney Disease')
    kd.rename(columns = {'Rank': 'KD Rank', 'Rate': 'KD Rate'}, inplace = True)
    m = pd.read_excel('Diseases.xlsx', sheet_name = 'Malaria')
    m.rename(columns = {'Rank': 'M Rank', 'Rate': 'M Rate'}, inplace = True)
    sc = pd.read_excel('Diseases.xlsx', sheet_name = 'Skin Cancer')
    sc.rename(columns = {'Rank': 'SC Rank', 'Rate': 'SC Rate'}, inplace = True)
    
    pop = pd.read_csv('clean_countries.csv')
    pop = pop[['Country', 'Population']]

    df = kd.set_index('Country').join(m.set_index('Country').join(sc.set_index('Country')).join(pop.set_index('Country')))
    
    df = df.dropna(inplace = False, axis = 0).reset_index()
    df = df[df['KD Rank']<=100]
    df = df[df['M Rank']<=100]
    df = df[df['SC Rank']<=100]
    
    fig = px.scatter_3d(df, x='KD Rate', y='M Rate', z='SC Rate',
              color='Country',size = 'Population',size_max=100)
    fig.update_layout(title={'text':'Top 100 Countries:<br>Kidney Disease, Malaria and Skin Cancer Rates',
                             'y':0.92,
                             'x':0.47,
                             'xanchor': 'center',
                             'yanchor': 'top'},
                      dragmode='select',
                      width=900,
                      height=700,
                      hovermode='closest',
                      font=dict(
                      family="Khmer MN",
                      size=15,
                      color="black")
                     )
    fig.show()
    

############ Function Call ############
visual2()


# ### Visualization 2 Explanation
# 
# For our second visualization, we wanted a visual that showed the top 100 countries with higher kidney disease, malaria, and skin cancer rates. The size of the population of each country is symbolized by the size of the circles. The bigger the circle, the more population. With this graph, we can see which countries have higher rates of each of the diseases. For example, we can see that Swaziland has a low Skin Cancer and kidney disease rate, and a high malaria rate. 
# 

# In[4]:


def visual3():
    
    kd = pd.read_excel('Diseases.xlsx', sheet_name = 'Kidney Disease')
    kd = kd[['Country', 'Rate']]
    kd.rename(columns = {'Rate': 'KD Rate'}, inplace = True)
    m = pd.read_excel('Diseases.xlsx', sheet_name = 'Malaria')
    m = m[['Country', 'Rate']]
    m.rename(columns = {'Rate': 'M Rate'}, inplace = True)
    sc = pd.read_excel('Diseases.xlsx', sheet_name = 'Skin Cancer')
    sc = sc[['Country', 'Rate']]
    sc.rename(columns = {'Rate': 'SC Rate'}, inplace = True)
    
    csv = pd.read_csv('clean_countries.csv')
    csv = csv[['Country', 'Population']]
    
    with open('avg_api.json') as f:
        data = json.load(f)
    api_df = pd.DataFrame(data).transpose().reset_index()
    api_df.rename(columns = {'index': 'Country'}, inplace = True)
    
    df = api_df.set_index('Country').join(kd.set_index('Country').join(m.set_index('Country').join(sc.set_index('Country').join(csv.set_index('Country')))))
#     df = pd.read_csv('summary.csv')
    df = df[df['Population']<100000000].reset_index()
    
    fig = go.Figure(data=go.Splom(
                      dimensions=[dict(label='KD Rate', values=df['KD Rate']),
                                  dict(label='M Rate', values=df['M Rate']),
                                  dict(label='SC Rate', values=df['SC Rate']),
                                  dict(label='Population', values=df['Population']),
                                  dict(label='Max Temp', values=df['temperature_2m_max']),
                                  dict(label=' Radiation', values=df['shortwave_radiation_sum']),
                                  dict(label='Precipitation', values=df['precipitation_sum'])],
                      showupperhalf=False,
                      marker=dict(color = [i for i in range(len(df))],
                                  size=5,
                                  colorscale='rainbow',
                                  line=dict(width=0.5,
                                            color='rgb(230,230,230)')),
                      text=df['Country'],
                      diagonal=dict(visible=False)
    ))

    fig.update_layout(title={'text':'Scatterplot Matrix Between all Columns',
                             'y':0.95,
                             'x':0.5,
                             'xanchor': 'center',
                             'yanchor': 'top'},
                      dragmode='select',
                      width=1000,
                      height=1000,
                      hovermode='closest',
                      font=dict(
                      family="Khmer MN",
                      size=18,
                      color="black")
                     )


    fig.show()


############ Function Call ############
visual3()


# ### Visualization 3 Explanation
# 
# For our third visualization, we wanted to bring everything together. Hence, we created a Scatterplot Matrix between all the information. For the rows, we have Malaria Rate, Skin Cancer Rate, Population rate, Max temperature, Radiation, and precipitation. For the columns, we have the Kidney disease, malaria, and skin cancer rates, the population, and max temperatures. We can compare how each of the rows behaves with each of the columns. For example, we can see the graph of max temperature and radiation. With higher radiation, we can see the max temperature is higher. This visualization helps us picture the relationship between everything we have analyzed during this project. 
# 

# ## Summary Files

# In[11]:


def risk(kdrate, mrate, scrate):
    if kdrate>= 25 and mrate>= 10 and scrate>= 3:
        return 'High Risk Country'
    elif kdrate>= 25 and mrate>= 10 or kdrate>= 25 and scrate>= 3 or mrate>= 10 and scrate>= 3:
        return 'Medium Risk Country'
    else:
        return 'Low Risk Country'
    
def summary1():
    with open('avg_api.json') as f:
        data = json.load(f)
    csv = pd.read_csv('clean_countries.csv')
    api_df = pd.DataFrame(data).transpose().reset_index()
    api_df.rename(columns = {'index': 'Country'}, inplace = True)

    new = csv.set_index('Country').join(api_df.set_index('Country')).reset_index()

    kd = pd.read_excel('Diseases.xlsx', sheet_name = 'Kidney Disease')
    m = pd.read_excel('Diseases.xlsx', sheet_name = 'Malaria')
    sc = pd.read_excel('Diseases.xlsx', sheet_name = 'Skin Cancer')

    kd_dict = {i: (kd.loc[i,'Country'],kd.loc[i,'Rate']) for i in range(len(kd))}
    m_dict = {i: (m.loc[i,'Country'], m.loc[i,'Rate']) for i in range(len(m))}
    sc_dict = {i: (sc.loc[i,'Country'],sc.loc[i,'Rate']) for i in range(len(sc))}

    df1 = pd.DataFrame(kd_dict, index = ['Country', 'Kidney Disease Rate']).transpose()
    df2 = pd.DataFrame(m_dict, index = ['Country', 'Malaria Rate']).transpose()
    df3 = pd.DataFrame(sc_dict, index = ['Country', 'Skin Cancer Rate']).transpose()

    df = df1.set_index('Country').join(df2.set_index('Country')).join(df3.set_index('Country')).join(new.set_index('Country'))
    df.rename(columns = {'weathercode': 'Weathercode', 'temperature_2m_max': 'Max Temp.', 'temperature_2m_min':'Min Temp.', 'precipitation_sum':'Precipitation', 'rain_sum':'Rain', 'shortwave_radiation_sum': 'Shortwave Radiation'}, inplace=True)
    
    df['People with Kidney D.'] = df.apply(lambda x: round((x['Kidney Disease Rate']/100) * x['Population'],2), axis=1)
    df['People with Malaria'] = df.apply(lambda x: round((x['Malaria Rate']/100) * x['Population'],2), axis=1)
    df['People with Skin Cancer'] = df.apply(lambda x: round((x['Skin Cancer Rate']/100) * x['Population'],2), axis=1)

    df['Risk Evaluation'] = df.apply(lambda x: risk(x["Kidney Disease Rate"], x["Malaria Rate"], x["Skin Cancer Rate"]), axis = 1)
    
    df.to_csv('summary.csv')
    
    return(df)

############ Function Call ############
summary1()


# # Cited Sources
# 
# If you used any additional sources to complete your Data Analysis section, list them here:
# 
# *   https://plotly.com/python/mapbox-density-heatmaps/
# *   https://plotly.com/python/3d-scatter-plots/
# *   https://plotly.com/python/splom/
# 

# # Video Presentation
# 
# If you uploaded your Video Presentation to Bluejeans, YouTube, or any other streaming services, please provide the link here:
# 
# 
# *   Video Presentation Link: https://youtu.be/PqXEHN0grTg
# 
# 
# Make sure the video sharing permissions are accessible for anyone with the provided link.

# # Submission
# 
# Prior to submitting your notebook to Gradescope, be sure to <b>run all functions within this file</b>. We will not run your functions ourselves, so we must see your outputs within this file in order to receive full credit.
# 
