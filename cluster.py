import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def run_clustering():
    df = pd.read_csv(os.path.join(DATA_DIR, 'raw_reviews.csv'))
    df = df.dropna(subset=['review_text'])
    df['review_text'] = df['review_text'].astype(str).str.strip()
    df = df[df['review_text'].str.len() > 10].reset_index(drop=True)

    print(f"Loaded {len(df)} reviews. Embedding...")

    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(df['review_text'].tolist(), show_progress_bar=True)

    # Force exactly 5 clusters with KMeans for reliability
    print("Clustering into 5 themes...")
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings)

    # Generate theme labels using top keywords per cluster
    theme_labels = []
    for cluster_id in range(5):
        mask = labels == cluster_id
        cluster_reviews = df['review_text'][mask].tolist()
        sample = ' '.join(cluster_reviews[:20]).lower()
        words = [w for w in sample.split() if len(w) > 4]
        from collections import Counter
        top_words = [w for w, _ in Counter(words).most_common(3)]
        theme_labels.append(f"Theme_{cluster_id}: {' '.join(top_words)}")

    df['theme_id'] = labels
    df['theme_label'] = df['theme_id'].map(lambda x: theme_labels[x])

    out_path = os.path.join(DATA_DIR, 'clustered_reviews.csv')
    df.to_csv(out_path, index=False)

    print("\nClustering complete:")
    for i, label in enumerate(theme_labels):
        count = (labels == i).sum()
        print(f"  {label} | {count} reviews")

    print(f"\nSaved to data/clustered_reviews.csv")

if __name__ == '__main__':
    run_clustering()
