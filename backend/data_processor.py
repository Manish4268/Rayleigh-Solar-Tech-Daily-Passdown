
import os, io
import pandas as pd
from statistics import mean, stdev, median, quantiles
from dotenv import load_dotenv

# Optional: Azure SDK (faster). If not installed, we'll use requests for SAS URL and container listing.
try:
    from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient
except Exception:
    BlobServiceClient = ContainerClient = BlobClient = None

# -------------------- ENV SETUP --------------------
load_dotenv()

# REQUIRED file name (enforced strictly)
REQUIRED_BLOB_NAME = os.getenv("BLOB_NAME", "BaseLine.xlsx")

"""
Supported configurations (set EXACTLY ONE of these modes):

1) Single Blob SAS URL (must point to BaseLine.xlsx exactly)
   BLOB_SAS_URL="https://<acct>.blob.core.windows.net/<container>/BaseLine.xlsx?sv=..."

2) Container SAS (must contain BaseLine.xlsx)
   AZURE_CONTAINER_URL="https://<acct>.blob.core.windows.net/<container>"
   AZURE_CONTAINER_SAS="?sv=...&sp=rl..."   # needs r + l to list/confirm
   # optional: BLOB_NAME="BaseLine.xlsx" (default)

3) Connection String (must contain BaseLine.xlsx)
   AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=...;"
   CONTAINER_NAME="baseline-xlsx"
   # optional: BLOB_NAME="BaseLine.xlsx" (default)
"""


# -------------------- STRICT LOADERS --------------------
def _read_xlsx_from_blob_sas_url(blob_sas_url: str) -> pd.DataFrame:
    """Download BaseLine.xlsx via a single Blob SAS URL (exact file)."""
    # Quick sanity: enforce URL targets REQUIRED_BLOB_NAME
    lower = blob_sas_url.lower()
    if not (lower.endswith(REQUIRED_BLOB_NAME.lower()) or f"/{REQUIRED_BLOB_NAME.lower()}?" in lower):
        raise FileNotFoundError(f"BLOB_SAS_URL must point to '{REQUIRED_BLOB_NAME}'.")
    if BlobClient is None:
        import requests
        r = requests.get(blob_sas_url)
        r.raise_for_status()
        return pd.read_excel(io.BytesIO(r.content))
    data = BlobClient.from_blob_url(blob_sas_url).download_blob().readall()
    return pd.read_excel(io.BytesIO(data))

def _strict_read_blob_from_container_sas(container_url: str, sas_token, blob_name: str):
    """
    Accepts either:
    - combined container SAS in container_url (has '?'), or
    - split mode: container_url (no '?') + sas_token ("?sv=...").
    Builds: https://<acct>.blob.core.windows.net/<container>/<blob>?<token>
    """
    import io, requests, pandas as pd
    from urllib.parse import urlsplit, urlunsplit

    if "?" in container_url:
        # Combined mode from Azure portal
        parts = urlsplit(container_url)
        if not parts.query:
            raise ValueError("Container URL has '?' but no query string.")
        # Insert '/BaseLine.xlsx' before the query
        path = parts.path.rstrip("/") + "/" + blob_name
        blob_url = urlunsplit((parts.scheme, parts.netloc, path, parts.query, ""))  # keep same token
    else:
        # Split mode (old behavior)
        if not sas_token:
            raise ValueError("AZURE_CONTAINER_SAS is required when container URL has no query.")
        if not sas_token.startswith("?"):
            sas_token = "?" + sas_token
        blob_url = container_url.rstrip("/") + "/" + blob_name + sas_token

    # Optional: print safe URL (without sig) for debugging
    safe = blob_url.split("&sig=")[0]
    print(f"🔐 Fetching: {safe}")

    r = requests.get(blob_url, stream=True)
    if r.status_code == 200:
        return pd.read_excel(io.BytesIO(r.content))
    if r.status_code == 404:
        raise FileNotFoundError(f"'{blob_name}' not found in container.")
    if r.status_code == 403:
        raise PermissionError("403 Forbidden: SAS lacks 'r', expired times, or IP restriction (sip) mismatch.")
    raise RuntimeError(f"Unexpected status {r.status_code} fetching blob.")





def _strict_read_blob_from_conn_str(conn_str: str, container: str, blob_name: str):
    """Read exactly BaseLine.xlsx via connection string. Raises if missing."""
    if BlobServiceClient is None:
        raise RuntimeError("azure-storage-blob is required for connection-string reads (pip install azure-storage-blob).")
    bsc = BlobServiceClient.from_connection_string(conn_str)
    cont = bsc.get_container_client(container)
    bc = cont.get_blob_client(blob_name)
    if not bc.exists():
        raise FileNotFoundError(f"Required blob '{blob_name}' not found in container '{container}'.")
    data = bc.download_blob().readall()
    return pd.read_excel(io.BytesIO(data))


