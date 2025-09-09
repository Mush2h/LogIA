import pandas as pd

# Input CSV file path
input_path = "../data/real_events.csv"

# Output paths
output_filtered = "../data/parsed_logs_filtered.json"
output_all = "../data/parsed_logs_all.json"
output_by_description = "../data/parsed_logs_by_unique_rule_description.json"

def parse_logs(input_path, output_filtered, output_all, output_by_description):
    # Load CSV
    df = pd.read_csv(input_path)

    # Keep only the key columns
    df = df[["timestamp", "agent.name", "rule.level", "rule.id", "rule.description"]]

    # Convert timestamp column to datetime
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        format="%b %d, %Y @ %H:%M:%S.%f",
        errors='coerce'
    )

    # ------------------ PARSE 1: Filter by level >= 7 ------------------
    df_filtered = df[df["rule.level"] >= 7].copy()
    df_filtered = df_filtered.sort_values(by="timestamp", ascending=False)
    df_filtered.to_json(output_filtered, orient="records", lines=True)

    # ------------------ PARSE 2: All events (with duplicates), sorted by rule.id ------------------
    df_all = df.copy()
    df_all = df_all.sort_values(by="rule.id", ascending=True)
    df_all.to_json(output_all, orient="records", lines=True)

    # ------------------ PARSE 3: Unique descriptions + counter + sort by level ------------------
    # Count occurrences of each description
    count = df["rule.description"].value_counts().rename("count").reset_index()
    count.rename(columns={"index": "rule.description"}, inplace=True)

    # Get unique events (latest by timestamp)
    df_unique_descriptions = (
        df.sort_values(by="timestamp", ascending=False)
          .drop_duplicates(subset="rule.description")
    )

    # Merge with counts
    df_unique_descriptions = pd.merge(df_unique_descriptions, count, on="rule.description")

    # Sort by threat level
    df_unique_descriptions = df_unique_descriptions.sort_values(by="rule.level", ascending=False)

    # Export
    df_unique_descriptions.to_json(output_by_description, orient="records", lines=True)

    print(f"[✓] Parse with level >= 7 exported to: {output_filtered}")
    print(f"[✓] All events (sorted by rule.id) exported to: {output_all}")
    print(f"[✓] Unique events by rule.description sorted by level with count exported to: {output_by_description}")

# Run if script is executed directly
if __name__ == "__main__":
    parse_logs(input_path, output_filtered, output_all, output_by_description)
