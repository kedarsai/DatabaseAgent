import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI

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
        
        return f"""Given the following question about database tables, identify which table is being referred to.
Available tables:
{table_context}

Question: {question}

Please respond with ONLY the table name that best matches the question. If no table matches, respond with 'None'.
Do not include any explanations or additional text."""

    def identify_table(self, question: str, tables: List[Dict]) -> Optional[str]:
        """Identify which table is being referred to in the question"""
        try:
            # Create the prompt
            prompt = self._create_prompt(question, tables)
            # print(prompt)
            # Call the LLM using the new API format
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a database expert that helps identify tables from natural language questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract the table name from the response
            table_name = response.choices[0].message.content.strip()
            
            # Validate the response
            if table_name.lower() == 'none':
                return None
                
            # Check if the table exists in our list
            table_names = [f"{t['schema']}.{t['name']}" for t in tables]
            if table_name in table_names:
                return table_name
                
            return None
            
        except Exception as e:
            print(f"Error in LLM processing: {str(e)}")
            return None 