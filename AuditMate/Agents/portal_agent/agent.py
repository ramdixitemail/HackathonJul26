"""Portal Agent for capturing compliance screenshots."""
from pathlib import Path
from typing import List, Optional
from ..common import SourceType, EvidenceItem, Provenance, PORTAL_TEST_DIR


class PortalAgent:
    """Agent for capturing portal screenshots."""
    
    def __init__(self):
        """Initialize portal agent."""
        self.portal_dir = Path(PORTAL_TEST_DIR)
    
    def capture(self, application_id: str) -> Optional[str]:
        """
        Capture portal screenshot for application.
        
        Args:
            application_id: Application ID (e.g., APP-001)
            
        Returns:
            Path to screenshot or None
        """
        # Check for HTML file
        html_file = self.portal_dir / f"{application_id}.html"
        if html_file.exists():
            # In real implementation, would use Playwright to render
            # For mock, just return path
            return str(html_file)
        
        return None
    
    def collect(self, application_id: str, start_id: int = 1) -> List[EvidenceItem]:
        """
        Collect portal evidence.
        
        Args:
            application_id: Application ID
            start_id: Starting ID for evidence items
            
        Returns:
            List of EvidenceItem objects
        """
        items = []
        
        screenshot_path = self.capture(application_id)
        if screenshot_path:
            items.append(EvidenceItem(
                id=f"EV-{start_id:04d}",
                type=SourceType.SCREENSHOT,
                summary=f"Portal compliance screenshot for {application_id}",
                image=screenshot_path,
                audit_points=[application_id, "portal_compliance"],
                provenance=Provenance(
                    system="portal",
                    method="screenshot",
                    ref=application_id,
                    extra={"captured": "mock"}
                )
            ))
        else:
            items.append(EvidenceItem(
                id=f"EV-{start_id:04d}",
                type=SourceType.SCREENSHOT,
                summary=f"Portal not found for {application_id}",
                content="[Portal screenshot not available in test environment]",
                audit_points=[application_id],
                provenance=Provenance(
                    system="portal",
                    method="not_found",
                    ref=application_id
                )
            ))
        
        return items


if __name__ == "__main__":
    agent = PortalAgent()
    items = agent.collect("APP-001")
    for item in items:
        print(f"{item.id}: {item.type} - {item.summary}")
