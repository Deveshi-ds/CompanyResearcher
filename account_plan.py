import json
import os
from datetime import datetime
from typing import Dict, Optional

class AccountPlan:
    """Manages account plan generation and updates"""
    
    SECTIONS = [
        'executive_summary',
        'company_overview',
        'market_position',
        'key_stakeholders',
        'business_challenges',
        'value_proposition',
        'engagement_strategy',
        'success_metrics'
    ]
    
    def __init__(self, company_name: str):
        self.company_name = company_name
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.sections = {section: "" for section in self.SECTIONS}
    
    def update_section(self, section_name: str, content: str) -> bool:
        """Update a specific section of the account plan"""
        if section_name in self.SECTIONS:
            self.sections[section_name] = content
            self.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def get_section(self, section_name: str) -> Optional[str]:
        """Get content of a specific section"""
        return self.sections.get(section_name)
    
    def to_dict(self) -> Dict:
        """Convert account plan to dictionary"""
        return {
            'company_name': self.company_name,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'sections': self.sections
        }
    
    def save(self, directory: str = 'data/account_plans'):
        """Save account plan to JSON file"""
        os.makedirs(directory, exist_ok=True)
        filename = f"{self.company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        return filepath
    
    def format_for_display(self) -> str:
        """Format account plan for display"""
        output = f"\n{'='*60}\n"
        output += f"ACCOUNT PLAN: {self.company_name}\n"
        output += f"{'='*60}\n\n"
        
        section_titles = {
            'executive_summary': 'Executive Summary',
            'company_overview': 'Company Overview',
            'market_position': 'Market Position',
            'key_stakeholders': 'Key Stakeholders',
            'business_challenges': 'Business Challenges & Opportunities',
            'value_proposition': 'Our Value Proposition',
            'engagement_strategy': 'Engagement Strategy',
            'success_metrics': 'Success Metrics'
        }
        
        for section, content in self.sections.items():
            if content:
                output += f"## {section_titles.get(section, section.upper())}\n"
                output += f"{content}\n\n"
        
        output += f"{'='*60}\n"
        return output
