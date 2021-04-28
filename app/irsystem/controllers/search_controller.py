from . import *  
import re
import json
# import nltk
# from nltk import word_tokenize
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.controllers.wine_data import wine_dict, tfidf_wine_matrix, wine_words_index_dict, vec, idf
from sklearn.metrics.pairwise import cosine_similarity
from app.irsystem.controllers.response_class import Response_format

project_name = "Where to Travel based on Wine Preferences"
net_id = "Jessica Chen: jjc387, Rhea Bansal: rab378, Amani Ahmed: ata57, \
Kylie Kurz: kjk248, Mindy Lee: ml2259"


@irsystem.route('/', methods=['GET'])
def home():
	return render_template('search.html', name=project_name, netid=net_id, flavors=[])

@irsystem.route('/search', methods=['GET'])
def search():
	query = request.args.get('flavors')
	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Your search: " + query
		data = cos_sim_reviews(query)
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)

def create_query_vec(query):
	query_vec = np.zeros((len(wine_words_index_dict,)))
	#took this from our code from A1
	query_tok = re.findall(r"[a-z]+", input_terms)

	for tok in query_tok:
		if tok in wine_words_index_dict:
			idx = wine_words_index_dict[tok]
			query_vec[idx] += 1
	
	for tok in set(query_tok):
		if tok in wine_words_index_dict:
			idx = wine_words_index_dict[tok]
			query_vec[idx] = query_vec[idx] * idf[idx]

	return query_vec


def get_cos_sim(query):
	"""
	input: string- the users input
	reviews: user reviews (wine_dict)
	relevant_doc_index: list of relevant docs
	returns: np vector of cos similarities 
	"""
	scores = {}
	query = query.reshape(1, -1) 
	cos_sims = cosine_similarity(tfidf_wine_matrix, query)
	# for doc in relevant_doc_index:
	# 	curr_review = tfidf_wine_matrix[doc]
	# 	c_review = curr_review.reshape(1, -1) 
	# 	cos_sim = cosine_similarity(query, c_review)
	# 	scores[doc] = cos_sim

	return scores

'''
dict['country'] = [ids associated with that]

for each country that we want:
	sorted(cos_sims of associated ids)
	get top 2 regions from the most similar reviews
'''


'''
relevant_idx = [5,6,4]
subset = cos_sims[relevant_idx]

sorted_args = np.argsort(subset)

new_idx_sorted_list = [relevant_idx[x] for x in sorted_args]
'''

def location_sorted_indices(cos_sims):
	"""
	get frequencies of the top 5 locations
	return {location : [index]}
	"""
	locs = {}
	scores_list = [(x, scores_dict[x]) for x in scores_dict]
	scores_list = sorted(scores_list, key = lambda x: x[1], reverse=True)
	
	for i in range(len(scores_list)):
		doc, score = scores_list[i]
		prov = wine_dict[doc]['province']
		if prov not in locs:
			locs[prov] = [doc]
		else:
			locs[prov].append(doc)
		
	return locs

def cos_sim_reviews(input_terms):
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
	
	#TODO: Iteration 2
	# pre-step) if user doesn't pick 3 countries, randomly generate countries to get 3 
	# 1) do cos sim with query against all docs
	# 2) for each country get sorted list of indices ranked by highest cos sim to lowest
	# 3) pick out top 2 regions from the indices (associated with 2 different reviews)
	# 4) dictionary with key of country and value is list of 2 response class objects 

	query_vec = create_query_vec(input_terms)
	cos_sims = get_cos_sim(query_vec, relevant_docs)
	
	locs = location_sorted_indices(cos_sims)

	loc_freq = [(x, len(locs[x])) for x in locs]
	loc_freq = sorted(loc_freq, key = lambda x: x[1], reverse=True)

	size = 5
	#if less than 5 distinct locations are returned
	if len(locs) < 5:
		size = len(locs)

	top_5_loc = [x[0] for x in loc_freq[:size]]

	top_5_info = {k: locs[k] for k in top_5_loc}
	output = formatted_output(top_5_info)
	return output

######################## formatting output #########################

def get_recommended_varieties(ids, wine_dict=wine_dict):
	"""
	return set of varieties suggested
	"""
	variety_set = set()
	for i in ids:
		variety_set.add(wine_dict[i]["variety"])
	return variety_set

def formatted_output(locations_dict):
	"""
	takes in the created dictionary and formats the output to be more user readable
	location, "you should consider these wines" + wines 
	{location : (frequency, [index])}
	"""
	data = []
	dict_data = {}
	for loc in locations_dict:
		variety_lst = list(get_recommended_varieties(locations_dict[loc]))
		if len(variety_lst) > 5:
			variety_lst = variety_lst[1:6]
		x = ', '.join(variety_lst)
		
		val = "visit {}, and while you are there you should consider these varities of wines: {}!".format(loc, x)
		data.append(val)
		
		##### tried to start the output formatting lmk what you think ######

		# get the top 3 wine responses for the location
		three_ind = locations_dict[loc][:3]

		dict_data[loc] = []
		## for the location, go through the top 3 responses (or we can change to 2) and get the info we need for each one. 
		## append the object to the list for the given location
		for i in three_ind:
			obj = Response_format(wine_dict["region"][i], wine_dict["wine"][i], wine_dict["description"][i], wine_dict["winery"][i])
			dict_data[loc].append(obj)

	#json.dumps(dict_data)
	
	return data



