import pandas as pd
import os

# Base path where the parsed JSON outputs will be saved
output_base = "data"

def parse_logs(input_path, prefix):
    """
    Parse a log CSV file and generate multiple JSON outputs:
    1. Filtered logs (severity >= 7, sorted by timestamp descending).
    2. All logs (including duplicates, sorted by rule.id ascending).
    3. Unique logs by rule description, including count, sorted by severity.

    Args:
        input_path (str): Path to the input CSV log file.
        prefix (str): Prefix to differentiate between datasets (e.g., "real" or "simulated").

    Outputs:
        - {prefix}_parsed_logs_filtered.json
        - {prefix}_parsed_logs_all.json
        - {prefix}_parsed_logs_by_unique_rule_description.json
    """
    # Check if the input CSV exists
    if not os.path.exists(input_path):
        print(f"[✗] File not found: {input_path}")
        return

    # Output file paths
    output_filtered = os.path.join(output_base, f"{prefix}_parsed_logs_filtered.json")
    output_all = os.path.join(output_base, f"{prefix}_parsed_logs_all.json")
    output_by_description = os.path.join(output_base, f"{prefix}_parsed_logs_by_unique_rule_description.json")

    # ---- STEP 1: Load the CSV ----
    df = pd.read_csv(input_path)

    # Keep only the relevant columns
    df = df[["timestamp", "agent.name", "rule.level", "rule.id", "rule.description"]]

    # Convert timestamps to datetime objects
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        format="%b %d, %Y @ %H:%M:%S.%f",
        errors="coerce"  # Invalid values become NaT
    )

    # ---- PARSE 1: Filtered events (severity >= 7) ----
    df_filtered = df[df["rule.level"] >= 7].sort_values(by="timestamp", ascending=False)
    df_filtered.to_json(output_filtered, orient="records", lines=True)

    # ---- PARSE 2: All events (with duplicates), sorted by rule.id ----
    df_all = df.sort_values(by="rule.id", ascending=True)
    df_all.to_json(output_all, orient="records", lines=True)

    # ---- PARSE 3: Unique rule descriptions ----
    # Count occurrences of each rule description
    count = df["rule.description"].value_counts().rename("count").reset_index()
    count.rename(columns={"index": "rule.description"}, inplace=True)

    # Keep the most recent event per description
    df_unique = (
        df.sort_values(by="timestamp", ascending=False)
          .drop_duplicates(subset="rule.description")
    )
    # Merge with counts and sort by severity level
    df_unique = pd.merge(df_unique, count, on="rule.description")
    df_unique = df_unique.sort_values(by="rule.level", ascending=False)

    df_unique.to_json(output_by_description, orient="records", lines=True)

    print(f"[✓] {prefix}: processed successfully.")


if __name__ == "__main__":
    # Define input CSV files for real and simulated logs
    files = {
        "real": "../data/real_events.csv",
        "simulated": "../data/simulated_events.csv"
    }
    # Parse both datasets
    for prefix, path in files.items():
        parse_logs(path, prefix)
