import pandas as pd
from pathlib import Path

def write_to_excel(data, output_path):
    output_path = Path(output_path)

    if output_path.exists():
        df = pd.read_excel(output_path)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    else:
        df = pd.DataFrame([data])

    df.to_excel(output_path, index=False)
