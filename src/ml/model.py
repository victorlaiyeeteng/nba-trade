import pandas as pd
from src.db import connect_supabase, close_connection_supabase
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

def get_dates(d):
    year, month, day = d.year, d.month, d.day
    if month >= 10:
        season = year + 1
    else: 
        season = year
    return year, month, day, season

# Load tables
conn = connect_supabase()
current_season = get_dates(datetime.utcnow())
player_stats = pd.read_sql(f"SELECT * FROM player_stats WHERE season <> {current_season[-1]}", conn)
outcome_stats = pd.read_sql(f"SELECT * FROM trade_outcome WHERE season <> {current_season[-1]}", conn)

df = player_stats.merge(outcome_stats, on=['playerid', "season"])
le = LabelEncoder()
df['label'] = le.fit_transform(df['outcome'])
print("Finished preparing dataset")

X = df.drop(columns=['playerid', 'season', 'outcome', 'label'])
y = df['label']


# ML Training

# X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2)

# clf = RandomForestClassifier(n_estimators=100, random_state=42)
# clf.fit(X_train, y_train)
# print(classification_report(y_test, clf.predict(X_test), target_names=le.classes_))
