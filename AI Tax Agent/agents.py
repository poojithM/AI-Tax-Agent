from crewai import Agent, LLM
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os

#Load environment variables from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Using a FREE model via Ollama to reduce API costs
# This example uses Microsoft's Phi-3 (3.8B) model locally
# Step-by-step:
# 1. Install Ollama from https://ollama.com
# 2. In terminal/CMD, run: ollama pull phi3:3.8b to download the model
# 3. Start the Ollama server: ollama run phi3
# 4. Then connect to it locally as shown below

Free_Model = ChatOpenAI(
    model="phi3:3.8b",                   # Name of the pulled model
    base_url="http://localhost:11434/v1" # Local Ollama API endpoint
)



# Initialize the GPT-4o-mini model(Paid Model)
llm = LLM(
    model="gpt-4o-mini",
    temperature=0.1,   # Lower temperature for more deterministic output
    api_key=api_key
)

#


#Function to create the Tax Calculation Agent dynamically with user inputs

def get_tax_calc_agent(income, filing_status, deductions,tax_withheld,dependents, llm):
    return Agent(
        name="TaxBot",
        role="Tax Calculation Specialist",
        goal="Accurately calculate step by step U.S. federal tax based on {income}, {filing_status}, {tax_withheld},{dependents} and {deductions}.",
        backstory="""
                    You are an expert financial AI assistant specialized in U.S. tax regulations.
                    You can apply standard deductions, use the latest tax brackets, and compute total tax owed or refunded.""",
        llm=llm,
        verbose=True,              # Enables detailed logging
        allow_delegation=False,    # Agent handles only its task
        memory=True                # Maintains memory during task flow
    )


#Static Agent to generate a professional tax report in markdown format
def get_tax_report(income, filing_status, deductions, tax_withheld, dependents, llm):
    return Agent(
        name="ReportBot",
        role="Tax Report Writer",
        goal=(
            f"Understand the tax calculation results based on income: {income}, filing_status: {filing_status}, "
            f"deductions: {deductions}, tax_withheld: {tax_withheld}, and dependents: {dependents}, "
            "and generate clear, structured markdown-based tax reports with detailed step-by-step calculations."
        ),
        backstory=(
            "You are a seasoned AI financial consultant. Your role is to explain tax results in a way that is both accurate and easy to understand. "
            "You write markdown-formatted reports that include income, deductions, taxable income, tax bracket breakdowns, and the final tax owed or refund."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=True,
        memory=True
    )


