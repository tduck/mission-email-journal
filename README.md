mission-email-journal
=====================

Missionary Email Journal Creator (CS 360 Project)

After finishing 2 years of missionary service, many despreately search for every way possible to remember their experience. The weekly emails home often provide not only an ideal record of the weekly goings on of the missionary but also of the unique interaction between a misionary and those he or she is closest to. The basic idea of this project is to create a simple to use service that provides missionaries with the ability to track their email correspondence during their two years of service. Reports generated on the site using the emails we've stored will provide a record, similar to a journal, of the missionary's communication with the outside world. 

Technologies:

    Flask/Jinja2
    PyMongo
    Mail Server(implements SMTP protocol)
    
Goals:

    Minimum Viable Product...
        - supports user registration
        - allows a registered user to download a report/journal of all their recorded emails
    Extended Goals...
        - include a rich text editor that allows emails we have in storage to be editted
        - store and include attatchments that come with the email
        - include different report formats for emails with certain key words in the subject
        - provide compatability with myldsmail's feature that allows you to export all emails. 
