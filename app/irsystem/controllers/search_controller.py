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
	if not query:
		data = []
		output_message = ''
	else:
		if len(countries) == 0:
			country_text = "anywhere"
		else:
			country_text = countries
		output_message = "Your search: " + query + " wines from " + country_text
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
	global tfidf_embedding_matrix # num reviews x 300
	global word_embedding_matrix # num terms x 300
	global idf_weight_dict # word -> tf idf weight
	global word_to_idx_dict # word -> idx (for word_embedding_matrix row idx)
	#TODO: replace with reduced descriptions dict
	with (open('wine_dict02.pickle', "rb")) as openfile:
		while True:
			try:
				wine_dict = (pickle.load(openfile))
			except EOFError:
				break

	with (open('review_tfidf_embeddings01.pickle', "rb")) as openfile:
		while True:
			try:
				tfidf_embedding_matrix = (pickle.load(openfile))
			except EOFError:
				break
	
	with (open('idf_weight_dict0.pickle', "rb")) as openfile:
		while True:
			try:
				idf_weight_dict = (pickle.load(openfile))
			except EOFError:
				break

	with (open('matrix_word2vec0.pickle', "rb")) as openfile:
		while True:
			try:
				word_embedding_matrix = (pickle.load(openfile))
			except EOFError:
				break
	
	with (open('country_to_idx0.pickle', "rb")) as openfile:
		while True:
			try:
				country_to_idx_dict = (pickle.load(openfile))
			except EOFError:
				break

	with (open('words_word2vec_dict0.pickle', "rb")) as openfile:
		while True:
			try:
				word_to_idx_dict = (pickle.load(openfile))
			except EOFError:
				break

def query_vectorizer(query_input):
	query_toks = re.findall(r"[a-z]+", query_input.lower())
	weightedqueryterms = []
	i = 0
	for term in query_toks:
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
	cos_sims = cosine_similarity(tfidf_embedding_matrix, query)
	return cos_sims

def format_descriptors(descrip):
	"""
	takes in string in format of "crisp cherry moist_earth dry dry"
	want to return "crisp, cherry, moist earth, dry"
	"""
	descrip_lst = descrip.split(' ')
	descrip_set = set(descrip_lst)
	descrip_out= ", ".join(list(descrip_set))
	descrip_out = descrip_out.replace("_", " ")
	return descrip_out

def update_results(idx, score, prov_list, countryset, results):
	
	score = '{:.2f}'.format(score)
	
	prov = wine_dict[idx]['province']
	region1 = wine_dict[idx]['region_1']
	country = wine_dict[idx]['country']
	prov_string = ''
	if region1 is None or region1 == 'NaN' or region1 == 'nan' or (not isinstance(region1, str) and math.isnan(region1)):
		prov_string = prov
		if country == prov:
			prov_string = wine_dict[idx]['winery']
	else:
		prov_string = "{}, {}".format(region1, prov)
	if prov_string not in prov_list:
		prov_list.append(prov_string)
		dets = {'province': prov_string, 'winery': wine_dict[idx]['winery'], 'variety': wine_dict[idx]['variety'], 'review':format_descriptors(wine_dict[idx]['description']), 'similarity': score, 'full_review': wine_dict[idx]['full_review']}
		if country not in countryset:
			print('adding country ' + country)
			print(countryset)
			country_ind = len(countryset)
			countryset[country] = country_ind
			print(countryset)
			results.append({'country': country, 'details' : [dets] })
		else:
			country_ind = countryset[country]
			results[country_ind]['details'].append(dets)

	return prov_list, countryset, results

def get_top_results(scores_array, country_list):
	"""
	insert comments
	"""
	results = [] 
	#user has selected no country preference
	if len(country_list) == len(country_to_idx_dict.keys()):
		srt_all_country = scores_array.flatten()		
		srt_all_country = (-srt_all_country).argsort()
		
		j = 0
		prov_list = []
		countryset = {} #country: index in the results output
		while j < len(scores_array) and (len(prov_list) < 10):
			idx = srt_all_country[j]
			score = scores_array[idx][0] *100
			prov_list, countryset, results = update_results(idx, score, prov_list, countryset, results)
			j = j+1
	#user has selected country preferences
	else:
		countryset = {}
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
				score = scores_array[idx][0] *100
				prov_list, countryset, results = update_results(idx, score, prov_list, countryset, results)
				i = i+1
	return results

def cos_sim_reviews(query_input, country_input):	
	
	query_vec = query_vectorizer(query_input)
	if query_vec == None:
		return []
	country_list = get_country_list(country_input)
	cos_scores = get_cos_sim(query_vec)
	results = get_top_results(cos_scores, country_list)
	return results




