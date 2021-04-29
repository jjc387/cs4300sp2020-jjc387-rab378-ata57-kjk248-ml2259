from . import *  
import re
import pickle
import os
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from sklearn.metrics.pairwise import cosine_similarity

project_name = "Where to Travel based on Wine Preferences"
net_id = "Jessica Chen: jjc387, Rhea Bansal: rab378, Amani Ahmed: ata57, \
Kylie Kurz: kjk248, Mindy Lee: ml2259"

global wine_dict
global tfidf_wine_matrix
global wine_words_index_dict
global idf

@irsystem.route('/', methods=['GET'])
def home():
	unpickle_files()
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
		if len(data) == 0:
			data = ["We couldn't find results for this query. Try adding more descriptors"]
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)


def unpickle_files():
	global wine_dict
	global tfidf_wine_matrix
	global wine_words_index_dict
	global idf
	with (open('winedata.pickle', "rb")) as openfile:
		while True:
			try:
				wine_dict = (pickle.load(openfile))
			except EOFError:
				break

	with (open('sparsetfidfmatrix.pickle', "rb")) as openfile:
		while True:
			try:
				tfidf_wine_matrix = (pickle.load(openfile))
			except EOFError:
				break
	
	with (open('idf.pickle', "rb")) as openfile:
		while True:
			try:
				idf = (pickle.load(openfile))
			except EOFError:
				break

	with (open('winedescriptions.pickle', "rb")) as openfile:
		while True:
			try:
				wine_words_index_dict = (pickle.load(openfile))
			except EOFError:
				break


def create_OR_list(q_lst):
	"""
	checks to see if ANY of the query terms are in the review

	returns: list of indexs
	"""
	word_idx = []
	cols = []
	for word in q_lst:
		if word in wine_words_index_dict:
			word_idx.append(wine_words_index_dict[word])
			col = tfidf_wine_matrix.getcol(wine_words_index_dict[word])
			cols.append(col)
	sum_row = np.sum(cols, axis = 0)
	postings = np.nonzero(sum_row)[0]
	postings.tolist()
	return postings

def get_cos_sim(query, relevant_doc_index):
	"""
	input: string- the users input
	reviews: user reviews (wine_dict)
	relevant_doc_index: list of relevant docs
	returns: {index: score}
	"""
	query = query.reshape(1, -1) 
	cos_sims = cosine_similarity(tfidf_wine_matrix, query)
	scores = {index:score for index, score in enumerate(cos_sims)}
	return scores


def location_frequency(scores_dict):
	"""
	get frequencies of the top 5 locations
	return {location : (frequency, [index])}
	"""
	global wine_dict
	locs = {}
	scores_list = [(x, scores_dict[x][0]) for x in scores_dict.keys()]
	scores_list = sorted(scores_list, key = lambda x: x[1], reverse=True)
	
	for i in range(len(scores_list)):
		doc, score = scores_list[i]

		prov = wine_dict.get(doc)['province']
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
	
	#TODO: tokenize query and put in vector format here
	
	####### THESE  4 LINES ARE WHERE IM GETTING AN ERROR #############
	# wine_dict= wine_dict[0]
	# tfidf_wine_matrix = tfidf_wine_matrix[0]
	# wine_words_index_dict = wine_words_index_dict[0]
	# idf = idf[0]

	# wine_words_index_dict = wine_words_index_dict[0]
	# print(wine_dict)
	query_vec = np.zeros((len(wine_words_index_dict,)))
	# print("IDF at 0" + str(idf[0]))
	#took this from our code from A1
	query_tok = re.findall(r"[a-z]+", input_terms.lower())

	for tok in query_tok:
		if tok in wine_words_index_dict:
			idx = wine_words_index_dict[tok]
			query_vec[idx] += 1
	
	for tok in set(query_tok):
		if tok in wine_words_index_dict:
			idx = wine_words_index_dict[tok]
			query_vec[idx] = query_vec[idx] * idf[idx]
			
	relevant_docs = create_OR_list(query_tok)
	cos_sims = get_cos_sim(query_vec, relevant_docs)
	locs = location_frequency(cos_sims)

	loc_freq = [(x, len(locs[x])) for x in locs]
	loc_freq = sorted(loc_freq, key = lambda x: len(x), reverse=True)

	size = 5
	#if less than 5 distinct locations are returned
	if len(locs) < 5:
		size = len(locs)

	top_5_loc = [x[0] for x in loc_freq[:size]]

	top_5_info = {k: locs[k] for k in top_5_loc}
	output = formatted_output(top_5_info)
	print("OUTPUTTTTTTTT")
	return output

######################## formatting output #########################

def get_recommended_varieties(ids):
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
	for loc in locations_dict:
		variety_lst = list(get_recommended_varieties(locations_dict[loc]))
		if len(variety_lst) > 5:
			variety_lst = variety_lst[1:6]
		x = ', '.join(variety_lst)
		
		val = "Visit {}, and while you are there you should consider these varieties of wines: {}!".format(loc, x)
		data.append(val)
	return data



