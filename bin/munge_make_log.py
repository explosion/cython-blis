import sys
import json

for line in sys.stdin:
    if not line.startswith('gcc'):
        continue
    pieces = line.split()
    args = {}
    flags = []
    macros = []
    includes = []
    for i, piece in enumerate(pieces):
        if piece == '-c':
            args['source'] = pieces[i+1]
        elif piece == '-o':
            args['target'] = pieces[i+1]
        elif piece.startswith('-f') or piece.startswith('-m') or piece.startswith('-O'):
            flags.append(piece)
        elif piece.startswith('-std'):
            flags.append(piece)
        elif piece.startswith('-D'):
            macros.append(piece.replace('\\', ''))
        elif piece.startswith('-I'):
            includes.append(piece)
    if 'source' in args:
        args['flags'] = flags
        args['macros'] = macros
        args['include'] = includes
        print(json.dumps(args))
