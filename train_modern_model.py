import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    train_file = os.path.join(base_dir, "Fake_News_Detection", "Fake_News_Detection", "train.csv")
    out_file = os.path.join(base_dir, "Fake_News_Detection", "Fake_News_Detection", "modern_model.joblib")
    
    print(f"Loading training data from {train_file}...")
    df = pd.read_csv(train_file)
    
    # Fill NaN statements
    df['Statement'] = df['Statement'].fillna('')
    
    print("Building and training pipeline (TF-IDF + Logistic Regression)...")
    clf = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', ngram_range=(1,4), use_idf=True, smooth_idf=True)),
        ('clf', LogisticRegression(penalty="l2", C=1, solver='liblinear'))
    ])
    
    clf.fit(df['Statement'], df['Label'])
    
    print(f"Saving modern model to {out_file}...")
    joblib.dump(clf, out_file)
    print("Training complete!")

if __name__ == "__main__":
    main()
