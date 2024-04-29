from flask import Flask, render_template, request, jsonify
from models import initialize_parameters, recommend_top_articles, update_user_click_history, reinitialize_parameters, get_most_viewed_categories
import pandas as pd
import random

app = Flask(__name__)

# Loading Datasets
news_df = pd.read_csv('static/news.tsv', header=None, sep='\t')
news_df.columns = ['News ID', 'Category', 'SubCategory', 'Title', 'Abstract', 'URL', 'Title Entities', 'Abstract Entities']
behaviours_df = pd.read_csv('static/behaviors.tsv', sep="\t", names=["ImpressionId", "userId", "timestamp", "click_history", "impressions"])

# Initializing parameters when app starts
news_id_to_title = news_df.set_index('News ID')['Title'].to_dict()
news_category_mapping = news_df.set_index('News ID')['Category'].to_dict()
user_click_history = {}
for index, row in behaviours_df.iterrows():
    user_id = row['userId']
    clicked_articles = str(row['click_history']).split()
    clicked_articles = [article for article in clicked_articles if article.lower() != 'nan']
    user_click_history.setdefault(user_id, set()).update(clicked_articles)

categories = news_df['Category'].unique()
user_alpha_beta_params = initialize_parameters(user_click_history, news_category_mapping, categories)
# Print a random userId from behaviours_df
if not behaviours_df.empty:
    random_user_id = random.choice(behaviours_df['userId'].unique())
    print(f"Randomly selected userId: {random_user_id}")
else:
    print("No users found in behaviours_df.")


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            user_id = request.form['user_id']
            recommended_articles = recommend_top_articles(user_id, user_alpha_beta_params, news_df)
            user_categories = get_most_viewed_categories(user_id, user_alpha_beta_params)
            return render_template('recommendations.html', articles=recommended_articles, user_id=user_id, categories=user_categories)
        else:
            return render_template('index.html')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update_preferences', methods=['POST'])
def update_preferences():
    try:
        data = request.get_json()
        user_id = data['user_id']
        article_id = data['article_id']
        liked = data['liked']

        if liked:
            global behaviours_df  # Reference the global variable
            global user_alpha_beta_params  # Reference the global variable
            behaviours_df = update_user_click_history(user_id, article_id, user_click_history, behaviours_df)
            user_alpha_beta_params = reinitialize_parameters(user_click_history, news_category_mapping, categories)

        return jsonify({'status': 'success'})
    except KeyError as e:
        return jsonify({'error': f'Missing key: {e}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
