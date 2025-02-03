from bs4 import BeautifulSoup
from gmail_integration.utils import determine_experience_level, determine_job_type

def parse_indeed_email(html_content):
    """
    Parses the HTML content of an Indeed Job Alert email to extract job details.
    Returns:
        list of dict: A list of job records with as many fields as we can parse
                      (title, company_name, location, salary, job_url,
                       job_description_snippet, job_type, experience_level).
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    jobs = []

    # Find all <a> tags with href containing 'rc/clk/dl' 
    job_entries = soup.find_all('a', href=lambda href: href and 'rc/clk/dl' in href)

    for entry in job_entries:
        job_title = "N/A"
        job_url = "N/A"
        company_name = "N/A"
        location = "N/A"
        salary = "N/A"
        job_description_snippet = "Description unavailable..."
        job_type = "Unknown"
        experience_level = "Unknown"

        job_url = entry.get('href', 'N/A')  
        
        # Job Title
        h2_tag = entry.find('h2')
        if h2_tag:
            inner_a_tag = h2_tag.find('a')
            if inner_a_tag:
                job_title = inner_a_tag.get_text(strip=True)

       # Company Name         
        company_td = entry.select_one('td[style*="padding:0 12px 0 0"]')
        if company_td:
            company_name = company_td.get_text(strip=True)

        # Location
        location_td = company_td.find_next('td', style=lambda v: v and 'font-size:14px;line-height:21px' in v) if company_td else None
        if location_td:
            location = location_td.get_text(separator=' ', strip=True).replace('•', '').replace('\xa0', ' ').strip()

        # Salary
        salary_table = entry.find('table', bgcolor="#f3f2f1")
        if salary_table:
            salary_strong = salary_table.find('strong')
            if salary_strong:
                salary = salary_strong.get_text(strip=True)
        
        # Job Description Snippet
        snippet_td = entry.find(
            'td',
            style=lambda s: s and "padding:0;color:#767676;font-size:14px;line-height:21px" in s
        )
        if snippet_td:
            snippet_text = snippet_td.get_text(strip=True)
            # Keep it short or store the entire snippet
            job_description_snippet = snippet_text

        # Job Type (remove, onsite, hybrid)
        job_type = determine_job_type(location)
        print(f'job type from parse indeed email: {job_type}')
        
        # Experience Level (if included in title)
        experience_level = determine_experience_level(job_title)

        if job_title != "N/A" and job_url != "N/A":
            jobs.append({
                'title': job_title,
                'company_name': company_name,
                'location': location,
                'salary': salary,
                'job_url': job_url,
                'job_description_snippet': job_description_snippet,
                'job_type': job_type,
                'experience_level': experience_level,
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
                parts = [part.strip() for part in company_location_text.split('·')]
                if len(parts) >= 2:
                    company_name = parts[0]  # First part is the company name
                    location = '·'.join(parts[1:]).strip()  # Join remaining parts as location
                    print(f'location: {location}')
                else:
                    # Fallback if separator is present but doesn't split into two parts
                    company_name = company_location_text
                    location = "N/A"
            else:
                # Fallback if separator is missing
                company_name = company_location_text
                location = "N/A"
        else:
            company_name = "N/A"
            location = "N/A"

        # Experience Level (if included in title)
        experience_level = determine_experience_level(job_title)

        # Job Type (remove, onsite, hybrid)
        job_type = determine_job_type(location)
        print(f'job type from parse linkedin email: {job_type}')

        jobs.append({
            'title': job_title,
            'company_name': company_name,
            'location': location,
            'job_url': job_url,
            'experience_level': experience_level,
            'job_type': job_type
        })

    return jobs