"""
Template Engine for dynamic Bangla response generation
Supports variable substitution and conditional logic
"""
from typing import Dict, Any, Optional
import re
from sqlalchemy.orm import Session

from app.db.models import Template


class TemplateEngine:
    def __init__(self):
        self.cache: Dict[str, str] = {}
        
    def render(
        self,
        template_key: str,
        variables: Dict[str, Any],
        db: Optional[Session] = None,
        fallback: Optional[str] = None
    ) -> str:
        """
        Render a template with variables
        
        Args:
            template_key: Template key to look up
            variables: Dict of variables to substitute
            db: Database session (optional, uses cache if not provided)
            fallback: Fallback text if template not found
            
        Returns:
            Rendered text in Bangla
        """
        # Get template
        template_body = self._get_template(template_key, db)
        
        if not template_body:
            if fallback:
                return fallback
            return f"Template '{template_key}' not found"
        
        # Render template
        return self._substitute_variables(template_body, variables)
    
    def _get_template(self, key: str, db: Optional[Session]) -> Optional[str]:
        """Get template from cache or database"""
        # Check cache first
        if key in self.cache:
            return self.cache[key]
        
        # Query database
        if db:
            template = db.query(Template).filter(Template.key == key).first()
            if template:
                self.cache[key] = template.body
                return template.body
        
        return None
    
    def _substitute_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Substitute variables in template
        Supports {variable} and {variable|default} syntax
        """
        def replace_var(match):
            var_expr = match.group(1)
            
            # Check for default value syntax: {var|default}
            if '|' in var_expr:
                var_name, default = var_expr.split('|', 1)
                var_name = var_name.strip()
                default = default.strip()
            else:
                var_name = var_expr.strip()
                default = ''
            
            # Get value
            value = variables.get(var_name, default)
            return str(value)
        
        # Replace all {variable} patterns
        result = re.sub(r'\{([^}]+)\}', replace_var, template)
        
        return result
    
    def clear_cache(self):
        """Clear template cache"""
        self.cache.clear()
    
    def preload_templates(self, db: Session):
        """Preload all templates into cache"""
        templates = db.query(Template).all()
        for template in templates:
            self.cache[template.key] = template.body


# Singleton instance
template_engine = TemplateEngine()


# Common Bangla templates
DEFAULT_TEMPLATES = {
    "greeting": "Assalamu alaikum! Ami {bot_name}. Apnake ki bhabe shahajjo korte pari?",
    "order_status": "Apnar order #{order_id} er status: {status}. Expected delivery: {delivery_date}",
    "order_in_transit": "Apnar order #{order_id} ekhon courier er kase ache. {courier_name} deliver korbe.",
    "order_delivered": "Apnar order #{order_id} already deliver hoyeche {delivery_date} e.",
    "return_initiated": "Apnar return request #{return_id} accept kora hoyeche. {refund_days} diner moddhe refund paben.",
    "product_available": "{product_name} ekhon stock e ache. Price: ৳{price}",
    "product_unavailable": "{product_name} ekhon stock e nai. {restock_date} e asbe.",
    "handoff_agent": "Ami apnake amader agent er sathe connect korchi. Ektu oppokha korun please.",
    "thank_you": "Dhonnobad! Aro kono shahajjo lagbe?",
    "goodbye": "Dhonnobad apnar somoy dewar jonno. Bhalo thakben!"
}

