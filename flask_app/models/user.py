from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re

regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

class User:
    DB = 'tv_shows'
    def __init__(self,data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def save(cls,data):
        query = """
                INSERT INTO users (first_name,last_name,email,password)
                VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);
        """
        return connectToMySQL(cls.DB).query_db(query,data)
    
    @classmethod  # NOTE THIS IS USED IN REGISTRATION & LOGIN VALIDATION
    def get_one_by_email(cls,email):
        data = {
            'email' : email
        }
        query = """
                SELECT * FROM users
                WHERE email=%(email)s;
                """
        results = connectToMySQL(cls.DB).query_db(query,data)
        if not results:
            return False
        else:
            user_obj = cls(results[0])
            return user_obj
    
    
    @staticmethod
    def user_reg_is_valid(data): #validations for all fields in user registration
        is_valid = True
        if len(data['first_name'].strip())<2: #first name at least 2 characters
            flash("First name must be at least 2 characters.","registration")
            is_valid=False
        if len(data['last_name'].strip())<2:  #last name at least 2 characters
            flash("Last name must be at least 2 characters.","registration")
            is_valid=False
        if not re.fullmatch(regex_email, data['email']):  #email checked for correct format with regex
            flash("Invalid email.","registration")
            is_valid=False
        if User.get_one_by_email(data['email']):  #is email in the database?  'get_one_by_email' method should return flash if available
            flash("Email is already in use.","registration")
            is_valid=False
        if  bool(re.search(r"\s", data['password'])): #checks if there are any spaces in 'password'
            flash("Password may not contain any spaces.","registration")
            is_valid=False
        if len(data['password'])<8: #password must be at least 8 characters long
            flash("Password must be at least 8 characters.","registration")
            is_valid=False
        # potentially add more validations for password...
        if not data['password'] == data['confirm_password']: # finally check to make sure that passwords match
            flash("Password does not match.","registration")
            is_valid=False
        return is_valid