EXPERIENCE_LEVEL_MAPPING = [
    ("co-op", "Intern"),  
    ("intern", "Intern"),
    ("junior", "Junior"),
    ("associate", "Junior"),
    ("assistant", "Junior"),
    ("coordinator", "Junior"),
    ("trainee", "Junior"),
    ("entry", "Junior"),
    ("senior", "Senior"),
    ("lead", "Senior"),
    ("principal", "Senior"),
    ("head", "Senior"),
    ("director", "Senior"),
    ("vp", "Senior"),
    ("chief", "Senior"),
    ("executive", "Senior"),
    ("manager", "Mid-Level"),
    ("supervisor", "Mid-Level"),
    ("consultant", "Mid-Level"),
    ("engineer", "Mid-Level"),
    ("analyst", "Mid-Level"),
    ("specialist", "Mid-Level"),
    ("intermediate", "Mid-Level"),
]

def determine_experience_level(job_title):
    """
    Determines the experience level based on keywords in the job title.
    Args:
        job_title (str): The job title to analyze.
    Returns:
        str: The experience level (e.g., "Senior", "Mid-Level", "Junior", "Intern").
    """
    job_title_lower = job_title.lower()
    for keyword, level in EXPERIENCE_LEVEL_MAPPING:
        if keyword in job_title_lower:
            return level
    return "Unknown"  

def determine_job_type(location):
    """
    Determines the job type (Remote, Hybrid, In Person, etc) based on the location string.
    Args:
        location (str): The location to analyze.
    Returns:
        str: The job type (e.g., "Remote", "Hybrid", "In Person", "Unknown").
    """
    if not location or location == "N/A":
        return "Unknown"

    location_lower = location.lower()

    if "hybrid remote" in location_lower:
        job_type = "Hybrid Remote"
    elif "hybrid" in location_lower:
        job_type = "Hybrid"
    elif "remote" in location_lower or "work from home" in location_lower or "wfh" in location_lower:
        job_type = "Remote"
    elif "on-site" in location_lower or "on site" in location_lower or "in-office" in location_lower:
        job_type = "On-site"
    elif "in person" in location_lower or "office-based" in location_lower:
        job_type = "In Person"
    else:
        job_type = "In Person"

    return job_type