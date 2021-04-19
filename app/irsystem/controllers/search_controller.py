from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

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


def get_cos_sim(input, review):
	"""
	input: string- the users input
	review: string - user reivew from dataset
	"""

def create_list():
	"""

	"""

def cos_sim_reviews(input_terms, wine_tfidf_matrix):
	"""
	input_terms: string inputted query
	wine_tfidf_matrix: vector of the words in the various
	reviews: {} dictionary of the user responses in format wine_name: user reivew

	0: postings list 
	1: get cos_sim of each one (into a arr)
	2: arg sort the arr to get the index of the top ____
	3: go through each row to contruct a {location: [ids]}
	4: once there are 4 unique regions & at least 5 entries in each list of tuples

	returns a dictionary of locations in format {location : [(score, row_number)]} 
	"""
	


def formated_output(locations_dict):
	"""
	takes in the created dictionary and formats the output to be more user readable

	"""

