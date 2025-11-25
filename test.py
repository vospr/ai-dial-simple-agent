import os
import sys
from pathlib import Path

# Add task directory to path
sys.path.insert(0, str(Path(__file__).parent))

from task.client import DialClient
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role
from task.prompts import SYSTEM_PROMPT
from task.tools.users.create_user_tool import CreateUserTool
from task.tools.users.delete_user_tool import DeleteUserTool
from task.tools.users.get_user_by_id_tool import GetUserByIdTool
from task.tools.users.search_users_tool import SearchUsersTool
from task.tools.users.update_user_tool import UpdateUserTool
from task.tools.users.user_client import UserClient
from task.tools.web_search import WebSearchTool

DIAL_ENDPOINT = "https://ai-proxy.lab.epam.com"
API_KEY = os.getenv('DIAL_API_KEY', 'dial-fxbasxs2h6t7brhnbqs36omhe2y')


def print_separator(title: str = ""):
    print(f"\n{'='*100}")
    if title:
        print(f"  {title}")
        print(f"{'='*100}")


def run_test_case(dial_client: DialClient, conversation: Conversation, test_name: str, user_query: str):
    print_separator(f"TEST: {test_name}")
    print(f"User Query: {user_query}")
    
    # Add User message
    conversation.add_message(Message(role=Role.USER, content=user_query))
    
    try:
        # Get assistant response
        assistant_response = dial_client.get_completion(conversation.get_messages(), print_request=False)
        
        # Add Assistant message
        conversation.add_message(assistant_response)
        
        print(f"\n✅ Assistant Response:\n{assistant_response.content}")
        print(f"\n{'='*100}")
        
        return True
    except Exception as e:
        print(f"\n❌ Test Failed: {str(e)}")
        print(f"\n{'='*100}")
        return False


def main():
    print_separator("🎯 AI DIAL SIMPLE AGENT - COMPREHENSIVE TEST SUITE")
    
    # Initialize UserClient
    print("\n🔧 Initializing User Client...")
    user_client = UserClient()
    print("✅ User Client initialized")
    
    # Initialize DialClient with all tools
    print("\n🔧 Initializing DIAL Client with tools...")
    dial_client = DialClient(
        endpoint=DIAL_ENDPOINT,
        deployment_name="gpt-4o",
        api_key=API_KEY,
        tools=[
            WebSearchTool(api_key=API_KEY, endpoint=DIAL_ENDPOINT),
            GetUserByIdTool(user_client),
            SearchUsersTool(user_client),
            CreateUserTool(user_client),
            UpdateUserTool(user_client),
            DeleteUserTool(user_client)
        ]
    )
    
    # Create Conversation with System message
    conversation = Conversation()
    conversation.add_message(Message(role=Role.SYSTEM, content=SYSTEM_PROMPT))
    print("✅ DIAL Client initialized with all tools")
    
    print_separator("Starting Automated Tests")
    
    test_results = []
    
    # Test 1: Web Search Tool
    test_results.append(run_test_case(
        dial_client, conversation,
        "Web Search - Who is Andrej Karpathy?",
        "Who is Andrej Karpathy? Please search the web for information about him."
    ))
    
    # Test 2: Search Users Tool
    test_results.append(run_test_case(
        dial_client, conversation,
        "Search Users by Name",
        "Search for users with the name John"
    ))
    
    # Test 3: Add New User (Andrej Karpathy)
    test_results.append(run_test_case(
        dial_client, conversation,
        "Create User - Add Andrej Karpathy",
        "Add Andrej Karpathy as a new user. Use web search to find information about him. "
        "His email should be andrej.karpathy@example.com, and include relevant details from your search in the about_me field."
    ))
    
    # Test 4: Search for the newly created user
    test_results.append(run_test_case(
        dial_client, conversation,
        "Search for Andrej Karpathy",
        "Search for users with the surname Karpathy"
    ))
    
    # Test 5: Get User by ID (assuming user with ID 1 exists)
    test_results.append(run_test_case(
        dial_client, conversation,
        "Get User by ID",
        "Get the user information for user ID 1"
    ))
    
    # Test 6: Update User
    test_results.append(run_test_case(
        dial_client, conversation,
        "Update User Information",
        "Update user ID 1's company to 'EPAM Systems'"
    ))
    
    # Test 7: Search by Gender
    test_results.append(run_test_case(
        dial_client, conversation,
        "Search Users by Gender",
        "Find all male users in the system"
    ))
    
    # Test 8: Complex Query - Search and Enrich
    test_results.append(run_test_case(
        dial_client, conversation,
        "Complex Query - User Profile Enhancement",
        "Search for users with surname 'Adams' and provide additional context about any notable person with that name using web search"
    ))
    
    # Print Summary
    print_separator("📊 TEST SUMMARY")
    total_tests = len(test_results)
    passed_tests = sum(test_results)
    failed_tests = total_tests - passed_tests
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print_separator()
    print("🎉 All automated tests completed!")
    print_separator()
    
    # Note about delete test
    print("\n⚠️  Note: User deletion test is not included in automated tests")
    print("   to avoid modifying the database. To test deletion manually:")
    print("   Run: python task/app.py")
    print("   Then: Delete user with ID <user_id>")
    print()


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    main()

