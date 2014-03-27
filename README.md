mission-email-journal
=====================

Missionary Email Journal Creator (CS 360 Project)

After finishing 2 years of missionary service, many missionaries despreately search for every way possible to remember their experience. The weekly emails home often provide not only an ideal record of the weekly goings on of the missionary but also dialog the unique interaction between a misionary and those he or she is closest to. The basic idea of this project is to create a simple to use service that provides missionaries with the ability to track their email correspondence during their two years of service. Reports generated on the site using the emails we've stored will provide a record, similar to a journal, of the missionary's communication with the outside world. 

ARCHITECTURE
_____________
- Flask/Jinja2
- PyMongo
- Custom mail Server(implements SMTP protocol)
- Web server(mod_wsgi - Apache)
    
    

MINIMUM VIABLE PRODUCT
________
- supports user registration
- display stored emails on the web
- allows a registered user to download a pdf report/journal of all their recorded emails
- provide a date-range for downloading

 
    
EXTENDED GOALS
_________
- include a rich text editor that allows emails we have in storage to be editted
- store attatchments that come with the email and include them in the reports
- include different report formats for emails with certain key words in the subject
- provide compatability with myldsmail's feature that allows you to export all emails. 
- support shared accounts or public links to specific report
- support other file formats when downloading
- provide differnt kinds of reports(sent from missionary, sent to missionary, etc.)
