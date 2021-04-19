import pandas as pd


url = "https://raw.githubusercontent.com/jjc387/cs4300sp2021-jjc387-rab378-ata57-kjk248-ml2259/mindy/app/irsystem/winereviews.csv"
column_headers = ["country", "description", "designation", "points", "price", "province", "region_1", "region_2", "variety", "winery"]
df = pd.read_csv(url, usecols=column_headers)
wine_dict = df.to_dict(orient='index')
print(wine_dict[0]["country"])
print(wine_dict[0]["description"])
# score_vec = TfidfVectorizer(stop_words='english',max_df=0.7,min_df= 50,max_features=5000)
# wine_tfidf_matrix = score_vec.fit_transform([wine_dict['description'] for description in wine_dict]).toarray()