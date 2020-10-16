import Utils as Utils

class DrawIOUtils:
    UTILS = Utils.Utils()

    def get_connection_text(self, predicate_label):

        connection_text = '# connect: {"to": "id", "invert": true, "style":"curved=0;endArrow=blockThin;endFill=1;", '

        id = self.UTILS.clean_label(predicate_label)

        connection_text = connection_text + '"from": ' + '"' + id + '",'

        connection_text = connection_text + ' "label": ' + '"' + predicate_label + '" }'

        return connection_text