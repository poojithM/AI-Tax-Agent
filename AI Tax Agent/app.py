from flask import Flask, render_template, request, flash, send_file
from agents import get_tax_calc_agent, get_tax_report, llm
from task import tax_calc_task, tax_report_task
from crewai import Crew, Process
import os
import shutil
import json

#Initialize Flask App
app = Flask(__name__)

#Ensure to save tex_report markdown file
REPORTS_DIR = "reports"
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

#Define  the main route for GET and POST
@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    report_filename = None #placeholder for potential report download

    if request.method == 'POST':
        #Get user input from the HTML form
        income = request.form['income']
        filing_status = request.form['filing_status']
        deduction_type = request.form['deductions']
        tax_withheld = request.form['tax_withheld']
        dependents = request.form['dependents']


        # Validate inputs
        if not income or not tax_withheld or not filing_status or not deduction_type:
            flash("Please fill all fields", "error")
            return render_template('index.html')

        try:
            income = round(float(income), 2)
            tax_withheld = round(float(tax_withheld), 2)
            dependents = int(dependents)

        except ValueError:
            flash("⚠️ Invalid number format", "error")
            return render_template('index.html')

        if deduction_type != "standard":
            flash("⚠️ Only standard deductions are supported", "error")
            return render_template('index.html')
        
        

        #Initialize agents and tasks for tax calculaton and reporting
        agent1 = get_tax_calc_agent(income, filing_status, deduction_type, tax_withheld,dependents, llm)
        agent2 = get_tax_report(income, filing_status, deduction_type, tax_withheld,dependents, llm)
        task1 = tax_calc_task(agent1, income, filing_status, deduction_type, tax_withheld, dependents)

        task2 = tax_report_task(agent2, income, filing_status, deduction_type, tax_withheld,dependents)

        #Run the CrewAI workflow
        crew = Crew(
            agents=[agent1, agent2],
            tasks=[task1, task2],
            process=Process.sequential, #Run task one after another
            return_intermediate_steps=True,
            verbose=True
        )

        #Executing crew
        crew_result = crew.kickoff()

        #Parse the output from agent1 to extract the message
        try:
            agent1_raw = crew_result.tasks_output[0].raw
            agent1_output = json.loads(agent1_raw)

            result = agent1_output.get("message", " No message found.")
            full_calculation = agent1_output.get("calculations", " No detailed calculation provided.")

        except Exception as e:
            result = f" Error parsing output: {str(e)}"
            full_calculation = None


        # Move existing tax_report.md from root to static/
        source_path = os.path.join(os.getcwd(), "tax_report.md")
        report_filename = "tax_report.md"
        destination_path = os.path.join("static", report_filename)

        if os.path.exists(source_path):
            with open(source_path, 'r') as src, open(destination_path, 'w') as dst:
                dst.write(src.read())
        else:
            report_filename = None  # Prevent error if file not found


    return render_template('index.html', result=result, report_filename=report_filename)

@app.route('/download/<filename>')
def download_report(filename):
    filepath = os.path.join("static", filename)
    return send_file(filepath, as_attachment=True)


import markdown  # Make sure this is imported at the top

@app.route('/report')
def view_report():
    try:
        with open('static/tax_report.md', 'r') as file:
            content_md = file.read()
            content_html = markdown.markdown(content_md)  # convert MD to HTML
    except FileNotFoundError:
        content_html = "<p><strong>Report not found.</strong></p>"

    return render_template('report.html', report_content=content_html)



if __name__ == '__main__':
    app.run(debug=True)