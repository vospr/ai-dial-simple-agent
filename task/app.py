import os

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

def main():
    #TODO:
    # 1. Create UserClient
    # 2. Create DialClient with all tools (WebSearchTool, GetUserByIdTool, SearchUsersTool, CreateUserTool, UpdateUserTool, DeleteUserTool)
    # 3. Create Conversation and add there first System message with SYSTEM_PROMPT (you need to write it in task.prompts#SYSTEM_PROMPT)
    # 4. Run infinite loop and in loop and:
    #    - get user input from terminal (`input("> ").strip()`)
    #    - Add User message to Conversation
    #    - Call DialClient with conversation history
    #    - Add Assistant message to Conversation and print its content
    
    # 1. Create UserClient
    user_client = UserClient()
    
    # 2. Create DialClient with all tools
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
    
    # 3. Create Conversation and add first System message
    conversation = Conversation()
    conversation.add_message(Message(role=Role.SYSTEM, content=SYSTEM_PROMPT))
    
    print("\n🎯 User Management Agent")
    print("="*50)
    print("Type 'exit' or 'quit' to end the conversation.")
    print("="*50)
    
    # 4. Run infinite loop
    while True:
        user_input = input("\n> ").strip()
        
        if user_input.lower() in ['exit', 'quit']:
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        # Add User message to Conversation
        conversation.add_message(Message(role=Role.USER, content=user_input))
        
        try:
            # Call DialClient with conversation history
            assistant_response = dial_client.get_completion(conversation.get_messages(), print_request=False)
            
            # Add Assistant message to Conversation and print its content
            conversation.add_message(assistant_response)
            print(f"\n🤖 Assistant: {assistant_response.content}")
        
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()

#TODO:
# Request sample:
# Add Andrej Karpathy as a new user