from bs4 import BeautifulSoup

def parse_indeed_email(html_content):
    """
    Parses the HTML content of an Indeed Job Alert email to extract job details.

    Args:
        html_content (str): HTML content of the email.

    Returns:
        list of dict: A list containing job details with keys 'title', 'company', 'location', 'salary', and 'url'.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    jobs = []

    # Find all <a> tags with href containing 'rc/clk/dl'
    job_entries = soup.find_all('a', href=lambda href: href and 'rc/clk/dl' in href)

    for entry in job_entries:
        # Initialize default values
        job_title = "N/A"
        job_url = "N/A"
        company_name = "N/A"
        location = "N/A"
        salary = "N/A"

        # Extract Job Title and URL
        h2_tag = entry.find('h2')
        if h2_tag:
            inner_a_tag = h2_tag.find('a')
            if inner_a_tag:
                job_title = inner_a_tag.get_text(strip=True)
                job_url = inner_a_tag['href']

        # Extract Company Name
        # Assuming the company name is in the first <td> after the title
        company_td = entry.find_next('td', style=lambda value: value and 'font-size:14px;line-height:21px' in value)
        if company_td:
            company_name = company_td.get_text(strip=True)

        # Extract Location
        # Assuming the location is in the next <td> after the company name
        location_td = company_td.find_next('td', style=lambda value: value and 'font-size:14px;line-height:21px' in value) if company_td else None
        if location_td:
            # Clean up special characters like &bull; or &nbsp;
            location = location_td.get_text(separator=' ', strip=True).replace('•', '').replace('\xa0', ' ').strip()

        # Extract Salary
        # Salary is within a <strong> tag inside a <table> with bgcolor="#f3f2f1"
        salary_table = entry.find('table', bgcolor="#f3f2f1")
        if salary_table:
            salary_strong = salary_table.find('strong')
            if salary_strong:
                salary = salary_strong.get_text(strip=True)

        # Append to jobs list only if job_title and job_url are found
        if job_title != "N/A" and job_url != "N/A":
            jobs.append({
                'title': job_title,
                'company': company_name,
                'location': location,
                'salary': salary,
                'url': job_url
            })

    return jobs

def parse_linkedin_email(html_content):
    """
    Parses the HTML content of a LinkedIn Job Alert email to extract job details.

    Args:
        html_content (str): HTML content of the email.

    Returns:
        list of dict: A list containing job details with keys 'title', 'company', 'location', and 'url'.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    jobs = []

    # Find all 'td' elements with data-test-id="job-card"
    job_entries = soup.find_all('td', attrs={'data-test-id': 'job-card'})

    for entry in job_entries:
        # Extract Job Title and URL
        # Select the <a> tag with both 'font-bold' and 'text-md' classes
        job_title_tag = entry.select_one('a.font-bold.text-md')
        if job_title_tag and job_title_tag.has_attr('href'):
            job_title = job_title_tag.get_text(strip=True)
            job_url = job_title_tag['href']
            # Ensure the URL is absolute
            if not job_url.startswith('http'):
                job_url = 'https://www.linkedin.com' + job_url
        else:
            # Skip this job entry if title or URL is missing
            continue

        # Extract Company Name and Location
        company_location_tag = entry.find('p', class_=lambda x: x and 'text-system-gray-100' in x)
        if company_location_tag:
            company_location_text = company_location_tag.get_text(strip=True)
            # Split the text into company and location based on the '·' separator
            if '·' in company_location_text:
                company_name, location = [part.strip() for part in company_location_text.split('·', 1)]
            else:
                # Fallback if separator is missing
                company_name = company_location_text
                location = "N/A"
        else:
            company_name = "N/A"
            location = "N/A"

        # Append the extracted details to the jobs list
        jobs.append({
            'title': job_title,
            'company': company_name,
            'location': location,
            'url': job_url
        })

    return jobs