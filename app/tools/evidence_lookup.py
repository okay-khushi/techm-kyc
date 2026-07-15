import threading
from typing import Any, Dict, List, Optional

import pandas as pd

from app.utils.constants import CSV_CHUNK_SIZE, KNOWLEDGE_DIR, MAX_SANCTIONS_ROWS, MAX_SCAN_CHUNKS

OFAC_SDN_CSV = KNOWLEDGE_DIR / "sanctions" / "ofac_sdn.csv"
OPENSANCTIONS_CSV = KNOWLEDGE_DIR / "sanctions" / "opensanctions_targets.csv"
CLIENT_ACCOUNT_CSV = KNOWLEDGE_DIR / "kyc" / "client_account_mapping.csv"
CLIENTS_FATF_OFAC_CSV = KNOWLEDGE_DIR / "kyc" / "clients_with_fatf_ofac.csv"
TRANSACTIONS_FATF_OFAC_CSV = KNOWLEDGE_DIR / "kyc" / "transactions_with_fatf_ofac.csv"
SAML_D_CSV = KNOWLEDGE_DIR / "aml" / "SAML-D.csv"

OFAC_SDN_COLUMNS = [
    "ent_num", "name", "sdn_type", "program", "title", "call_sign",
    "vessel_type", "tonnage", "grt", "vessel_flag", "vessel_owner", "remarks",
]


