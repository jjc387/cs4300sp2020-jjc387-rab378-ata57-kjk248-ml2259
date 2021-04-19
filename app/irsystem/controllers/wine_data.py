import pandas as pd
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import word_tokenize


url = "https://raw.githubusercontent.com/jjc387/cs4300sp2021-jjc387-rab378-ata57-kjk248-ml2259/mindy/app/irsystem/winereviews.csv"
column_headers = ["country", "description", "designation", "points", "price", "province", "region_1", "region_2", "variety", "winery"]
df = pd.read_csv(url, usecols=column_headers)
wine_dict = df.to_dict(orient='index')

# referenced assignment 5 to help with the tf-idf vecotorizer!
vec = TfidfVectorizer(stop_words='english',max_df=0.75,min_df= 1,max_features=10000)
tfidf_wine_matrix = vec.fit_transform([wine_dict[d]['description'] for d in wine_dict]).toarray()
wine_words = vec.get_feature_names()
wine_words_index_dict ={inex:word for index, word in enumerate(wine_words)} 


