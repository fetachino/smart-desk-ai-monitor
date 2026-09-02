# train.py
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
import joblib

OUT = Path("outputs")
OUT.mkdir(exist_ok=True)

def main():
    df = pd.read_csv(OUT / "train_data.csv")

    # Features (keep it small & interpretable)
    features = ["temp_c", "humidity", "gas_ppm", "temp_ma5", "hum_ma5", "gas_ma5"]
    X = df[features]
    y = df["label"]

    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.25, random_state=0, stratify=y
    )

    # Tiny tree for explainability
    clf = DecisionTreeClassifier(max_depth=4, random_state=0)
    clf.fit(Xtr, ytr)

    # Metrics
    ypred = clf.predict(Xte)
    print(classification_report(yte, ypred))

    # Save model
    model_path = OUT / "model.joblib"
    joblib.dump(clf, model_path)
    print(f"Saved model to {model_path}")

    # Confusion matrix plot
    cm = confusion_matrix(yte, ypred, labels=["Good","Moderate","Poor"])
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Good","Moderate","Poor"])
    fig = plt.figure()
    disp.plot(values_format="d")
    plt.title("Confusion Matrix (Test)")
    fig.savefig(OUT / "confusion_matrix.png", bbox_inches="tight")
    plt.close(fig)

    # Class balance plot (for report)
    fig2 = plt.figure()
    df["label"].value_counts().plot(kind="bar")
    plt.title("Class Balance in Training Data (All)")
    plt.xlabel("Class")
    plt.ylabel("Count")
    fig2.savefig(OUT / "class_balance.png", bbox_inches="tight")
    plt.close(fig2)

    # Optional: visualize the tree (small trees only)
    fig3 = plt.figure(figsize=(10,6))
    plot_tree(clf, feature_names=features, class_names=["Good","Moderate","Poor"], filled=True)
    fig3.savefig(OUT / "decision_tree.png", bbox_inches="tight")
    plt.close(fig3)

if __name__ == "__main__":
    main()