class _DatasetCache:
    """
    Lazily loads and caches the (mostly small) KYC/sanctions reference
    datasets. The two very large files (opensanctions_targets.csv,
    SAML-D.csv) are capped/chunked rather than loaded in full.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._cache: Dict[str, pd.DataFrame] = {}

    def _get(self, key: str, loader) -> pd.DataFrame:
        with self._lock:
            if key not in self._cache:
                self._cache[key] = loader()

            return self._cache[key]

    def ofac_sdn(self) -> pd.DataFrame:
        def load():
            if not OFAC_SDN_CSV.exists():
                return pd.DataFrame(columns=OFAC_SDN_COLUMNS)

            return pd.read_csv(OFAC_SDN_CSV, header=None, names=OFAC_SDN_COLUMNS)

        return self._get("ofac_sdn", load)

    def opensanctions(self) -> pd.DataFrame:
        def load():
            if not OPENSANCTIONS_CSV.exists():
                return pd.DataFrame()

            return pd.read_csv(
                OPENSANCTIONS_CSV,
                usecols=["id", "schema", "name", "aliases", "countries", "sanctions"],
                nrows=MAX_SANCTIONS_ROWS,
                dtype=str,
            )

        return self._get("opensanctions", load)

    def client_account_mapping(self) -> pd.DataFrame:
        def load():
            if not CLIENT_ACCOUNT_CSV.exists():
                return pd.DataFrame()

            return pd.read_csv(CLIENT_ACCOUNT_CSV)

        return self._get("client_account_mapping", load)

    def clients_with_fatf_ofac(self) -> pd.DataFrame:
        def load():
            if not CLIENTS_FATF_OFAC_CSV.exists():
                return pd.DataFrame()

            return pd.read_csv(CLIENTS_FATF_OFAC_CSV)

        return self._get("clients_with_fatf_ofac", load)

    def transactions_with_fatf_ofac(self) -> pd.DataFrame:
        def load():
            if not TRANSACTIONS_FATF_OFAC_CSV.exists():
                return pd.DataFrame()

            return pd.read_csv(TRANSACTIONS_FATF_OFAC_CSV)

        return self._get("transactions_with_fatf_ofac", load)


_datasets = _DatasetCache()


class EvidenceLookupTool:
    """
    Cross-references entity names / client identifiers against the
    sanctions and KYC/FATF/OFAC knowledge base.
    """

    def search_sanctions(self, name: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not name:
            return []

        needle = name.lower()
        hits: List[Dict[str, Any]] = []

        sdn = _datasets.ofac_sdn()

        if not sdn.empty:
            matches = sdn[sdn["name"].str.lower().str.contains(needle, na=False)]

            for _, row in matches.head(limit).iterrows():
                hits.append({
                    "source": "ofac_sdn",
                    "name": row["name"],
                    "program": row["program"],
                    "remarks": row["remarks"],
                })

        opensanctions = _datasets.opensanctions()

        if not opensanctions.empty:
            name_match = opensanctions["name"].str.lower().str.contains(needle, na=False)
            alias_match = opensanctions["aliases"].fillna("").str.lower().str.contains(needle, na=False)
            matches = opensanctions[name_match | alias_match]

            for _, row in matches.head(limit).iterrows():
                hits.append({
                    "source": "opensanctions",
                    "name": row["name"],
                    "schema": row["schema"],
                    "countries": row["countries"],
                    "sanctions": row["sanctions"],
                })

        return hits[:limit]

    def search_kyc(
        self,
        client_id: Optional[str] = None,
        name: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:

        hits: List[Dict[str, Any]] = []

        mapping = _datasets.client_account_mapping()
        clients = _datasets.clients_with_fatf_ofac()

        for df, source in ((mapping, "client_account_mapping"), (clients, "clients_with_fatf_ofac")):
            if df.empty:
                continue

            frame = df

            if client_id is not None and "client_id" in frame.columns:
                frame = frame[frame["client_id"].astype(str) == str(client_id)]
            elif name and "client_name" in frame.columns:
                frame = frame[frame["client_name"].str.lower().str.contains(name.lower(), na=False)]

            for _, row in frame.head(limit).iterrows():
                hits.append({"source": source, **row.to_dict()})

        return hits[:limit]

    def list_clients(self, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Distinct client_id/client_name pairs from the KYC reference
        data, for UI pickers (e.g. the dashboard's client dropdown)
        rather than free-typed client ids.
        """

        clients = _datasets.clients_with_fatf_ofac()

        if clients.empty or "client_id" not in clients.columns:
            return []

        columns = [c for c in ("client_id", "client_name", "country", "sector") if c in clients.columns]

        deduped = clients[columns].drop_duplicates(subset="client_id").sort_values("client_id")

        return deduped.head(limit).to_dict(orient="records")

    def search_transactions(
        self,
        client_id: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:

        transactions = _datasets.transactions_with_fatf_ofac()

        if transactions.empty or client_id is None:
            return []

        matches = transactions[transactions["client_id"].astype(str) == str(client_id)]

        return matches.head(limit).to_dict(orient="records")

    def search_aml_patterns(self, account: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Best-effort chunked scan of the (~1GB) SAML-D transaction ledger
        for a given sender/receiver account, bounded by MAX_SCAN_CHUNKS
        so a single lookup cannot stall the pipeline.
        """

        if not account or not SAML_D_CSV.exists():
            return []

        hits: List[Dict[str, Any]] = []

        for i, chunk in enumerate(pd.read_csv(SAML_D_CSV, chunksize=CSV_CHUNK_SIZE)):
            matches = chunk[
                (chunk["Sender_account"].astype(str) == str(account))
                | (chunk["Receiver_account"].astype(str) == str(account))
            ]

            hits.extend(matches.to_dict(orient="records"))

            if len(hits) >= limit or i + 1 >= MAX_SCAN_CHUNKS:
                break

        return hits[:limit]

    def run(self, entities: List[str], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        metadata = metadata or {}

        results = {
            "sanctions_matches": [],
            "kyc_matches": [],
            "transaction_matches": [],
        }

        for entity in entities:
            results["sanctions_matches"].extend(self.search_sanctions(entity))

        client_id = metadata.get("client_id")

        if client_id is not None:
            results["kyc_matches"].extend(self.search_kyc(client_id=client_id))
            results["transaction_matches"].extend(self.search_transactions(client_id=client_id))
        else:
            for entity in entities:
                results["kyc_matches"].extend(self.search_kyc(name=entity))

        return results


evidence_lookup_tool = EvidenceLookupTool()
