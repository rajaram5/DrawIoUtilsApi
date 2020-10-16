import Utils as Utils

class DrawIOUtils:
    UTILS = Utils.Utils()

    def get_connection_text(self, predicate_label):
        '''
        This method create draw.io connection text
        :param predicate_label: String object label of predicate
        :return: String object connection text
        '''

        connection_text = '# connect: {"to": "id", "invert": true, "style":"curved=0;endArrow=blockThin;endFill=1;", '
        predicate_id = self.UTILS.clean_label(predicate_label)
        connection_text = connection_text + '"from": ' + '"' + predicate_id + '",'
        connection_text = connection_text + ' "label": ' + '"' + predicate_label + '" }'
        return connection_text