import google.generativeai as genai
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from tools import ResearchTools
from account_plan import AccountPlan

load_dotenv()

class CompanyResearchAgent:
    """Conversational AI agent for company research and account planning"""
    
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])
        
        # Initialize tools
        self.tools = ResearchTools()
        
        # Agent state
        self.current_company = None
        self.account_plan = None
        self.research_data = None
        self.conversation_context = []
        
        # System prompt
        self.system_prompt = """You are a professional company research assistant and account plan generator. 

Your capabilities:
- Research companies using multiple data sources
- Synthesize findings into comprehensive account plans
- Provide real-time updates during research
- Ask clarifying questions when needed
- Handle updates to specific sections of account plans

Communication style:
- Professional yet conversational
- Proactive in asking for clarification
- Transparent about research progress and limitations
- Helpful and adaptive to user needs

When researching:
- Always inform the user what you're doing
- If information conflicts or is missing, ask if you should dig deeper
- Synthesize information from multiple sources
- Be honest about data quality and gaps

When generating account plans:
- Create comprehensive, actionable plans
- Structure information clearly across sections
- Base recommendations on researched data
- Be realistic about what you know vs. what you're inferring
"""
    
    def process_message(self, user_message: str) -> str:
        """Process user message and generate response"""
        
        # Add to conversation context
        self.conversation_context.append({
            'role': 'user',
            'content': user_message
        })
        
        # Detect intent
        intent = self._detect_intent(user_message)
        
        # Handle based on intent
        if intent == 'research_company':
            response = self._handle_research_request(user_message)
        elif intent == 'generate_plan':
            response = self._handle_plan_generation()
        elif intent == 'update_section':
            response = self._handle_section_update(user_message)
        elif intent == 'show_plan':
            response = self._show_current_plan()
        else:
            response = self._handle_general_conversation(user_message)
        
        # Add response to context
        self.conversation_context.append({
            'role': 'assistant',
            'content': response
        })
        
        return response
    
    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message"""
        message_lower = message.lower()
        
        # Check for research keywords
        research_keywords = ['research', 'find out about', 'tell me about', 'information on', 'look up']
        if any(keyword in message_lower for keyword in research_keywords):
            return 'research_company'
        
        # Check for plan generation
        plan_keywords = ['generate plan', 'create plan', 'account plan', 'make a plan']
        if any(keyword in message_lower for keyword in plan_keywords):
            return 'generate_plan'
        
        # Check for updates
        update_keywords = ['update', 'change', 'modify', 'edit']
        if any(keyword in message_lower for keyword in update_keywords):
            return 'update_section'
        
        # Check for showing plan
        show_keywords = ['show plan', 'display plan', 'view plan', 'see plan']
        if any(keyword in message_lower for keyword in show_keywords):
            return 'show_plan'
        
        return 'general'
    
    def _handle_research_request(self, message: str) -> str:
        """Handle company research request"""
        
        # Extract company name using Gemini
        extraction_prompt = f"""Extract the company name from this user message: "{message}"
        
Return ONLY the company name, nothing else. If no company name is found, return "UNKNOWN".

