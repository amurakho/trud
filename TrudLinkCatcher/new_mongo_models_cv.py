import datetime
from mongoengine import *
from mongoengine import signals as sig
import re

GENDER = (('male', 'male'),
          ('female', 'female'))


class Location(Document): #hh
    address = StringField()


class Title(Document):
    name = StringField()


class Name(EmbeddedDocument):
    fullname = StringField()

class Platform(Document):
    name = StringField()



class DriverLicense(EmbeddedDocument):
    type = ListField(StringField()) #hh
    description = StringField() # rabota
    own_car = BooleanField(null=True, default=None) #hh


class Salary(EmbeddedDocument): #hh
    currency = StringField()
    salary = IntField()


class SocialNetwork(EmbeddedDocument):
    platform = ReferenceField(Platform)
    url = URLField()


class Language(Document):
    name = StringField()
    level_grade = IntField()


class Keyword(Document):
    name = StringField()


class Skill(Document): #hh
    name = ListField(StringField()) #hh


class Portfolio(EmbeddedDocument):
    description = StringField()
    url = URLField()


class AdditionalEducation(EmbeddedDocument):
    start_date = DateTimeField()
    end_date = DateTimeField() #hh #rab
    organization_name = StringField() #hh
    course_name = StringField() #hh #rab
    description = StringField() #rab #work
    position = ReferenceField(Title)
    location = ReferenceField(Location) #rab


class Certificate(EmbeddedDocument):
    certificate = StringField() #hh
    url = URLField() #hh
    organization_name = StringField() #hh
    end_date = DateTimeField() #hh
    start_date = DateTimeField()
    position = ReferenceField(Title)
    description = StringField()
    location = ReferenceField(Location)


class Education(EmbeddedDocument):
    school_name = StringField() #hh #rabota
    faculty = StringField() #hh #rabota
    specialization = StringField()
    disciplines = ListField(StringField())
    location = ReferenceField(Location) #rabota #work
    start_year = DateTimeField()
    end_year = DateTimeField() #hh
    description = StringField()
    degree = StringField() # work


class SubIndustry(Document): #hh
    name = StringField() #hh


class Industry(Document): #hh
    name = StringField() #hh
    sub_industry = ListField(ReferenceField(SubIndustry)) #hh


class WorkExperience(EmbeddedDocument):
    position = ReferenceField(Title) #hh # rab
    start_date = DateTimeField() #hh # rab
    end_date = DateTimeField() #hh # rab
    till_now = BooleanField(default=False) #hh # rab
    company_description = StringField()
    location = ReferenceField(Location)
    company_url = URLField()
    company_name = StringField() #hh # rab
    industry = ReferenceField(Industry) #rab
    employer = StringField()
    job_description = StringField() #hh #rab


class Relocation(EmbeddedDocument): #hh
    type = StringField()
    is_possible = BooleanField() #hh
    locations = ListField(ReferenceField(Location)) #hh


class Recommendation(EmbeddedDocument): #hh
    company_name = StringField()
    referee = EmbeddedDocumentField(Name)
    position = StringField()
    phone = StringField()
    email = StringField()


class AnotherInformation(EmbeddedDocument):
    text = StringField()
    title = StringField()


class RawHtml(Document):
    created_at = DateTimeField()
    html = StringField()


class WorkPermission(EmbeddedDocument):
    locations = ListField(ReferenceField(Location))


class Cv(Document):
    url = URLField() #all
    img_src = URLField() #all

    created_at = DateTimeField() #all
    date_added = DateTimeField() #all
    updated_by_owner = DateTimeField() #all
    birth_date = DateTimeField() #hh

    gender = StringField(choices=GENDER) #hh

    cv_lang = StringField() # ? hh
    about_me = StringField() # rab #work
    photo_storage = StringField() #hh
    job_status = StringField() # rab

    nationality = ListField(StringField()) #hh
    employment_type = ListField(StringField()) #hh
    work_schedule = ListField(StringField()) #hh

    age = IntField() #hh
    travel_time_to_work = IntField() #hh

    title = ReferenceField(Title) #hh
    platform = ReferenceField(Platform) #hh
    location = ReferenceField(Location) #hh


    skills = ListField(ReferenceField(Skill)) # all
    keywords = ListField(ReferenceField(Keyword)) # all
    languages = ListField(ReferenceField(Language)) #all
    raw_html = ListField(ReferenceField(RawHtml))  # all
    industry = ListField(ReferenceField(Industry))  #hh # work

    name = EmbeddedDocumentField(Name) #hh
    salary = EmbeddedDocumentField(Salary) #hh
    driver_license = EmbeddedDocumentField(DriverLicense) #hh
    social_networks = ListField(EmbeddedDocumentField(SocialNetwork))
    relocation = EmbeddedDocumentField(Relocation) #hh
    work_permission = EmbeddedDocumentField(WorkPermission) #hh


    education = ListField(EmbeddedDocumentField(Education)) #hh
    certificate = ListField(EmbeddedDocumentField(Education)) #hh
    additional_education = ListField(EmbeddedDocumentField(AdditionalEducation)) #hh
    experience = ListField(EmbeddedDocumentField(WorkExperience))  #hh
    portfolio = ListField(EmbeddedDocumentField(Portfolio)) #hh
    recommendation = ListField(EmbeddedDocumentField(Recommendation)) #hh
    another_information = ListField(EmbeddedDocumentField(AnotherInformation))  # rabota

    is_moved = BooleanField(null=True, default=None)
    hidden = BooleanField(default=False)
    business_trips = BooleanField(default=None) #hh
    international_passport = BooleanField(null=True, default=None) #hh



    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.date_added = datetime.datetime.now()