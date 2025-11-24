from agent import CompanyResearchAgent
from colorama import Fore, Style, init
import sys

# Initialize colorama for colored terminal output
init(autoreset=True)

def print_agent(message: str):
    """Print agent message with formatting"""
    print(f"\n{Fore.CYAN}🤖 Agent:{Style.RESET_ALL} {message}\n")

def print_user(message: str):
    """Print user message with formatting"""
    print(f"{Fore.GREEN}👤 You:{Style.RESET_ALL} {message}")

def print_system(message: str):
    """Print system message"""
    print(f"{Fore.YELLOW}ℹ️  {message}{Style.RESET_ALL}")

def main():
    """Main application loop"""
    
    print(f"\n{Fore.MAGENTA}{'='*60}")
    print("🏢 COMPANY RESEARCH ASSISTANT")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    print_system("Initializing agent...")
    
    try:
        agent = CompanyResearchAgent()
        print_system("✅ Agent ready!")
        
        print_agent("Hello! I'm your Company Research Assistant. I can help you:")
        print("   • Research companies from multiple sources")
        print("   • Generate comprehensive account plans")
        print("   • Update specific sections of plans")
        print("   • Answer questions about companies\n")
        print_agent("What company would you like to research today?")
        
        # Main conversation loop
        while True:
            try:
                # Get user input
                user_input = input(f"\n{Fore.GREEN}👤 You: {Style.RESET_ALL}").strip()
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                    print_agent("Thank you for using the Company Research Assistant. Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Process message
                print_system("Processing...")
                response = agent.process_message(user_input)
                
                # Display response
                print_agent(response)
                
            except KeyboardInterrupt:
                print("\n")
                print_system("Interrupted by user")
                break
            except Exception as e:
                print(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
                print_system("Please try again")
    
    except Exception as e:
        print(f"\n{Fore.RED}❌ Fatal error during initialization: {str(e)}{Style.RESET_ALL}")
        print_system("Please check your API keys in .env file")
        sys.exit(1)

if __name__ == "__main__":
    main()
