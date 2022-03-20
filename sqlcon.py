import psycopg2

import imageprocessing


class Database:
    def __init__(self, database_url):
        try:
            self.conn = psycopg2.connect(database_url, sslmode = 'require' )
        except Exception as e:
            print(f"Error occurred when connecting to database: {e}")

    def _conn(func):
        def wrapper(self, *args, **kwargs):
            self.cur = self.conn.cursor()
            result = func(self, *args, **kwargs)
            self.cur.close()
            return result
        return wrapper

    @_conn
    def create_tables(self):
        # # Create user table
        # query="""CREATE TABLE users(
        # user_id bigint PRIMARY KEY NOT NULL
        # )"""

        # self.cur.execute(query)

        # Create pics table
        query = """CREATE TABLE sources(
        img_id SERIAL,
        img_url varchar(255) NOT NULL UNIQUE,
        window_point_x int NOT NULL,
        window_point_y int NOT NULL,
        window_a int NOT NULL,
        window_b int NOT NULL)
        """

        self.cur.execute(query)
        self.conn.commit()

    @_conn
    def another_query(self):
        query = """DROP TABLE Sources;
        """
        # query="""ALTER TABLE sources DROP CONSTRAINT ix_sources;
        # """
        # query = """SELECT name, current_setting(name)
        # FROM pg_settings;
        #         """
        # query = """ALTER SYSTEM SET block_size = '1073741824';
        # """
        self.cur.execute(query)
        # result = self.cur.fetchall()
        # print(result)
        self.conn.commit()

    @_conn
    def delete_pic_by_id(self, img_id):
        query="""DELETE FROM sources WHERE img_id = %i;
        """ %img_id

        self.cur.execute(query)
        self.conn.commit()


    @_conn
    def add_pic(self, pic_url, window_point, window_size):
        """

        :param pic_data: numpy array
        :param pic_size: tuple (3,)
        :return: None
        """
        query = """INSERT INTO sources (img_url, window_point_x, window_point_y, window_a, window_b) 
        VALUES ('%s', %i, %i, %i, %i );
        """ %(pic_url, window_point[0], window_point[1], window_size[0], window_size[1])

        self.cur.execute(query)
        self.conn.commit()

    @_conn
    def add_user(self, user_id):
        query = """INSERT INTO users (user_id) VALUES (%i)
        """ %(user_id)

        self.cur.execute(query)
        self.conn.commit()

    @_conn
    def get_all_pics(self):

        query="""SELECT * FROM sources
        """

        self.cur.execute(query)
        result = self.cur.fetchall()
        print(result)

        return result

    @_conn
    def get_random_pic(self):

        query="""SELECT * FROM sources ORDER BY RANDOM() LIMIT 1
        """

        self.cur.execute(query)
        result = self.cur.fetchall()

        return result

    @_conn
    def get_pic_by_id(self, img_id):

        query="""SELECT * FROM sources WHERE img_id = %s
        """%img_id

        self.cur.execute(query)
        result = self.cur.fetchall()

        return result

    @_conn
    def get_users(self):

        query = """SELECT * FROM users
        """

        self.cur.execute(query)
        result = self.cur.fetchall()

        return result

    def close(self):
            self.conn.close()

if __name__ == "__main__":
    db = Database(
'postgres://rslvvjpdsdkpgg:7ceaba1d59e559453ae4cefdbc1b96e3a62cfb4455446059cb6ec6d58d22bbbe@ec2-44-195-191-252.compute-1.amazonaws.com:5432/ddrkkg75nsm2ho'
    )
    db.another_query()
    db.create_tables()
    for link in open(r'd:\links.txt','r').read().split('\n'):
        url = '%s/image.jpg' %link.replace('ibb.co','i.ibb.co')
        size, point = imageprocessing.get_coords(url)
        try:
            db.add_pic(url, size, point)
        except:
            pass