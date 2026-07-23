"""Storage module for evidence sets."""
import json
from pathlib import Path
from typing import Optional, List
from .schemas import EvidenceSet
from .config import EVIDENCE_STORE


def save_evidence_set(evidence_set: EvidenceSet) -> str:
    """
    Save evidence set to storage.
    
    Args:
        evidence_set: EvidenceSet to save
        
    Returns:
        Path where saved
    """
    EVIDENCE_STORE.mkdir(parents=True, exist_ok=True)
    file_path = EVIDENCE_STORE / f"{evidence_set.request_id}.json"
    
    with open(file_path, 'w') as f:
        f.write(evidence_set.model_dump_json(indent=2))
    
    return str(file_path)


def load_evidence_set(request_id: str) -> Optional[EvidenceSet]:
    """
    Load evidence set from storage.
    
    Args:
        request_id: Request ID to load
        
    Returns:
        EvidenceSet or None if not found
    """
    file_path = EVIDENCE_STORE / f"{request_id}.json"
    
    if not file_path.exists():
        return None
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    return EvidenceSet(**data)


def list_evidence_sets() -> List[str]:
    """
    List all saved evidence set IDs.
    
    Returns:
        List of request IDs
    """
    if not EVIDENCE_STORE.exists():
        return []
    
    return [f.stem for f in EVIDENCE_STORE.glob("*.json")]


def latest_evidence_set() -> Optional[EvidenceSet]:
    """
    Get most recent evidence set.
    
    Returns:
        Most recent EvidenceSet or None
    """
    sets = list_evidence_sets()
    if not sets:
        return None
    
    # Sort by modification time, get latest
    all_files = sorted(
        EVIDENCE_STORE.glob("*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if all_files:
        return load_evidence_set(all_files[0].stem)
    
    return None
