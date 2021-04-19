from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.controllers.wine_data import wine_dict

project_name = "Wine and Beer Food Pairings"
net_id = "Jessica Chen: jjc387, Rhea Bansal: rab378, Amani Ahmed: ata57, \
Kylie Kurz: kjk248, Mindy Lee: ml2259"

@irsystem.route('/', methods=['GET'])
def search():
	query = request.args.get('search')
	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Your search: " + cos_sim_reviews(query, wine_dict[:40])
		data = range(5)
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)



def create_OR_list(wine_dict, ):
	"""
	checks to see if ANY of the query terms are in the review

	returns: list of indexs
	"""



def get_cos_sim(input, reviews, relevant_doc_index):
	"""
	input: string- the users input
	reviews: user reviews 
	relevant_doc_index: list of relevant docs
	"""

def top_locations():
	"""
	get top 100 locations 
	return in format {location : [(score, row_number)]}
	"""

def location_frequency():
	"""
	get frequencies of the top 100 
	return {location : (score, [index])}
	"""

def cos_sim_reviews(input_terms, wine_dict):
	"""
	input_terms: string inputted query
	wine_tfidf_matrix: vector of the words in the various

	returns a dictionary of locations in format {location : [(score, row_number)]} 
	"""
	# call create_OR_list and get list of releveant index
	# do cos_sim for the relevant docs  call get_cos_sim
	# go through and create  {location : [(score, row_number)]} for top 100 cos_sim results
	# get frequency each location in the top 100 {location : (score, [index])}
	


def formatted_output(locations_dict):
	"""
	takes in the created dictionary and formats the output to be more user readable
	location, "you should consider these wines" + wines 

	"""

