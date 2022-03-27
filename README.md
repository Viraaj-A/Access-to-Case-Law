## Manual:
The Dashboard (Module 4) was built with dash. To open it you will need to run it via the terminal by calling the Module 4 dash.py script. We ran this from the Anaconda Prompt. To be sure this runs smoothly, make sure you have all relevant dash dependencies installed (these include: dash_core_components, dash_html_components, dash_bootstrap_components, dash_bootstrap_components._components.Container, and dash.dependencies). 
When in doubt, open Module 4 dash.py in Python and double check that you have installed all relevant packages.

Once you have cloned this repository, open anaconda, set your working directory to the Acess to Case Law folder, then type the following code into the Anaconda Prompt to run Module 4 dash:
**python "src\Module 4 dash.py"**

**Important notice:** When executing this file in Anaconda, it might be a little difficult to find the URL for the dashboard. Here are some tips to help you find it!
If everything is running smoothly you should spot a red warning message that reads "WARNING: This is a development server. Do not use it in a production deployment." This is not of concern to us, but instead it is a useful reference to finding the address of the Dashbord server which is located 3 lines above this warning. The Dashboard typically runs on a local host http://127.0.0.1:8050/


## 1 § Modules

### Web scraping

Initially our program will access the comprehensive database of HUDOC’s European Union Court of Human Rights legal documents (https://hudoc.echr.coe.int). Specifically, we built a web scraper to download all substantive judgements from this database. Additionally, we will extract all metadata associated with the legal documents to enable further exploration and analysis.

### Data cleaning & wrangling

In order to be able to work with the scraped data we will construct a database, comprising all relevant information regarding all judgements. During the data cleaning & wrangling stage we will use the spaCy library for NLP-preprocessing to conveniently organise information for further analysis.

### Data analysis

In the analysis stage of the project we will do basic to advanced NLP analysis of the documents to provide the underlying information of the data visualisation. This analysis is what transforms the HUDOC database to a database where meaningful insight can be gained, i.e. a transformation of an inaccessible database to an accessible database. 

### Information Visualisation

The user will be presented with interactive infographics, the output of the previous modules, that they can manipulate. Here, we will leverage the plotly library to produce the plots and the dash library to produce a navigable dashboard for the user. 