def _load_baseline_df():
    """STRICT: load only 'BaseLine.xlsx' from Azure. If missing/inaccessible, raise. No local fallback."""
    blob_sas_url = os.getenv("BLOB_SAS_URL")
    container_url = os.getenv("AZURE_CONTAINER_URL")
    sas_token = os.getenv("AZURE_CONTAINER_SAS")
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container = os.getenv("CONTAINER_NAME")
    blob_name = REQUIRED_BLOB_NAME  # enforced exact name

    modes = sum(bool(x) for x in [blob_sas_url, (container_url and sas_token), (conn_str and container)])
    if modes != 1:
        raise RuntimeError(
            "Configure exactly ONE source:\n"
            "1) BLOB_SAS_URL (must point to BaseLine.xlsx), OR\n"
            "2) AZURE_CONTAINER_URL + AZURE_CONTAINER_SAS, OR\n"
            "3) AZURE_STORAGE_CONNECTION_STRING + CONTAINER_NAME"
        )

    if blob_sas_url:
        print("🔐 Loading BaseLine.xlsx via BLOB_SAS_URL (strict)")
        return _read_xlsx_from_blob_sas_url(blob_sas_url)

    if container_url and sas_token:
        print("🔐 Loading BaseLine.xlsx via Container SAS (strict)")
        return _strict_read_blob_from_container_sas(container_url, sas_token, blob_name)

    # connection string
    print("🔐 Loading BaseLine.xlsx via Connection String (strict)")
    return _strict_read_blob_from_conn_str(conn_str, container, blob_name)


# -------------------- STATS HELPERS --------------------
def calculate_box_plot_stats(values):
    """Calculate box plot statistics from a list of values (keeps your original 'count = len/4')."""
    if not values or len(values) == 0:
        return {
            'min': 0, 'q1': 0, 'median': 0, 'q3': 0, 'max': 0,
            'mean': 0, 'std': 0, 'count': 0
        }

    sorted_values = sorted(values)
    n = len(sorted_values)

    if n >= 4:
        q_values = quantiles(sorted_values, n=4)
        q1, median_val, q3 = q_values[0], q_values[1], q_values[2]
    else:
        q1 = sorted_values[0]
        median_val = median(sorted_values)
        q3 = sorted_values[-1]

    return {
        'min': round(min(sorted_values), 2),
        'q1': round(q1, 2),
        'median': round(median_val, 2),
        'q3': round(q3, 2),
        'max': round(max(sorted_values), 2),
        'mean': round(mean(sorted_values), 2),
        'std': round(stdev(sorted_values) if len(sorted_values) > 1 else 0, 2),
        'count': len(sorted_values) / 4  # preserved from your code
    }


# -------------------- CORE EXTRACTORS (STRICT) --------------------
def extract_chart_data():
    """Extract chart data from strictly-loaded BaseLine.xlsx."""
    parameter_mapping = {
        'PCE': 'PCE (%)',
        'FF': 'FF (%)',
        'Max Power': 'Max Power (mW/cm2)',
        'HI': 'HI (%)',
        'I_sc': 'J_sc (mA/cm2)',
        'V_oc': 'V_oc (V)',
        'R_series': 'R_series (Ohm.cm2)',
        'R_shunt': 'R_shunt (Ohm.cm2)'
    }
    empty_stats = {'min': 0, 'q1': 0, 'median': 0, 'q3': 0, 'max': 0, 'mean': 0, 'std': 0, 'count': 0}
    chart_data = {k: [] for k in parameter_mapping}

    df = _load_baseline_df()  # <-- will raise if BaseLine.xlsx not accessible
    print(f"✅ Excel loaded. Shape: {df.shape}")

    batch_column = next((c for c in df.columns if 'batch' in str(c).lower() or 'id' in str(c).lower()), None)
    batches = df[batch_column].unique() if batch_column else ['Baseline']
    colmap = {str(c).upper(): c for c in df.columns}

    for param, col in parameter_mapping.items():
        col_key = colmap.get(col.upper())
        if not col_key:
            # Try fuzzy match
            for alt in df.columns:
                if param.lower() in str(alt).lower():
                    col_key = alt
                    print(f"✅ Using alternative for {param}: {alt}")
                    break
        if not col_key:
            s = dict(empty_stats); s['batch'] = 'No Data'
            chart_data[param].append(s)
            continue

        if batch_column:
            for b in batches:
                vals = pd.to_numeric(df.loc[df[batch_column] == b, col_key], errors='coerce').dropna().tolist()
                s = calculate_box_plot_stats(vals) if vals else dict(empty_stats)
                s['batch'] = str(b)
                chart_data[param].append(s)
        else:
            vals = pd.to_numeric(df[col_key], errors='coerce').dropna().tolist()
            s = calculate_box_plot_stats(vals) if vals else dict(empty_stats)
            s['batch'] = 'Baseline'
            chart_data[param].append(s)

    return chart_data


