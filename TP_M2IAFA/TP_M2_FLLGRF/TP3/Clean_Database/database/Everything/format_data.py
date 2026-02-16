file = "database.graphml"
formated_file = file[:-8] + "_formated_for_NetworkX.graphml"

def remove_new_line_in_text(file, formated_file):
    with open(file) as f, open(formated_file, 'w') as f_new:
        contents = []
        for line in f:
            if line[0] == "<":
                contents.append(line[:-1])
            else:
                contents[-1] += '\\n' + line[:-1]

        # On ajoute manuellement la présence de l'attribut "id"
        contents.insert(27, '<key id="id" for="node" attr.name="id" attr.type="string"/>')
        contents.insert(30, '<key id="id" for="edge" attr.name="id" attr.type="string"/>')
        f_new.write("\n".join(contents)) # On enlève le premier \n et on écrit le fichier

remove_new_line_in_text(file, formated_file)