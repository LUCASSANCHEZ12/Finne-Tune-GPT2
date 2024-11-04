import pandas as pd
from sklearn.model_selection import train_test_split

# Read the CSV file
dataframe = pd.read_csv("dataset.csv")

# Divide the dataframe in sets of training and testing
train_df, test_df = train_test_split(dataframe, test_size=0.1, random_state=42)

# Optional: Save the resulting dataframes in CSV files
train_df.to_csv("train_dataset.csv", index=False)
test_df.to_csv("test_dataset.csv", index=False)

with open('question_answers_train.txt', 'w') as f:
  for index, row in train_df.iterrows():
    
    f.write('[Q] ' + row['Q'] + '\n')
    f.write('[A] ' + row['A'] + '\n\n') 
      
with open('question_answers_validation.txt', 'w') as f:
  for index, row in test_df.iterrows():

    f.write('[Q] ' + row['Q'] + '\n')
    f.write('[A] ' + row['A'] + '\n\n') 