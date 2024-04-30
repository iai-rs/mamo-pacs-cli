import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

# -------------- Prepare the data --------------
# Load .csv file
df = pd.read_csv('updated_rsna_per_breast.csv')

# Extract columns of interest (input/output to model)
columns_of_interest = ['patient_id', 'BIRADS'] + [f'inference_{i}' for i in range(1, 513)]
df_filtered = df[columns_of_interest]

groups_birads_2 = df_filtered[df_filtered['BIRADS'] == 2].groupby('patient_id').groups.keys()

# Find the number of unique patients for BIRADS 2, or set a target number.
num_patients_birads_2 = len(groups_birads_2)

# For BIRADS 0 and 1, randomly sample patient_ids up to the number of unique BIRADS 2 patients.
# This ensures all records for a selected patient are included.
patient_ids_birads_0 = df_filtered[df_filtered['BIRADS'] == 0].groupby('patient_id').sample(n=1).sample(n=num_patients_birads_2, replace=False)['patient_id'].unique()
patient_ids_birads_1 = df_filtered[df_filtered['BIRADS'] == 1].groupby('patient_id').sample(n=1).sample(n=num_patients_birads_2, replace=False)['patient_id'].unique()

# Filter the original dataframe for these patient_ids
df_birads_0_balanced = df_filtered[df_filtered['patient_id'].isin(patient_ids_birads_0)]
df_birads_1_balanced = df_filtered[df_filtered['patient_id'].isin(patient_ids_birads_1)]

# The DataFrame for BIRADS 2 is already defined as df_birads_2
# Concatenate the balanced dataframes
df_filtered = pd.concat([df_birads_0_balanced, df_birads_1_balanced, df_filtered[df_filtered['BIRADS'] == 2]])

def aggregate_rows(rows):
    birads = rows['BIRADS'].iloc[0]  # assuming birads are consistent for patient (iloc is used to slice df in pandas)
    flattened = rows.iloc[:, 2:].values.flatten()  # flatten inference data to single array
    if len(flattened) == 512 * 2:  # check if we need to duplicate data (patients with 2 images)
        flattened = np.tile(flattened, 2)
    return pd.Series(np.concatenate([[birads], flattened]))  # pd.Series converts a np array to a pd Series object


# Aggregate data for each patient (apply aggregate_rows to each patient)
patient_data_with_labels = df_filtered.groupby('patient_id').apply(aggregate_rows)

# Separate the aggregated data
y = patient_data_with_labels.iloc[:, 0].to_numpy()  # y (labels)
y = y.astype(int)  # labels are whole numbers
x = patient_data_with_labels.iloc[:, 1:].to_numpy()  # x (features)

print(f"Patient data - x shape: {x.shape}, y shape: {y.shape}")

# -------------- Create and fit model --------------
model = Sequential()
model.add(Dense(256, activation='relu', input_shape=(2048,)))
model.add(Dropout(0.2))
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(3, activation='softmax'))

optimizer = Adam(lr=0.00001)
model.compile(optimizer=optimizer,
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

x_train, x_val, y_train, y_val = train_test_split(x, y, test_size=0.2)

model.fit(x_train, y_train, epochs=500, batch_size=32)

# ------------- Validate model ---------------
predictions_prob = model.predict(x_val)
predictions = np.argmax(predictions_prob, axis=1)
conf_matrix = confusion_matrix(y_val, predictions)  # compute the confusion matrix
print(conf_matrix)
