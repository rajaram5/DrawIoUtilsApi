from flask import Flask, request, Response
from werkzeug.datastructures import FileStorage
import RdfDrawing
import os
from flask_restplus import Resource, Api

app = Flask(__name__)
api = Api(app,
          version='0.1',
          title='Draw.io RDF drawing utils api alpha version',
          description='APIs to create RDF drawing',
          license='MIT',
          contact='Rajaram Kaliyaperumal',
          contact_url='https://www.linkedin.com/in/rajaram-kaliyaperumal-73677115')

app.config['UPLOAD_FOLDER'] = 'api-uploads/'

name_space = api.namespace('draw-io-utils', description='APIs to create RDF drawing from turtle file')

upload_parser = api.parser()
upload_parser.add_argument('file', location='files', type=FileStorage)

@name_space.route("/turtle-to-csv")
@api.expect(upload_parser)
class DrawIoCsv(Resource):
    ALLOWED_EXTENSIONS = {'ttl'}

    DRAW_IO_INSTANCE = RdfDrawing.RdfDrawing()

    @api.response(200, 'Draw.io CSV successfully created.')
    @api.response(422, 'Invalid input')
    @api.produces(["text/csv"])
    def post(self):

        # check if the post request has the file part
        if 'file' not in request.files:
            return Response('No file provided. Please provide a turtle file as n input.', status=422,
                            mimetype='text/plain')

        args = upload_parser.parse_args()
        file = args.get('file')

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return Response('No selected file', status=422, mimetype='text/plain')

        if not self.allowed_file(file.filename):
            return Response('Invalid file format provided. This app takes only text/turtle as an input', status=422,
                            mimetype='text/plain')

        if file and self.allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            input_file = app.config['UPLOAD_FOLDER'] + filename

            draw_io_text = self.DRAW_IO_INSTANCE.get_draw_io_csv(input_file)
            f = open("output/draw-io-output.csv", "w")
            f.write(draw_io_text)
            f.close()
            os.remove(input_file)
            return Response(draw_io_text, status=200, mimetype='text/csv')


    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) #run app in debug mode on port 5000