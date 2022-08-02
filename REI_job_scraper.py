#!/usr/bin/env python
# coding: utf-8


import requests

from bs4 import BeautifulSoup

import smtplib

from email.message import EmailMessage

from datetime import datetime, timedelta, date


yesterday = date.today() - timedelta(days=1)

# These links are of each cities results sorted by date posted decending
brentwood_rei_url = 'https://rei.jobs/careers/SearchJobs/?3_73_3=37158&jobSort=postedDate&jobSortDirection=DESC&'
lebanon_rei_url = 'https://rei.jobs/careers/SearchJobs/?3_73_3=5813561&jobSort=postedDate&jobSortDirection=DESC&'
chattanooga_rei_url = 'https://rei.jobs/careers/SearchJobs/?3_73_3=2217122&jobSort=postedDate&jobSortDirection=DESC&'


def get_job_titles(url, dict_to_append):
    """This function takes a job search url and an empty dict and appends the url of each job as the key
    and a list of job title and date posted as the values"""
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    joblist = soup.find('ul', class_='jobList')
    for li in joblist.find_all('li', class_="group"):
        title = li.find('a').get('title')
        link = li.find('a').get('href')
        if li.find('p') is None:
            pass
        else:
            date_str = li.find('p').find_all('span')[1].text.split(' ', 1)[1]
            date_obj = datetime.strptime(date_str, '%m-%d-%Y').date()

        dict_to_append.update({link: [title, date_obj]})


# Initialize dict
job_dict = {}

# Use function to fill dict with each city of interest
get_job_titles(brentwood_rei_url, job_dict)
get_job_titles(lebanon_rei_url, job_dict)
get_job_titles(chattanooga_rei_url, job_dict)


# Initialize empty string to eventually become email message
new_jobs_str = ''

# Look for jobs posted yesterday, add them to the email message
for (k, v) in job_dict.items():
    if v[1] > yesterday:
        new_jobs_str += f'{str(v[0])}\n{k}\n\n'
    else:
        pass


# If the email message has new jobs send the email to receiver
if len(new_jobs_str) == 0:
    print('No new jobs')
else:
    smtpHost = 'smtp.office365.com'
    smtpPort = 587
    sender = 'georgetregoning@gmail.com'
    with open(r'C:\Users\georg\Documents\REI Download\outlookpassword.txt') as f:
        password = f.readlines()[0]

    receiver = ['annie.graefe@gmail.com']

    subject = "New Brentwood-Chatt-Lebanon REI Jobs"
    # Add the From: and To: headers at the start!
    message = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
               % (sender, ", ".join(receiver), subject))
    message += new_jobs_str

    try:
        smtpObj = smtplib.SMTP(smtpHost, smtpPort)
        # smtpObj.set_debuglevel(1)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()
        smtpObj.login(sender, password)
        smtpObj.sendmail(sender, receiver, message)
        smtpObj.quit()
        print("Successfully sent email")
    except:
        print("Error: unable to send email")
