import ujson, os


language = {}


def load_library():
    current_path = os.path.join('/var/www/bot/' 'app', 'language')
    for file in os.listdir(current_path):
        if file.endswith('json'):
            with open(os.path.join(current_path, file), 'rb') as asset:
                language[file.split('.')[0]] = ujson.loads(asset.read())


if __name__ != '__main__':
	load_library()
