from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Create DB session
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurants = session.query(Restaurant).all()

                output = ""
                output += "<html><body>"
                output += "<a href='/restaurants/new'>Make a New Restaurant Here</a><br><br>"

                for restaurant in restaurants:
                    output += restaurant.name
                    output += "<br>"
                    output += "<a href='/restaurants/%s/edit'>Edit</a><br>" % restaurant.id
                    output += "<a href='#'>Delete</a><br>"
                    output += "<br>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body><h1>Make a New Restaurant</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
                output += "<input name='restName' type='text' placeholder='New Restaurant Name'>"
                output += "<input type='submit' value='Create'>"
                output += "</form></body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/edit"):
                restID = self.path.split("/")[2]
                restUpdate = session.query(Restaurant).filter_by(id=restID).one()

                if restUpdate:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    output = ""
                    output += "<html><body><h1>%s</h1>" % restUpdate.name
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % restID
                    output += "<input name='newRestName' type='text' placeholder='%s'>" % restUpdate.name
                    output += "<input type='submit' value='Rename'>"
                    output += "</form></body></html>"
                    self.wfile.write(output)
                    print output
                    return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('restName')

                    newRest = Restaurant(name=messagecontent[0])
                    session.add(newRest)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestName')

                    restID = self.path.split("/")[2]
                    restUpdate = session.query(Restaurant).filter_by(id=restID).one()

                    restUpdate.name = messagecontent[0]
                    session.add(restUpdate)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