Examples:
User: "Research Microsoft" -> Microsoft
User: "Tell me about Apple Inc" -> Apple Inc
User: "Find information on Tesla" -> Tesla
User: "What do you know?" -> UNKNOWN
"""
        
        extraction_response = self.model.generate_content(extraction_prompt)
        company_name = extraction_response.text.strip()
        
        if company_name == "UNKNOWN":
            return "I'd be happy to research a company for you! Which company would you like me to look into?"
        
        # Start research
        self.current_company = company_name
        response = f"🔍 Starting research on **{company_name}**...\n\n"
        
        # Search for website URL
        url_prompt = f"What is the official website URL for {company_name}? Return ONLY the URL (e.g., https://example.com) or 'UNKNOWN' if you don't know."
        url_response = self.model.generate_content(url_prompt)
        website_url = url_response.text.strip()
        
        if website_url.startswith('http'):
            response += f"📍 Found website: {website_url}\n"
        else:
            website_url = None
            response += "ℹ️ No official website URL found.\n"
        
        # Gather information
        response += "\n🔎 Gathering information from multiple sources...\n"
        
        self.research_data = self.tools.search_company_info(company_name, website_url)
        
        # Analyze results
        successful_sources = [s for s in self.research_data['sources'] if s.get('success')]
        failed_sources = [s for s in self.research_data['sources'] if not s.get('success')]
        
        response += f"\n✅ Successfully gathered data from {len(successful_sources)} source(s)\n"
        
        if failed_sources:
            response += f"⚠️ {len(failed_sources)} source(s) had issues\n"
        
        # Show summary of findings
        response += "\n📊 **Research Summary:**\n\n"
        
        for source in successful_sources:
            if source['source'] == 'Wikipedia':
                response += f"**Wikipedia:**\n{source['summary'][:200]}...\n\n"
            elif source['source'] == 'ScrapingDog':
                response += f"**Website Content (scraped):**\nSuccessfully retrieved content from {source['url']}\n\n"
        
        # Check for conflicts or gaps
        if len(successful_sources) < 2:
            response += "⚠️ I found limited information. Would you like me to:\n"
            response += "1. Try additional sources\n"
            response += "2. Generate an account plan with available data\n"
            response += "3. Focus on specific aspects of the company\n"
        else:
            response += "✨ I have enough information to generate a comprehensive account plan.\n"
            response += "Would you like me to proceed with generating the account plan?"
        
        return response
    
    def _handle_plan_generation(self) -> str:
        """Generate account plan from research data"""
        
        if not self.current_company:
            return "I need to research a company first. Please tell me which company you'd like to research."
        
        if not self.research_data:
            return f"I haven't gathered research data for {self.current_company} yet. Let me do that first!"
        
        response = f"📝 Generating account plan for **{self.current_company}**...\n\n"
        
        # Initialize account plan
        self.account_plan = AccountPlan(self.current_company)
        
        # Prepare research summary for Gemini
        research_summary = self._prepare_research_summary()
        
        # Generate each section using Gemini
        for section in AccountPlan.SECTIONS:
            response += f"✍️ Writing: {section.replace('_', ' ').title()}...\n"
            
            section_content = self._generate_section_content(section, research_summary)
            self.account_plan.update_section(section, section_content)
        
        response += "\n✅ **Account plan generated successfully!**\n\n"
        response += self.account_plan.format_for_display()
        
        # Save the plan
        filepath = self.account_plan.save()
        response += f"\n💾 Plan saved to: {filepath}\n"
        response += "\nYou can now:\n"
        response += "- Ask me to update specific sections\n"
        response += "- Request more research on specific areas\n"
        response += "- Export the plan\n"
        
        return response
    
    def _prepare_research_summary(self) -> str:
        """Prepare research data summary for LLM"""
        summary = f"Company: {self.current_company}\n\n"
        summary += "Available Information:\n"
        
        for source in self.research_data['sources']:
            if source.get('success'):
                summary += f"\nSource: {source['source']}\n"
                if 'summary' in source:
                    summary += f"Content: {source['summary']}\n"
                if 'content' in source:
                    summary += f"Content: {source['content'][:500]}\n"
        
        return summary
    
    def _generate_section_content(self, section: str, research_summary: str) -> str:
        """Generate content for a specific account plan section"""
        
        section_prompts = {
            'executive_summary': "Write a concise executive summary (3-4 sentences) highlighting the company's core business, market position, and why they're a strategic account.",
            'company_overview': "Provide a comprehensive company overview including: founding, headquarters, industry, products/services, size, and recent developments.",
            'market_position': "Analyze the company's market position, competitive landscape, market share, and industry trends affecting them.",
            'key_stakeholders': "Identify likely key stakeholders and decision-makers (C-level, department heads). If specific names aren't available, describe typical roles.",
            'business_challenges': "Analyze potential business challenges and opportunities the company might be facing based on their industry and size.",
            'value_proposition': "Craft a compelling value proposition for how your organization could help this company (be professional and realistic).",
            'engagement_strategy': "Outline a strategic engagement approach including recommended touchpoints, timing, and messaging themes.",
            'success_metrics': "Define measurable success metrics for this account (revenue targets, engagement metrics, strategic milestones)."
        }
        
        prompt = f"""Based on the following research data, {section_prompts.get(section, 'generate content for this section')}.

