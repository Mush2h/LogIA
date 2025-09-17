import pandas as pd
import os

# Base path for outputs
output_base = "data"

def parse_logs(input_path, prefix):
    # Check if the file exists
    if not os.path.exists(input_path):
        print(f"[✗] File not found: {input_path}")
        return

    # Output paths
    output_filtered = os.path.join(output_base, f"{prefix}_parsed_logs_filtered.json")
    output_all = os.path.join(output_base, f"{prefix}_parsed_logs_all.json")
    output_by_description = os.path.join(output_base, f"{prefix}_parsed_logs_by_unique_rule_description.json")

    # Load CSV
    df = pd.read_csv(input_path)

    # Keep only the key columns
    df = df[["timestamp", "agent.name", "rule.level", "rule.id", "rule.description"]]

    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        format="%b %d, %Y @ %H:%M:%S.%f",
        errors='coerce'
    )

    # ---- PARSE 1: Events with severity level >= 7 ----
    df_filtered = df[df["rule.level"] >= 7].sort_values(by="timestamp", ascending=False)
    df_filtered.to_json(output_filtered, orient="records", lines=True)

    # ---- PARSE 2: All events (with duplicates), sorted by rule.id ----
    df_all = df.sort_values(by="rule.id", ascending=True)
    df_all.to_json(output_all, orient="records", lines=True)

    # ---- PARSE 3: Unique rule descriptions with count, sorted by severity ----
    count = df["rule.description"].value_counts().rename("count").reset_index()
    count.rename(columns={"index": "rule.description"}, inplace=True)

    df_unique = (
        df.sort_values(by="timestamp", ascending=False)
          .drop_duplicates(subset="rule.description")
    )
    df_unique = pd.merge(df_unique, count, on="rule.description")
    df_unique = df_unique.sort_values(by="rule.level", ascending=False)

    df_unique.to_json(output_by_description, orient="records", lines=True)

    print(f"[✓] {prefix}: processed successfully.")

if __name__ == "__main__":
    files = {
        "real": "../data/real_events.csv",
        "simulated": "../data/simulated_events.csv"
    }
    for prefix, path in files.items():
        parse_logs(path, prefix)
