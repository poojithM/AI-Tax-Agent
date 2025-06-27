from crewai import Task

from pydantic import BaseModel, Field

#Schema for parsing the result from Agent1 (Tax Bot)
class TaxResult(BaseModel):
    message: str = Field(..., description="The final tax result message.")
    calculations: str = Field(..., description="Step-by-step full calculation details with user inputs.")

#Task1: Tax Calculation
def tax_calc_task(agent, income, filing_status, deduction_type, tax_withheld,dependents):

    # Prompt provides detailed tax calculation instructions
    # Includes:
    # - Standard deduction based on filing status
    # - Calculation of taxable income
    # - Application of 2025 federal tax brackets
    # - Final tax amount after subtracting tax withheld
    # - Returns JSON object with 'message' (owed, refund, or zero)

  prompt = f"""
            
        You are a U.S. tax assistant trained in 2025 federal tax rules. Your task is to calculate the federal income tax owed or refund due based on the provided details and return the result as a JSON object with a 'message' field containing a user-friendly message.

        User Details:
        - Income: ${income}
        - Filing Status: {filing_status}
        - Deduction Type: {deduction_type}
        - Tax Withheld: ${tax_withheld}
        - Number of Dependents: {dependents}


        Instructions:

        1. Apply Standard Deduction:
        - Based on the filing status, use the following standard deductions:
            - Single: $15,000
            - Married Filing Jointly: $30,000
            - Married Filing Separately: $15,000
            - Head of Household: $22,500

        2. Calculate Taxable Income:
        - Subtract the standard deduction from the income to get taxable income.
        - If the result is negative, set taxable income to $0.

        3. Apply 2023 U.S. Federal Tax Brackets:
        - Use the tax brackets corresponding to the filing status:
            - Single:
            - 10% on $0 to $11,925
            - 12% on $11,926 to $48,475
            - 22% on $48,476 to $103,350
            - 24% on $103,351 to $197,300
            - 32% on $197,301 to $250,525
            - Married Filing Jointly:
            - 10% on $0 to $23,850
            - 12% on $23,851 to $96,950
            - 22% on $96,951 to $206,700
            - 24% on $206,701 to $394,600
            - 32% on $394,601 to $501,050
            - Married Filing Separately:
            - 10% on $0 to $11,925
            - 12% on $11,926 to $48,475
            - 22% on $48,476 to $103,350
            - 24% on $103,351 to $197,300
            - 32% on $197,301 to $250,525
            - Head of Household:
            - 10% on $0 to $17,000
            - 12% on $17,001 to $64,850
            - 22% on $64,851 to $103,350
            - 24% on $103,351 to $197,300
            - 32% on $197,301 to $250,500

        - Calculate the tax liability for each applicable bracket:
            - Determine the portion of taxable income in each bracket.
            - Multiply that portion by the bracket's tax rate.
            - Sum the tax amounts from all applicable brackets.

        4. Apply Dependent Credits:
            - Multiply the number of dependents by $2,000 to calculate total credit.
            - Subtract this credit from the tax liability.
            - If the result is negative, set tax liability to $0.
        

        5. Calculate Final Tax Owed or Refund:
        - Subtract the tax withheld from the tax adjusted liability to get the final amount(after credits).
        - If the result is positive, the user owes that amount.
        - If the result is negative, the user is entitled to a refund of the absolute value.
        - If the result is zero, the user owes nothing and receives no refund.


        Example Calculation:
          Input: Income = $50000, Filing Status = single, Deduction Type = standard, Tax Withheld = $3000, Dependents = 1

          Step 1: Standard deduction = $15,000

          Step 2: Taxable income = $50,000 - $15,000 = $35,000

          Step 3: Tax liability calculation:

          10% on $11,925 = $1,192.50  
          12% on ($35,000 - $11,925) = $23,075 × 0.12 = $2,769.00  

          Total tax liability = $1,192.50 + $2,769.00 = **$3,961.50**

          Step 4: Dependent credit = 1 × $2,000 = **$2,000**

          Adjusted tax liability = $3,961.50 - $2,000 = **$1,961.50**

          Step 5: Final amount = Tax Withheld - Adjusted Tax =  
          $3,000 - $1,961.50 = **$1,038.50**

          Output:  
          {{ "message": "Congratulations! You are entitled to a refund of $1,038.50." }}

          5. Return a JSON Output:
        - Format the output as a JSON object with a single 'message' field:
            - If final amount is positive: "You owe $amount in federal income tax."
            - If final amount is negative: "Congratulations! You are entitled to a refund of $amount."
            - If final amount is zero: "You owe no federal income tax and will receive no refund."
            - Format the amount to two decimal places.
        - Example JSON output: {{ "Calculations": "your step by step calculations  of Tax", "message": "You owe 'Final amount' in federal income tax." }}


        NOTE: Calculate the income, filing status, deduction_type, tax withheld.calculate step by step then provide the output as expected output. Do not hallucinate.

        
"""




  return Task(
          description=prompt,
          expected_output="A JSON object with a 'message' field containing the tax result",
          agent=agent,
          output_pydantic = TaxResult
      )


#Task2 : Tax report Generator Task
def tax_report_task(agent2, income, filing_status, deduction_type, tax_withheld, dependents):
    
    # This prompt generates a clear, human-readable tax report in markdown format
    # The report includes:
    # - Income and deduction details
    # - Bracket-wise tax breakdown
    # - Explanation of how tax was calculated
    # - Final summary (e.g., refund or owed amount)

    prompt = f"""
    You are a tax report generator.

    Use the result provided by the tax calculation agent to create a professional, step-by-step tax summary in markdown format.

    Your report should include the following:

    ### Tax Report

    - *Income*: ${income}
    - *Filing Status*: {filing_status}
    - *Deduction Type*: {deduction_type}
    - *Deduction Applied*: Based on standard deduction for selected status.
    - *Tax Withheld*: ${tax_withheld}
    - *Dependents*: {dependents}
    - *Taxable Income*: Explain how the deduction was subtracted from income.

    ### Tax Bracket Breakdown

    For each bracket used:
    - Mention how much income falls into that bracket.
    - Show the percentage and the exact tax calculated for that portion.

    ### Total Tax Calculation

    - Sum the tax from each bracket.
    - Mention if any credits (e.g., dependents) were applied.
    - Clearly explain how the total tax amount was arrived at.

    ### Final Summary

    At the end of the report, provide a friendly, conclusive statement:
    - If the user owes money:  
      *"You owe $X in taxes."*
    - If the user is due a refund:  
      *"Congratulations! You will receive a refund of $Y."*

    ### Helpful Suggestions

    Include 2–3 actionable suggestions on how the user could:
    - Maximize their refund next year
    - Lower their taxable income
    - Better plan for withholdings

    Example tips include: contributing to a retirement plan (like IRA or 401(k)), tracking medical and charitable expenses for itemized deductions, or adjusting W-4 withholdings.

    Use markdown formatting throughout to keep the report structured, informative, and easy to read.
    """
    return Task(
        description=prompt,
        expected_output="A detailed markdown report with step-by-step explanation of the tax calculation and helpful financial tips.",
        agent=agent2,
        output_file="tax_report.md" #This will generate the markdown report in the project folder
    )
