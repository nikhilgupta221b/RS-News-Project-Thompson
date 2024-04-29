import numpy as np
import pandas as pd

def initialize_parameters(user_click_history, news_category_mapping, categories):
    user_category_counts = {}
    for user_id, clicked_news_ids in user_click_history.items():
        user_category_counts[user_id] = {category: 1 for category in categories}  # Start with a uniform prior
        for news_id in clicked_news_ids:
            if news_id in news_category_mapping:
                category = news_category_mapping[news_id]
                user_category_counts[user_id][category] += 1  # Increase count for clicked categories
    # Convert counts to alpha parameters, keeping beta at 1
    user_alpha_beta_params = {
        user_id: {category: [count, 1] for category, count in category_counts.items()}
        for user_id, category_counts in user_category_counts.items()
    }
    return user_alpha_beta_params

def recommend_top_articles(user_id, user_alpha_beta_params, news_df):
    sampled_probs = {
        category: np.random.beta(a=user_alpha_beta_params[user_id][category][0], b=user_alpha_beta_params[user_id][category][1])
        for category in user_alpha_beta_params[user_id].keys()
    }
    sorted_categories = sorted(sampled_probs.items(), key=lambda item: item[1], reverse=True)
    top_categories = [cat[0] for cat in sorted_categories[:3]]
    top_articles = []
    for category in top_categories:
        category_articles = news_df[news_df['Category'] == category]
        sampled_articles = category_articles.sample(min(5, len(category_articles)))
        top_articles.extend(sampled_articles.to_dict('records'))

    np.random.shuffle(top_articles)
    return top_articles[:5]

def get_most_viewed_categories(user_id, user_alpha_beta_params):
    category_clicks = {category: params[0] - 1 for category, params in user_alpha_beta_params[user_id].items()}  # Subtract 1 for the initial value
    # Sort categories by the number of clicks in descending order
    sorted_categories = sorted(category_clicks.items(), key=lambda item: item[1], reverse=True)
    return sorted_categories

def update_user_click_history(user_id, news_id, user_click_history, behaviours_df):
    if user_id not in user_click_history:
        user_click_history[user_id] = set()
    user_click_history[user_id].add(news_id)
    if user_id in behaviours_df['userId'].values:
        current_history = behaviours_df.loc[behaviours_df['userId'] == user_id, 'click_history'].iloc[0]
        current_history = '' if pd.isna(current_history) else str(current_history)
        updated_history = current_history + ' ' + news_id if current_history else news_id
        behaviours_df.loc[behaviours_df['userId'] == user_id, 'click_history'] = updated_history
    else:
        new_entry = pd.DataFrame({
            'userId': [user_id],
            'click_history': [news_id],
            'Impressions': ['']  # Assuming this can be empty or set a default value
        })
        behaviours_df = pd.concat([behaviours_df, new_entry], ignore_index=True)

    return behaviours_df

def reinitialize_parameters(user_click_history, news_category_mapping, categories):
    user_category_counts = {}
    for user_id, clicked_news_ids in user_click_history.items():
        category_counts = {category: 1 for category in categories}
        for news_id in clicked_news_ids:
            if news_id in news_category_mapping:
                category = news_category_mapping[news_id]
                category_counts[category] += 1
        user_category_counts[user_id] = category_counts

    # Convert these counts to alpha and beta parameters
    user_alpha_beta_params = {
        user_id: {category: [count, 1] for category, count in counts.items()}
        for user_id, counts in user_category_counts.items()
    }
    return user_alpha_beta_params


# # Function to recommend an article to a user
# def recommend_article(user_id, user_alpha_beta_params, news_df, news_category_mapping):
#     sampled_probs = {
#         category: np.random.beta(a=user_alpha_beta_params[user_id][category][0], b=user_alpha_beta_params[user_id][category][1])
#         for category in user_alpha_beta_params[user_id].keys()
#     }
#     chosen_category = max(sampled_probs, key=sampled_probs.get)
#     possible_articles = news_df[news_df['Category'] == chosen_category]
#     if not possible_articles.empty:
#         recommended_article = possible_articles.sample(1).iloc[0]
#         return recommended_article['News ID']
#     return None


#
# def recommend_and_display_article(user_id, user_alpha_beta_params,news_df,news_category_mapping):
#     # Display the user's most viewed categories
#     most_viewed_categories = get_most_viewed_categories(user_id, user_alpha_beta_params)
#     print(f"User's most viewed categories: {most_viewed_categories}")
#
#     # Recommend an article
#     recommended_news_id = recommend_article(user_id, user_alpha_beta_params,news_df,news_category_mapping)
#     if recommended_news_id:
#         news_title = news_id_to_title[recommended_news_id]
#         news_category = news_category_mapping[recommended_news_id]
#         print(f"Recommended Article: {recommended_news_id} - {news_title} (Category: {news_category})")
#     else:
#         print("No article recommended.")
#     return recommended_news_id
