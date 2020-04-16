from http.server import BaseHTTPRequestHandler, HTTPServer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.database_setup import Base, Restaurant
import cgi

new_restaurant_from = '''<form method='POST' enctype='multipart/form-data' action='/set_restaurant'>
<h2>Enter new restaurant</h2>
<input name="new_restaurant_name" type="text" >
<input type="submit" value="Submit"></form>'''

edit_restaurant_from = '''<form method='POST' enctype='multipart/form-data' action='/restaurants/{0}/rename_restaurant'>
<h2>Rename restaurant {1}</h2>
<input name="restaurant_rename" type="text" >
<input type="submit" value="Submit"></form>'''

delete_restaurant_from = '''
<form method='POST' enctype='multipart/form-data' action='/restaurants/{0}/delete_restaurant'>
<h2>Delete restaurant {1}?</h2>
<input type="submit" value="Delete"></form>'''


engine = create_engine('sqlite:///restaurantmenu.db')
# This command creates the connections between our class definitions and the corresponding tables in the db.
Base.metadata.bind = engine
# create a session, add an entry, commit and exit
db_session = sessionmaker(bind=engine)


def add_new_restaurant(messagecontent):
    session = db_session()
    first_restaurant = Restaurant(name=messagecontent)
    session.add(first_restaurant)
    session.commit()


def edit_restaurant_name(restaurant_id, new_name):
    session = db_session()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    restaurant.name = new_name
    session.add(restaurant)
    session.commit()


def delete_restaurant(restaurant_id):
    session = db_session()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    session.delete(restaurant)
    session.commit()


def get_restaurant_name_by_id(restaurant_id):
    session = db_session()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    return restaurant.name


class BasicRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path and self.path.endswith("/restaurants"):
                self.set_headers_200()
                message = self.main_page()
                self.wfile.write(message.encode())
            elif self.path and self.path.endswith("/restaurants/new"):
                self.set_headers_200()
                message = "<html><body>{0}</body></html>".format(new_restaurant_from)
                self.wfile.write(message.encode())
            elif self.path and self.path.find("restaurants/") > 0 and self.path.endswith("/edit"):
                to_edit_id = int(self.path.split("/")[-2])
                res_name = get_restaurant_name_by_id(to_edit_id)
                edit_this_res = edit_restaurant_from.format(to_edit_id, res_name)
                self.set_headers_200()
                message = "<html><body>{0}</body></html>".format(edit_this_res)
                self.wfile.write(message.encode())
            elif self.path and self.path.find("restaurants/") > 0 and self.path.endswith("/delete"):
                to_edit_id = int(self.path.split("/")[-2])
                res_name = get_restaurant_name_by_id(to_edit_id)
                edit_this_res = delete_restaurant_from.format(to_edit_id, res_name)
                self.set_headers_200()
                message = "<html><body>{0}</body></html>".format(edit_this_res)
                self.wfile.write(message.encode())
            else:
                self.send_error(404, 'File Not Found: %s' % self.path)
        except Exception as e:
            self.send_error(500, 'Inner exception on: %s' % self.path)
            print(e)

    def do_POST(self):
        try:
            if self.path and self.path.endswith("/set_restaurant"):
                self.set_headers_301()
                messagecontent = self.get_form_data('new_restaurant_name')
                if not messagecontent:
                    raise Exception("no form data")
                else:
                    add_new_restaurant(messagecontent)
            elif self.path and self.path.endswith("/rename_restaurant"):
                self.set_headers_301()
                to_edit_id = int(self.path.split("/")[-2])
                messagecontent = self.get_form_data('restaurant_rename')
                if not messagecontent:
                    raise Exception("no form data")
                else:
                    edit_restaurant_name(to_edit_id, messagecontent)
            elif self.path and self.path.endswith("/delete_restaurant"):
                self.set_headers_301()
                to_edit_id = int(self.path.split("/")[-2])
                delete_restaurant(to_edit_id)
            else:
                self.send_error(404, 'Invalid POST: %s' % self.path)
        except Exception as e:
            self.send_error(500, 'Inner exception on: %s' % self.path)
            print(e)

    def set_headers_301(self):
        self.send_response(301)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', '/restaurants')
        self.end_headers()

    def get_form_data(self, form_text_elem_name):
        ctype, p_dict = cgi.parse_header(
            self.headers.get('content-type'))
        p_dict['boundary'] = bytes(p_dict['boundary'], "utf-8")
        content_len = int(self.headers.get('Content-length'))
        p_dict['CONTENT-LENGTH'] = content_len
        if ctype == 'multipart/form-data':
            fields = cgi.parse_multipart(self.rfile, p_dict)
            messagecontent = fields.get(form_text_elem_name)
            return messagecontent[0].decode()
        else:
            return None

    def main_page(self):
        message = "<html><body>"
        message += '''<a href="/restaurants/new">Create a new restaurant</a></br>'''
        session = db_session()
        for restaurant in session.query(Restaurant).all():
            message += '''{name}</br>'''.format(name=restaurant.name)
            message += '''<a href="restaurants/{res_id}/edit">Edit</a></br>'''.format(res_id=restaurant.id)
            message += '''<a href="restaurants/{res_id}/delete">Delete</a></br>'''.format(res_id=restaurant.id)
            message += '''</br>'''
        session.close()
        message += "</body></html>"
        return message

    def set_headers_200(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()


def main():
    server = None
    try:
        port = 8080
        server = HTTPServer(('', port), BasicRequestHandler)
        print("Web Server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        if server:
            server.server_close()


if __name__ == '__main__':
    main()