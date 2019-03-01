"""
boolean_query.py
Dependencies: python 3.x, flask

Students: Modify this code to provide an interface for your Boolean search engine
To start the application:
   >python boolean_query.py
To terminate the application, use control-c
To use the application within a browser, use the url:
   http://127.0.0.1:5000/

Some test queries to exercise the dummy interface:
king of sweden
<next button>
prince
a of

To learn flask, see flask tutorial in https://www.tutorialspoint.com/flask/index.htm
"""

from os import environ
import nltk
from nltk.stem.snowball import SnowballStemmer
from flask import Flask, render_template, request
from boolean_search import dummy_search, dummy_movie_data, dummy_movie_snippet, get_term_dict, get_stop_word_dict

# Create an instance of the flask application within the appropriate namespace (__name__).
# By default, the application will be listening for requests on port 5000 and assuming the base 
# directory for the resource is the directory where this module resides.
app = Flask(__name__)
term_dict = get_term_dict()
stop_words = get_stop_word_dict()
stemmer = SnowballStemmer("english")


# Welcome page
# Python "decorators" are used by flask to associate url routes to functions.
# A route is the path from the base directory (as it would appear in the url)
# This decorator ties the top level url "localhost:5000" to the query function, which
# renders the query_page.html template.
@app.route("/")
def query():
    """For top level route ("/"), simply present a query page."""
    return render_template('query_page.html')


# This takes the form data produced by submitting a query page request and returns a page displaying
# results (SERP).
@app.route("/results", methods=['POST'])
def results():
    """Generate a result set for a query and present the 10 results starting with <page_num>."""

    page_num = int(request.form['page_num'])
    query = request.form['query']  # Get the raw user query
    # query_director = request.form['director']
    # query_starring = request.form['starring']
    # query_location = request.form['location']

    query_terms = [stemmer.stem(word) for word in nltk.word_tokenize(query.strip())]

    # Keep track of any stop words removed from the query to display later.
    # Stop words should be stored in persistent storage when building your index,
    # and loaded into your search engine application when the application is started.
    skipped = [e for e in query_terms if e in stop_words]
    unknown_terms = [terms for terms in query_terms if terms not in term_dict]

    # If your search found any query terms that are not in the index, add them to unknown_terms and
    # render the error_page.
    if unknown_terms:
        return render_template('error_page.html', unknown_terms=unknown_terms)
    else:
        # At this point, your query should contain normalized terms that are not stopwords or unknown.
        movie_ids = dummy_search(query)  # Get a list of movie doc_ids that satisfy the query.
        # render the results page
        num_hits = len(movie_ids)  # Save the number of hits to display later
        movie_ids = movie_ids[((page_num - 1) * 10):(page_num * 10)]  # Limit of 10 results per page
        # movie_results = list(map(dummy_movie_snippet, movie_ids))  # Get movie snippets: title, abstract, etc.
        # Using list comprehension:
        movie_results = [dummy_movie_snippet(e) for e in movie_ids]
        return render_template('results_page.html', orig_query=query, movie_results=movie_results, srpn=page_num,
                               len=len(movie_ids), skipped_words=skipped, unknown_terms=unknown_terms,
                               total_hits=num_hits)


# Process requests for movie_data pages
# This decorator uses a parameter in the url to indicate the doc_id of the film to be displayed
@app.route('/movie_data/<film_id>')
def movie_data(film_id):
    """Given the doc_id for a film, present the title and text (optionally structured fields as well)
    for the movie."""
    data = dummy_movie_data(film_id)  # Get all of the info for a single movie
    return render_template('doc_data_page.html', data=data)


# If this module is called in the main namespace, invoke app.run().
# This starts the local web service that will be listening for requests on port 5000.
# if __name__ == "__main__":
#     app.run(debug=True)
# app.run()
# While you are debugging, set app.debug to True, so that the server app will reload
# the code whenever you make a change.  Set parameter to false (default) when you are
# done debugging.
app.run(environ.get('PORT'))
