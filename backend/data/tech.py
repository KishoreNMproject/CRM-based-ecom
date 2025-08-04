import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
import subprocess

# Install these libraries if you don't have them
try:
    import shap
    import lime
    from lime import lime_tabular
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.tree import DecisionTreeClassifier, export_text
    from sklearn.model_selection import train_test_split
except ImportError:
    print("Required libraries 'shap', 'lime', 'scikit-learn' not found. Installing them now...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "shap", "lime", "scikit-learn"])
    import shap
    import lime
    from lime import lime_tabular
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.tree import DecisionTreeClassifier, export_text
    from sklearn.model_selection import train_test_split

def create_sample_data():
    """
    Creates a synthetic dataset for demonstration purposes.
    This function is used if no input CSV is provided.
    The data is intentionally varied to ensure a binary classification problem
    (high-value vs. not-high-value) can be created.
    """
    print("No CSV file provided. Creating a sample dataset for demonstration...")
    data = {
        'InvoiceNo': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        'InvoiceDate': [
            '2024-07-28', '2024-07-29', '2024-07-25', '2024-07-15', '2024-07-29',
            '2024-07-20', '2024-07-10', '2024-07-05', '2024-07-02', '2024-08-01',
            '2024-07-01', '2024-07-01', '2024-07-01', '2024-07-02', '2024-07-03',
            '2024-07-28', '2024-07-29', '2024-07-29', '2024-07-30', '2024-07-31'
        ],
        'CustomerID': [101, 102, 101, 103, 101, 104, 102, 105, 103, 101, 104, 105, 102, 103, 101, 106, 107, 108, 106, 107],
        'UnitPrice': [10.5, 25.0, 12.0, 5.0, 15.0, 20.0, 30.0, 50.0, 8.0, 18.0, 22.0, 45.0, 35.0, 10.0, 20.0, 7.5, 9.0, 11.5, 12.5, 14.0]
    }
    df = pd.DataFrame(data)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    return df

def calculate_rfm(df, output_dir):
    """
    Calculates Recency, Frequency, and Monetary values for each customer.
    
    Args:
        df (pd.DataFrame): Input DataFrame with transaction data.
        output_dir (str): The directory to save the output files.
        
    Returns:
        pd.DataFrame: DataFrame with RFM scores or None if calculation fails.
    """
    print("\nStarting RFM analysis...")
    snapshot_date = datetime.now()
    
    # Check for required columns
    required_cols = ['CustomerID', 'InvoiceDate', 'UnitPrice']
    if not all(col in df.columns for col in required_cols):
        print(f"Error: Input CSV must contain all of the following columns: {required_cols}. Exiting.")
        return None

    # RFM Calculation
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda date: (snapshot_date - date.max()).days,
        'InvoiceNo': 'count',
        'UnitPrice': 'sum'
    })
    
    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    rfm = rfm.reset_index()
    
    rfm_path = os.path.join(output_dir, 'rfm_output.csv')
    rfm.to_csv(rfm_path, index=False)
    print(f"RFM analysis complete. Saved to '{os.path.abspath(rfm_path)}'.")
    
    return rfm

def train_and_explain_models(rfm_df):
    """
    Trains a classification model and uses it for SHAP and LIME explanations.
    
    Args:
        rfm_df (pd.DataFrame): DataFrame with RFM scores.
        
    Returns:
        tuple: (random_forest_model, decision_tree_model, X, y) or (None, None, None, None)
    """
    print("\nPreparing to train models for SHAP, LIME, and business rules...")
    
    # Create a target variable: 'is_high_value' based on RFM scores
    # A simple heuristic: high value if Recency is low and F/M are high
    rfm_df['is_high_value'] = (
        (rfm_df['Recency'] < rfm_df['Recency'].median()) &
        (rfm_df['Frequency'] > rfm_df['Frequency'].median()) &
        (rfm_df['Monetary'] > rfm_df['Monetary'].median())
    ).astype(int)
    
    X = rfm_df[['Recency', 'Frequency', 'Monetary']]
    y = rfm_df['is_high_value']
    
    # Check if the target variable has more than one class.
    # This is a critical check to avoid the IndexError with LIME and SHAP.
    if y.nunique() < 2:
        print("\nWarning: The target variable 'is_high_value' has only one class.")
        print("SHAP, LIME, and Business Rules cannot be generated without a binary classification problem.")
        return None, None, None, None

    # Train a Random Forest model for SHAP/LIME
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X, y)
    
    # Train a Decision Tree model for business rules
    dt_model = DecisionTreeClassifier(max_depth=3, random_state=42)
    dt_model.fit(X, y)

    print("Models trained successfully.")
    return rf_model, dt_model, X, y

