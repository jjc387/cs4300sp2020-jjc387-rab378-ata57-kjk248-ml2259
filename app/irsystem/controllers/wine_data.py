# import pandas as pd
# import pickle
# from scipy import sparse
# from sklearn.feature_extraction.text import TfidfVectorizer

# #PREPROCESSING

# url = "https://raw.githubusercontent.com/jjc387/cs4300sp2021-jjc387-rab378-ata57-kjk248-ml2259/master/app/irsystem/winereviews.csv"
# column_headers = ["country", "description", "province", "region_1", "variety", "winery"]
# df = pd.read_csv(url, usecols=column_headers)


# # print(len(df))

# df = df[df.region_1.notnull()]
# df = df[df.province != "Other"]
# df = df[df.province.notnull()]
# df = df[df.province != "France Other"]
# df = df[df.province != "Spain Other"]
# df = df[df.province != "Australia Other"]
# df = df.reset_index()

# wine_dict = df.to_dict(orient='index')
# # print(wine_dict[26670])

# with open('winedata.pickle', 'wb') as handle:
#     pickle.dump(wine_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)


# # wine_dict = df.to_dict(orient='index')
# # print(wine_dict[26670])
# #END


# # with open('winedata.pickle', 'rb') as handle:
# #     wine_dict = pickle.load(handle)

# # print(wine_dict == b)

# # print(len(wine_dict))

# # print(df.description)
# # sparse_descrip_matrix = sparse.csr_matrix(df.description.astype(str))
# # print(sparse_descrip_matrix)
# # get rid of Other and NULL

# # referenced assignment 5 to help with the tf-idf vecotorizer!
# vec = TfidfVectorizer(stop_words='english', min_df = 10, max_features=5000)
# tfidf_wine_matrix = vec.fit_transform([wine_dict[d]['description'] for d in wine_dict]).toarray()
# print("TF IDF WINE MATRIX")
# print(len(tfidf_wine_matrix))
# print("WINE DICT SHAPE")
# print(len(wine_dict))

# sparse_tfidf_matrix = sparse.csr_matrix(tfidf_wine_matrix)
# idf = vec.idf_ 
# wine_words = vec.get_feature_names()
# wine_words_index_dict ={word:index for index, word in enumerate(wine_words)}
# # print(wine_words_index_dict) 

# with open('winedescriptions.pickle', 'wb') as handle:
#     pickle.dump(wine_words_index_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open('idf.pickle', 'wb') as handle:
#     pickle.dump(idf, handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open('sparsetfidfmatrix.pickle', 'wb') as handle:
#     pickle.dump(sparse_tfidf_matrix, handle, protocol=pickle.HIGHEST_PROTOCOL)