def extract_device_yield_data():
    """Extract device yield (2.5% quantiles + batch averages) strictly from BaseLine.xlsx."""
    # Updated to include all 8 parameters matching charts_api.py
    yield_parameters = {
        'PCE': 'PCE (%)',
        'FF': 'FF (%)',
        'Max Power': 'Max Power (mW/cm2)',
        'HI': 'HI (%)',
        'I_sc': 'J_sc (mA/cm2)',
        'V_oc': 'V_oc (V)',
        'R_series': 'R_series (Ohm.cm2)',
        'R_shunt': 'R_shunt (Ohm.cm2)'
    }

    df = _load_baseline_df()  # strict load

    batch_column = next((c for c in df.columns if 'batch' in str(c).lower() or 'id' in str(c).lower()), None)
    if not batch_column:
        raise ValueError("No batch column found for device yield analysis (strict mode).")

    batches = sorted(df[batch_column].unique())
    colmap = {str(c).upper(): c for c in df.columns}

    result = {
        'parameters': list(yield_parameters.keys()),
        'batches': [str(b) for b in batches],
        'quantiles': {},
        'batch_averages': {}
    }

    for param, col_name in yield_parameters.items():
        col_key = colmap.get(col_name.upper())
        if col_key is None:
            print(f"⚠️ Column not found for {param}: {col_name}")
            continue

        all_values = pd.to_numeric(df[col_key], errors='coerce').dropna().tolist()
        if len(all_values) > 0:
            # 2.5% quantile is first of 40-quantiles
            q2_5 = round(quantiles(all_values, n=40)[0], 3)
            result['quantiles'][param] = q2_5

            batch_avgs = []
            for b in batches:
                vals = pd.to_numeric(df.loc[df[batch_column] == b, col_key], errors='coerce').dropna().tolist()
                avg = round(mean(vals), 3) if vals else 0
                batch_avgs.append(avg)
            result['batch_averages'][param] = batch_avgs
            print(f"✅ {param}: 2.5% quantile = {q2_5}, batch averages computed")
        else:
            result['quantiles'][param] = 0
            result['batch_averages'][param] = [0] * len(batches)

    return result


def extract_iv_repeatability_data():
    """Extract IV repeatability (daily avg + CV for last 10 days) strictly from BaseLine.xlsx."""
    df = _load_baseline_df()  # strict load

    date_column = next((c for c in df.columns if 'date' in str(c).lower()), None)
    if not date_column:
        raise ValueError("No date column found for IV repeatability analysis (strict mode).")

    colmap = {str(c).upper(): c for c in df.columns}
    # Updated to include all 8 parameters matching charts_api.py
    iv_parameters = {
        'PCE': 'PCE (%)',
        'FF': 'FF (%)',
        'Max Power': 'Max Power (mW/cm2)',
        'HI': 'HI (%)',
        'I_sc': 'J_sc (mA/cm2)',
        'V_oc': 'V_oc (V)',
        'R_series': 'R_series (Ohm.cm2)',
        'R_shunt': 'R_shunt (Ohm.cm2)'
    }

    # Convert to datetime (handles Excel serials)
    if str(df[date_column].dtype) in ('float64', 'int64'):
        try:
            df[date_column] = pd.to_datetime(df[date_column], origin='1899-12-30', unit='D')
        except Exception:
            df[date_column] = pd.to_datetime(df[date_column], unit='D', origin='unix')
    else:
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')

    df = df.dropna(subset=[date_column])
    if df.empty:
        raise ValueError("No valid dates found (strict mode).")

    df = df.sort_values(by=date_column)
    df['date_only'] = df[date_column].dt.date
    unique_dates = sorted(df['date_only'].unique())
    last_10 = unique_dates[-10:] if len(unique_dates) >= 10 else unique_dates

    daily_data = []
    for d in last_10:
        day_df = df[df['date_only'] == d]
        point = {'date': d.strftime('%Y-%m-%d'), 'date_short': d.strftime('%m/%d')}

        for param, col_name in iv_parameters.items():
            col_key = colmap.get(col_name.upper())
            if col_key and col_key in day_df.columns:
                vals = pd.to_numeric(day_df[col_key], errors='coerce').dropna()
                if len(vals) > 0:
                    avg = round(mean(vals), 3)
                    cv = round((stdev(vals) / avg * 100), 3) if len(vals) > 1 and avg != 0 else 0
                    point[f'{param}_avg'] = avg
                    point[f'{param}_cv'] = cv
                else:
                    point[f'{param}_avg'] = 0
                    point[f'{param}_cv'] = 0
            else:
                point[f'{param}_avg'] = 0
                point[f'{param}_cv'] = 0

        daily_data.append(point)

    print(f"✅ Processed {len(daily_data)} days of IV repeatability data")
    return {
        'dates': [p['date'] for p in daily_data],
        'repeatability_data': daily_data,
        'parameters': ['PCE', 'FF', 'Max Power', 'HI', 'I_sc', 'V_oc', 'R_series', 'R_shunt']  # Updated to match charts_api.py
    }


# -------------------- SIMPLE GETTERS --------------------
def get_parameter_data(parameter):
    all_data = extract_chart_data() 
    return all_data.get(parameter, [])

def get_all_parameters():
    return ['PCE', 'FF', 'Max Power', 'HI', 'I_sc', 'V_oc', 'R_series', 'R_shunt']