def perform_shap_analysis(model, data, output_dir):
    """
    Performs SHAP analysis and saves the results to a CSV.
    
    Args:
        model: Trained scikit-learn model.
        data (pd.DataFrame): DataFrame used for training.
        output_dir (str): The directory to save the output files.
    """
    print("\nPerforming SHAP analysis...")
    
    try:
        # Use TreeExplainer for tree-based models
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(data)
        
        # The shap_values object is a list of arrays for classification, we need the values for class 1
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        shap_df = pd.DataFrame(shap_values, columns=data.columns + '_SHAP_value')
        shap_df.insert(0, 'CustomerID', data.index)
        
        shap_path = os.path.join(output_dir, 'shap.csv')
        shap_df.to_csv(shap_path, index=False)
        print(f"SHAP analysis complete. Saved to '{os.path.abspath(shap_path)}'.")
    except Exception as e:
        print(f"An error occurred during SHAP analysis: {e}. SHAP file was not created.")

def perform_lime_analysis(model, data, features, output_dir):
    """
    Performs LIME analysis for a few samples and saves the results to a CSV.
    
    Args:
        model: Trained scikit-learn model.
        data (pd.DataFrame): DataFrame used for training.
        features (list): List of feature names.
        output_dir (str): The directory to save the output files.
    """
    print("\nPerforming LIME analysis on a few samples...")
    
    try:
        explainer = lime_tabular.LimeTabularExplainer(
            training_data=np.array(data),
            feature_names=features,
            class_names=['not_high_value', 'is_high_value'],
            mode='classification'
        )
        
        lime_results = []
        # Generate explanations for the first 5 customers
        for i in range(min(5, len(data))):
            exp = explainer.explain_instance(
                data.iloc[i], 
                model.predict_proba, 
                num_features=len(features)
            )
            
            # Extract explanation features and weights
            explanation_dict = {f'feature_{j+1}': f'{feature}={weight:.2f}' for j, (feature, weight) in enumerate(exp.as_list())}
            lime_results.append({'CustomerID': data.index[i], **explanation_dict})
        
        lime_df = pd.DataFrame(lime_results)
        
        lime_path = os.path.join(output_dir, 'lime.csv')
        lime_df.to_csv(lime_path, index=False)
        print(f"LIME analysis complete. Saved to '{os.path.abspath(lime_path)}'.")
    except Exception as e:
        print(f"An error occurred during LIME analysis: {e}. LIME file was not created.")

def extract_business_rules(model, feature_names, output_dir):
    """
    Extracts business rules from a trained Decision Tree model.
    
    Args:
        model: Trained scikit-learn Decision Tree model.
        feature_names (list): List of feature names.
        output_dir (str): The directory to save the output files.
    """
    print("\nExtracting business rules from the Decision Tree model...")
    try:
        tree_rules = export_text(model, feature_names=feature_names)
        
        # Split the text output into a list of rules
        rules_list = [rule.strip() for rule in tree_rules.split('\n') if rule.strip()]
        
        # Save the rules to a CSV file
        rules_df = pd.DataFrame({'BusinessRule': rules_list})
        
        rules_path = os.path.join(output_dir, 'business_rules.csv')
        rules_df.to_csv(rules_path, index=False)
        print(f"Business rules extracted. Saved to '{os.path.abspath(rules_path)}'.")
    except Exception as e:
        print(f"An error occurred during business rule extraction: {e}. Rules file was not created.")

def main():
    """
    Main function to run all analysis steps.
    """
    # Create the output directory
    output_dir = 'data_output'
    os.makedirs(output_dir, exist_ok=True)
    print(f"All output files will be saved in the directory: '{os.path.abspath(output_dir)}'.")
    
    # Ask the user for a CSV file path
    file_path = input("\nEnter the path to your CSV file (e.g., 'data.csv'). Press Enter to use a sample dataset: ")
    
    if file_path:
        try:
            df = pd.read_csv(file_path)
            # Ensure the InvoiceDate column is in datetime format
            df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
            print(f"Successfully loaded data from '{file_path}'.")
        except FileNotFoundError:
            print(f"Error: File not found at '{file_path}'. Using sample data instead.")
            df = create_sample_data()
        except Exception as e:
            print(f"An error occurred while loading the file: {e}. Using sample data instead.")
            df = create_sample_data()
    else:
        df = create_sample_data()

    # Step 1: RFM Analysis
    rfm_df = calculate_rfm(df, output_dir)
    if rfm_df is None:
        print("\nProcess aborted due to missing data columns.")
        return

    # Step 2: Train models
    rf_model, dt_model, X, y = train_and_explain_models(rfm_df)
    
    # Check if the models were successfully trained (i.e., we have two classes)
    if rf_model is not None and dt_model is not None:
        # Step 3: SHAP Analysis
        perform_shap_analysis(rf_model, X, output_dir)
        
        # Step 4: LIME Analysis
        perform_lime_analysis(rf_model, X, features=['Recency', 'Frequency', 'Monetary'], output_dir=output_dir)
        
        # Step 5: Business Rules Extraction
        extract_business_rules(dt_model, feature_names=['Recency', 'Frequency', 'Monetary'], output_dir=output_dir)
    else:
        print("\nSkipping SHAP, LIME, and Business Rules generation as the data is not suitable for classification.")
    
    print(f"\n*** All tasks completed. Check the '{os.path.abspath(output_dir)}' directory for the generated CSV files. ***")

if __name__ == "__main__":
    main()

