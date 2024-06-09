from re import finditer

from nbsio import NbsSong, Note

NOTE_REGEX = r'(\d+)?>(.)'

NOTE_MAPPING = {
    'abcdefghijklmnopqrstuvwxy': 0,
    'zABCDEFGHIJKLMNOPQRSTUVWX': 1,
   r'YZ!§½#£¤$%&/{[(])=}?\+´`^': 2,
    "~¨*'.;,:-_<µ€ÌìíÍïÏîÎóÓòÒ": 3,
    'öÖåÅäÄñÑõÕúÚùÙüûÜÛéÉèÈêÊë': 4
}

def mcsp2nbs(filename: str) -> NbsSong:
    '''It reads the file, splits it into two parts, parses the first part, and
    then parses the second part if it exists
    
    Parameters
    ----------
    filename : str
        The file path to the .mcsp file
    
    Returns
    -------
        A NBSSong object
    
    '''
    
    with open(filename, 'r', encoding='ansi') as f:
        main_part = f.readline()
        metadata_part = f.readline()
        song = NbsSong()
        header = song.header

        main_elements = main_part.split('|')
        main_elements.pop(0)
        auto_save = int(main_elements.pop(0))
        header.auto_save = auto_save != 0
        header.auto_save_time = auto_save
        header.name = main_elements.pop(0)
        header.author = main_elements.pop(0)
        header.orig_author = main_elements.pop(0)
        header.import_name = filename

        main_elements.pop(0)

        notes = song.notes
        tick = 0
        it = iter(main_elements)
        for element in it:
            col_offset = int(element)
            tick += col_offset
            col_notes = next(it)

            layer = 0
            for match in finditer(NOTE_REGEX, col_notes):
                layer_offset = int(match[1])
                layer += layer_offset
                note_data = match[2]
                for keys, inst in NOTE_MAPPING.items():
                    if note_data in keys:
                        key = keys.index(note_data) + 33
                        notes.append(Note(int(tick), layer, inst, key))
                        break
                else:
                    raise KeyError(note_data)

        if metadata_part:
            metadata = metadata_part.split('|')
            header.tempo = int(metadata.pop(0))
            header.left_clicks = int(metadata.pop(0))
            header.right_clicks = int(metadata.pop(0))
            header.block_added = int(metadata.pop(0))
            header.block_removed = int(metadata.pop(0))
            header.minutes_spent = int(metadata.pop(0))
            song.appendix = '|'.join(metadata)

        song.correctData()
        return song

if __name__ == '__main__':
    import sys
    mcsp2nbs(sys.argv[1]).write('output.nbs')