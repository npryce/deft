
import sys
import mimetypes
import pkg_resources
import tornado.ioloop
import tornado.web
from tornado.web import URLSpec, RequestHandler, HTTPError
from tornado.template import Template
from markdown import Markdown
from deft.warn import PrintWarnings
import deft.tracker


markdown = Markdown(safe_mode=True, output_format="xhtml1")

# Not efficient!
def excerpt(description):
    return markdown.convert(description.splitlines()[0])

def titlify(name):
    return " ".join(s.capitalize() for s in name.split("-"))

class TrackerRepresentation(tornado.web.RequestHandler):
    def initialize(self, tracker):
        self.tracker = tracker
    
    def get(self):
        self.render("tracker.template", tracker=self.tracker, excerpt=excerpt, titlify=titlify)

class FeatureRepresentation(tornado.web.RequestHandler):
    def initialize(self, tracker):
        self.tracker = tracker
    
    def get(self, feature_name):
        feature = self.tracker.feature_named(feature_name)
        self.render("feature.template", tracker=self.tracker, feature=feature, markdown=markdown.convert)


class PackagedResources(tornado.web.RequestHandler):
    def initialize(self, module):
        self.module = module
    
    def get(self, resource_path):
        if not pkg_resources.resource_exists(self.module, resource_path):
            raise HTTPError(404)
        
        content_type, encoding = mimetypes.guess_type(resource_path)
        self.set_header("Content-Type", content_type)
        self.write(pkg_resources.resource_string(self.module, resource_path))


def main():
    tracker = deft.tracker.load_tracker(PrintWarnings(sys.stderr, "WARNING: "))
    
    app = tornado.web.Application([
            URLSpec(r"/", TrackerRepresentation, 
                    name="tracker", 
                    kwargs=dict(tracker=tracker)),
            URLSpec(r"/feature/(.+)", FeatureRepresentation, 
                    name="feature", 
                    kwargs=dict(tracker=tracker)),
            URLSpec(r"/static/((?:.+)\.(?:css|js|txt|ico|png|jpg))", PackagedResources, 
                    name="static", 
                    kwargs=dict(module=__name__))
    ], debug=True)
    
    app.listen(8888)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
