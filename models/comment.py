from models.dbSettings import db
from datetime import datetime
from email_helper import send_email,send_email_from_sendgridlib

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)

    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))
    topic = db.relationship("Topic")

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship("User")

    created = db.Column(db.DateTime,default= datetime.utcnow())


    @classmethod
    def create(cls, text, author, topic):
        comment = cls(text=text, author=author, topic=topic)
        #adding comment to database
        db.add(comment)
        db.commit()

        #send email using email helper
        # if topic.author.email:
        #     send_email(receiver_email=topic.author.email,
        #                subject="New Comment on your topic - {}!!".format(topic.title),
        #                text="Your topic has one comment : {0} - by {1} ".format(text, author))

        #send email using sendgrid-python
        if topic.author.email:
            send_email_from_sendgridlib(receiver_email=topic.author.email,
                       subject="New Comment on your topic - {}!!".format(topic.title),
                       text="Your topic has one comment : {0} - by {1} ".format(text, author))

        return comment


