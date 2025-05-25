import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI
from tools import get_tool_schemas

class LLMHandler:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('MODEL_NAME', 'gpt-4o-2024-08-06')
        self.temperature = float(os.getenv('TEMPERATURE', '0.7'))
        self.max_tokens = int(os.getenv('MAX_TOKENS', '150'))
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)

    def _create_table_context(self, tables: List[Dict]) -> str:
        """Create a context string from available tables"""
        table_info = []
        for table in tables:
            table_info.append(f"- {table['schema']}.{table['name']} ({table['row_count']} rows)")
        return "\n".join(table_info)

    def _create_prompt(self, question: str, tables: List[Dict]) -> str:
        """Create a prompt for the LLM"""
        table_context = self._create_table_context(tables)
        
        return f"""Given the following question about database tables, determine which database operation to perform.
Available tables:
{table_context}

Question: {question}

Please analyze the question and determine which database operation would be most appropriate."""

    def process_question(self, question: str, tables: List[Dict]) -> Dict:
        """Process a question and determine which database operation to perform"""
        try:
            # Create the prompt
            prompt = self._create_prompt(question, tables)
            # print(prompt)
            
            # Get available tools
            tools = get_tool_schemas()
            
            # Call the LLM using function calling
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a database expert that helps determine which database operations to perform based on natural language questions."},
                    {"role": "user", "content": prompt}
                ],
                tools=[{"type": "function", "function": tool} for tool in tools],
                tool_choice="auto",
                temperature=0,
                max_tokens=self.max_tokens
            )
            
            # Extract the function call from the response
            message = response.choices[0].message
            
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                print(tool_call.function.name, tool_call.function.arguments)
                return {
                    "tool_name": tool_call.function.name,
                    "parameters": tool_call.function.arguments
                }
            
            return None
            
        except Exception as e:
            print(f"Error in LLM processing: {str(e)}")
            return None 