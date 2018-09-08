import os
import sys
import json

print(json.dumps({"environment": os.environ}))
for line in sys.stdin:
    if 'flatten-headers.py' in line:
        continue
    pieces = line.split()
    args = {}
    flags = []
    macros = []
    includes = []
    for i, piece in enumerate(pieces):
        if i == 0:
            args['compiler'] = piece
        elif piece == '-c':
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
