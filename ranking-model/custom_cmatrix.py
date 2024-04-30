import pandas as pd
import matplotlib.pyplot as plt

to_check = 'blind_db'

# Define a function to determine the predicted class based on the probabilities
def get_predicted_class(row):
    return 'positive' if row['classification_1'] > row['classification_0'] else 'negative'

if to_check == 'rsna':
    # custom confusion matrix
    # Load the CSV file into a DataFrame
    df = pd.read_csv('updated_rsna_train.csv')
    df = df.dropna(subset=['BIRADS'])

    # Apply the function to create a new column for predicted classification
    df['predicted'] = df.apply(get_predicted_class, axis=1)

    # keep one entry per patient (per-patient diagnostics)
    df = df.sort_values(by=['patient_id','predicted'])
    df = df.drop_duplicates(subset='patient_id', keep='last')

    # Create a pivot table (or crosstab) with counts of predicted classifications for each BIRADS category
    result_matrix = pd.crosstab(df['BIRADS'], df['predicted'], rownames=['BIRADS'], colnames=['Predicted'])

    print(result_matrix)

elif to_check == 'blind_db':
    # custom confusion matrix
    # Load the CSV file into a DataFrame
    df = pd.read_excel('updated_blind_db.xlsx', engine='openpyxl')
    df = df.dropna(subset=['birads_image'])

    # Apply the function to create a new column for predicted classification
    df['predicted'] = df.apply(get_predicted_class, axis=1)

    # Create a pivot table (or crosstab) with counts of predicted classifications for each BIRADS category
    result_matrix = pd.crosstab(df['birads_image'], df['predicted'], rownames=['BIRADS'], colnames=['Predicted'])

    print(result_matrix)

    # sorted results by severity
    # Sort the DataFrame based on 'classification_1' in descending order
    sorted_df = df.sort_values(by='classification_1', ascending=False)

    # Selecting only the columns of interest
    output_df = sorted_df[['classification_1', 'birads_image', 'image_id']]

    # Output the results
    print(output_df)

    # Optionally, save the sorted DataFrame to a new Excel file
    output_df.to_excel('sorted_data.xlsx', index=False)

    # histogram
    birads_categories = df['birads_image'].unique()
    n_categories = len(birads_categories)

    # Create a figure with multiple subplots
    fig, axes = plt.subplots(nrows=1, ncols=n_categories, figsize=(5 * n_categories, 4), sharey=True)

    # Loop through each BIRADS category and plot a histogram
    for ax, birads in zip(axes, birads_categories):
        subset = df[df['birads_image'] == birads]['classification_1']
        ax.hist(subset, bins=10, alpha=0.7)
        ax.set_title(f'BIRADS {birads}')
        ax.set_xlabel('Classification_1 Values')
        if ax is axes[0]:  # Only add y-label to the first subplot to avoid repetition
            ax.set_ylabel('Frequency')

    plt.tight_layout()
    plt.show()