Research Data:
{research_summary}

Requirements:
- Be specific and data-driven where possible
- If information is limited, be honest and use reasonable industry assumptions
- Keep it professional and actionable
- Length: 100-150 words

Generate the content now:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"[Content generation in progress - {section}]"
    
    def _handle_section_update(self, message: str) -> str:
        """Handle request to update a section"""
        
        if not self.account_plan:
            return "I don't have an account plan to update. Would you like me to generate one first?"
        
        # Use Gemini to identify which section and what update
        update_prompt = f"""Analyze this user request for updating an account plan section:
User: "{message}"

Available sections:
{', '.join(AccountPlan.SECTIONS)}

Extract:
1. Section name (must match one from the list)
2. What they want to update/change

Format your response as:
SECTION: [section_name]
UPDATE: [what to update]

If you can't determine the section, respond with:
SECTION: UNKNOWN
UPDATE: [summary of request]
"""
        
        analysis = self.model.generate_content(update_prompt)
        analysis_text = analysis.text
        
        # Parse response
        lines = analysis_text.strip().split('\n')
        section = None
        update_request = None
        
        for line in lines:
            if line.startswith('SECTION:'):
                section = line.replace('SECTION:', '').strip().lower()
            elif line.startswith('UPDATE:'):
                update_request = line.replace('UPDATE:', '').strip()
        
        if section == 'unknown' or section not in AccountPlan.SECTIONS:
            return f"I'm not sure which section you want to update. Please specify one of these sections:\n" + \
                   "\n".join([f"- {s.replace('_', ' ').title()}" for s in AccountPlan.SECTIONS])
        
        # Generate updated content
        current_content = self.account_plan.get_section(section)
        research_summary = self._prepare_research_summary()
        
        update_prompt = f"""Update the following section of an account plan based on the user's request.

Section: {section.replace('_', ' ').title()}
Current Content:
{current_content}

User's Update Request:
{update_request}

Research Data (for reference):
{research_summary}

Generate the UPDATED content (100-150 words):"""
        
        updated_content_response = self.model.generate_content(update_prompt)
        updated_content = updated_content_response.text.strip()
        
        # Update the plan
        self.account_plan.update_section(section, updated_content)
        
        response = f"✅ Updated **{section.replace('_', ' ').title()}** section\n\n"
        response += f"**New Content:**\n{updated_content}\n\n"
        response += "Would you like to:\n"
        response += "- Update another section\n"
        response += "- View the complete updated plan\n"
        response += "- Save the plan"
        
        return response
    
    def _show_current_plan(self) -> str:
        """Display current account plan"""
        if not self.account_plan:
            return "I haven't generated an account plan yet. Would you like me to create one?"
        
        return self.account_plan.format_for_display()
    
    def _handle_general_conversation(self, message: str) -> str:
        """Handle general conversation using Gemini"""
        
        # Build context
        context = self.system_prompt + "\n\nConversation history:\n"
        for msg in self.conversation_context[-6:]:  # Last 3 exchanges
            context += f"{msg['role'].capitalize()}: {msg['content'][:200]}\n"
        
        context += f"\nUser: {message}\n\nRespond as the company research assistant:"
        
        response = self.model.generate_content(context)
        return response.text.strip()
