from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import streamlit as st

def find_match(users_collection):
    users = list(users_collection.find({}))
    if len(users) <= 1:
        st.warning("Not enough users to find a match. Please wait for more participants.")
        return

    users_df = pd.DataFrame(users)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    worries = users_df['worries'].fillna('').tolist()
    worry_embeddings = model.encode(worries)

    n_clusters = min(5, len(users_df))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    users_df['cluster'] = kmeans.fit_predict(worry_embeddings)

    current_user_index = users_df[users_df['email'] == st.session_state['user_email']].index[0]
    current_user_cluster = users_df.loc[current_user_index, 'cluster']
    cluster_users = users_df[users_df['cluster'] == current_user_cluster]

    if len(cluster_users) > 1:
        current_user_embedding = worry_embeddings[current_user_index].reshape(1, -1)
        cluster_embeddings = [worry_embeddings[i] for i in cluster_users.index if i != current_user_index]
        similarity_scores = cosine_similarity(current_user_embedding, cluster_embeddings)[0]
        closest_match_index = similarity_scores.argmax()
        matched_user = cluster_users.iloc[closest_match_index]
        return matched_user
    else:
        st.warning("No similar users found in your cluster. Please wait for more participants.")
        return None
