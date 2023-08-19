from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import user

class Show:
    DB='tv_shows'
    def __init__(self,data):
        self.id = data['id']
        self.title = data['title']
        self.network = data['network']
        self.release_date = data['release_date']
        self.description = data['description']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.owner = None
        self.likes = []

    @classmethod
    def save(cls,data):
        query = """
                INSERT INTO shows (title,network,release_date,description,user_id)
                VALUES (%(title)s, %(network)s, %(release_date)s, %(description)s, %(user_id)s);
                """
        return connectToMySQL(cls.DB).query_db(query,data)
    

    @classmethod
    def update(cls,data):
        query = """
                UPDATE shows 
                SET title = %(title)s, network = %(network)s , description = %(description)s , release_date = %(release_date)s
                WHERE id=%(id)s;
                """
        return connectToMySQL(cls.DB).query_db(query,data)

    @classmethod
    def get_one_by_id(cls,show_id):
        data = {
            'id': show_id
        }
        query = """
				SELECT * FROM shows
                LEFT JOIN users ON shows.user_id = users.id
                LEFT JOIN likes ON shows.id = likes.show_id
                LEFT JOIN users AS liking_users ON likes.user_id = liking_users.id
                WHERE shows.id = %(id)s;
                """
        show_dict = (connectToMySQL(cls.DB).query_db(query,data))
        show_obj = cls(show_dict[0])
        owner_data = {
            'id' : show_dict[0]['users.id'],
            'first_name' : show_dict[0]['first_name'],
            'last_name' : show_dict[0]['last_name'],
            'email' : show_dict[0]['email'],
            'password' : show_dict[0]['password'],
            'created_at' : show_dict[0]['users.created_at'],
            'updated_at' : show_dict[0]['users.updated_at']
        }
        show_obj.owner = user.User(owner_data)
        if not show_dict[0]['likes.user_id'] == None:
            show_likes = []  
            for row in show_dict:
                like_data = {
                    'id' : row['liking_users.id'],
                    'first_name' : row['liking_users.first_name'],
                    'last_name' : row['liking_users.last_name'],
                    'email' : row['liking_users.email'],
                    'password' : row['liking_users.password'],
                    'created_at' : row['liking_users.created_at'],
                    'updated_at' : row['liking_users.updated_at']
                }
                show_like_obj = user.User(like_data) # create an object for the 'liker'
                show_likes.append(show_like_obj) # add the 'liker' object to the list of 'show_likes'
            show_obj.likes = show_likes
        return show_obj

    @classmethod
    def get_all(cls):
        query = """
				SELECT * FROM shows
                LEFT JOIN users ON shows.user_id = users.id
                LEFT JOIN likes ON shows.id = likes.show_id
                LEFT JOIN users AS liking_users ON likes.user_id = liking_users.id;
                """
        show_dict = (connectToMySQL(cls.DB).query_db(query))
        if not show_dict:
            return []
        list_of_shows = []  
        current_show_id = None
        for row in show_dict:
            if not current_show_id == row['id']: # must be either the very first row or the first row of a new show
                if not current_show_id == None: # must be the first row a a show that is not the very first
                    show_obj.likes = show_likes 
                    list_of_shows.append(show_obj) #add the previous show to 'list_of_shows'
                # start working on the first row of new show
                show_obj = cls(row) # create the show object
                current_show_id = row['id'] # update the 'current_show_id' as soon as we've created the new show object
                data = {
                    'id' : row['users.id'],
                    'first_name' : row['first_name'],
                    'last_name' : row['last_name'],
                    'email' : row['email'],
                    'password' : row['password'],
                    'created_at' : row['users.created_at'],
                    'updated_at' : row['users.updated_at']
                }
                show_obj.owner = user.User(data) # add the owner object to the show object
                current_show_id = row['id'] # now update the 'current_show_id'
                show_likes = [] # reset list of likes to empty
            if not row['likes.user_id'] == None: # if the current row includes 'like' data
                # make 'show_like'_obj
                like_data = {
                    'id' : row['liking_users.id'],
                    'first_name' : row['liking_users.first_name'],
                    'last_name' : row['liking_users.last_name'],
                    'email' : row['liking_users.email'],
                    'password' : row['liking_users.password'],
                    'created_at' : row['liking_users.created_at'],
                    'updated_at' : row['liking_users.updated_at']
                }
                show_like_obj = user.User(like_data) # create an object for the 'liker'
                show_likes.append(show_like_obj) # add the 'liker' object to the list of 'show_likes'
        #exited loop after last row
        show_obj.likes = show_likes 
        list_of_shows.append(show_obj) #add the final show to list
        return list_of_shows
    
    @classmethod
    def delete(cls,show_id):
        data = {
            'show_id' : show_id
        }
        query = """
                DELETE FROM likes
                WHERE show_id=%(show_id)s;
                """
        connectToMySQL(cls.DB).query_db(query,data) # first, delete all the associated likes
        data = {
            'id' : show_id
        }
        query = """
                DELETE FROM shows
                WHERE id=%(id)s;
                """
        return connectToMySQL(cls.DB).query_db(query,data) # then, delete the show
    
    @classmethod
    def like_show(cls,show_id, user_id):
        data = {
            'show_id' : show_id,
            'user_id' : user_id
        }
        query = """
                INSERT INTO likes (user_id,show_id)
                VALUES (%(user_id)s, %(show_id)s);
                """
        results = connectToMySQL(cls.DB).query_db(query,data)
        return results

    @classmethod
    def unlike_show(cls,show_id,user_id):
        data = {
            'show_id' : show_id,
            'user_id' : user_id
        }
        query = """
                DELETE FROM likes
                WHERE user_id=%(user_id)s and show_id=%(show_id)s;
                """
        results = connectToMySQL(cls.DB).query_db(query,data)
        return results

    @staticmethod
    def show_is_valid(data):
        is_valid=True
        if len(data['title'].strip())<3:
            flash("Title is insufficient length.")
            is_valid=False
        if len(data['network'].strip())<3:
            flash("Network information is insufficient.")
            is_valid=False
        if len(data['description'].strip())<3:
            flash("Longer description is needed.")
            is_valid=False
        if 'release_date' not in data or data['release_date']=='':
            flash("Please select release date for this show.")
            is_valid=False  
        return is_valid