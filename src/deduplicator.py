def is_duplicate(new_id, existing_df):
    if "Complaint ID" not in existing_df.columns:
        return False
    return new_id in existing_df["Complaint ID"].values
