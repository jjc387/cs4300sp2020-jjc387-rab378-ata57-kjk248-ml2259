from . import *  
import re
import pickle
import os
import flask
import math
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from sklearn.metrics.pairwise import cosine_similarity

project_name = "Where to Travel based on Wine Preferences"
net_id = "Jessica Chen: jjc387, Rhea Bansal: rab378, Amani Ahmed: ata57, \
Kylie Kurz: kjk248, Mindy Lee: ml2259"

global wine_dict 
global country_to_idx_dict
#insert kylie's ml stuff 
global tfidf_embedding_matrix # num reviews x 300
global word_embedding_matrix # num terms x 300
global idf_weight_dict # word -> tf idf weight
global word_to_idx_dict # word -> idx (for word_embedding_matrix row idx)

@irsystem.route('/', methods=['GET'])
def home():
	unpickle_files()
	return render_template('search.html', name=project_name, netid=net_id, flavors=[])

@irsystem.route('/search', methods=['GET'])
def search():
	query = request.args.get('flavors')
	countries = request.args.get('countries')
	print("COUNTRY TYPE" + str(type(countries)))
	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Your search: " + query
		data = cos_sim_reviews(query, countries)
		# if len(data) == 0:
		# 	data = ["We couldn't find results for this query. Try adding more descriptors"]
	return render_template('search.html', data=data, output_message=output_message, name=project_name, netid=net_id)

@irsystem.route('/aroma_wheel.html')
def aroma_wheel():
	return render_template('aroma_wheel.html')

def unpickle_files():
	global wine_dict # done
	global country_to_idx_dict
	#insert kylie's ml stuff 
	global tfidf_embedding_matrix # num reviews x 300
	global word_embedding_matrix # num terms x 300
	global idf_weight_dict # word -> tf idf weight
	global word_to_idx_dict # word -> idx (for word_embedding_matrix row idx)
	#TODO: replace with reduced descriptions dict
	with (open('wine_dict2.pickle', "rb")) as openfile:
		while True:
			try:
				wine_dict = (pickle.load(openfile))
			except EOFError:
				break

	with (open('review_tfidf_embeddings2.pickle', "rb")) as openfile:
		while True:
			try:
				tfidf_embedding_matrix = (pickle.load(openfile))
			except EOFError:
				break
	
	with (open('idf_weight_dict2.pickle', "rb")) as openfile:
		while True:
			try:
				idf_weight_dict = (pickle.load(openfile))
			except EOFError:
				break
	print("HERE IS THE DICT")
	print(idf_weight_dict["spice"])

	with (open('matrix_word2vec2.pickle', "rb")) as openfile:
		while True:
			try:
				word_embedding_matrix = (pickle.load(openfile))
			except EOFError:
				break
	
	with (open('country_to_idx2.pickle', "rb")) as openfile:
		while True:
			try:
				country_to_idx_dict = (pickle.load(openfile))
			except EOFError:
				break

	with (open('words_word2vec_dict2.pickle', "rb")) as openfile:
		while True:
			try:
				word_to_idx_dict = (pickle.load(openfile))
			except EOFError:
				break

#TODO: query vectorizer function
def query_vectorizer(query_input):
	query_toks = re.findall(r"[a-z]+", query_input.lower())
	weightedqueryterms = []
	i = 0
	for term in query_toks:
		# print(idf_weight_dict)
		if term in idf_weight_dict:
			i = i+1
			tfidfweight = idf_weight_dict[term]
			idx = word_to_idx_dict[term]
			word_vector = tfidfweight * word_embedding_matrix.getrow(idx).reshape(1,300)
			weightedqueryterms.append(word_vector)
	if i == 0:
		return None
	query_vec = sum(weightedqueryterms)
	return query_vec

#TODO: parses through input for country preference and returns list of countries 
def get_country_list(country_list):
	if len(country_list) == 0:
		return country_to_idx_dict.keys()
	country_list = country_list.split(",")
	if (len(country_list) == 1 and 'No preference' in country_list):
		country_list = country_to_idx_dict.keys()
	
	if 'No preference' in country_list:
		country_list.remove('No preference')

	return country_list

def get_cos_sim(query):
	"""
	input: string- the users input
	reviews: user reviews (wine_dict)
	relevant_doc_index: list of relevant docs
	returns: {index: score}
	"""
	query = query.reshape(1, -1) 
	#TODO: do cos sim with tfidf_embeddings_matrix
	cos_sims = cosine_similarity(tfidf_embedding_matrix, query)
	return cos_sims

#TODO: repurpose this to take in cos_sim values and queried countries and return the top 3 distinct regions and associated wineries
def get_top_results(scores_array, country_list):
	"""
	get frequencies of the top 5 locations
	return {location : (frequency, [index])}
	"""
	results = [] 
	for country in country_list:
		country_idx = country_to_idx_dict[country]
		scores_subset = scores_array[country_idx]
		scores_subset = scores_subset.flatten()
		sorted_args = (-scores_subset).argsort()
		sorted_idxs = [country_idx[i] for i in sorted_args]

		i = 0
		prov_list = []
		while i < len(sorted_idxs) and len(prov_list) < 3:
			idx = sorted_idxs[i]
			prov_string = ''
			print(wine_dict[idx].keys())
			print(wine_dict[idx])
			region1 = wine_dict[idx]['region_1']
			prov = wine_dict[idx]['province']
			if region1 is None or region1 == 'NaN' or region1 == 'nan' or math.isnan(region1):
				prov_string = prov
				if country == prov:
					prov_string = wine_dict[idx]['winery']
			else:
				print(region1)

				prov_string = "{}, {}".format(region1, prov)
			
			if prov_string not in prov_list:
				prov_list.append(prov_string)
				province_dict = {'country': country,'province': prov_string, 
				'winery': wine_dict[idx]['winery'], 'variety': wine_dict[idx]['variety'], 
				'review':wine_dict[idx]['description']}
				results.append(province_dict)
		
			i = i+1

	return results

def cos_sim_reviews(query_input, country_input):
	"""
	input_terms: string inputted query
	wine_tfidf_matrix: vector of the words in the various

	returns a dictionary of locations in format {location : [(score, row_number)]} 
	"""
	# call create_OR_list and get list of releveant index
	# do cos_sim for the relevant docs  call get_cos_sim (return as a dict)
	# create tuple list from get_cos_sim
	# go through and create  {location : [(score, row_number)]} for top 100 cos_sim results
	# get frequency each location in the top 100 {location : (score, [index])}
	
	
	query_vec = query_vectorizer(query_input)
	if query_vec == None:
		return []
	country_list = get_country_list(country_input)
	cos_scores = get_cos_sim(query_vec)
	results = get_top_results(cos_scores, country_list)
	print("OUTPUTTTTTTTT")
	return results




