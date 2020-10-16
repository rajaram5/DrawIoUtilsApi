import Utils as Utils




texts = {"name":"http://xmlns.com/foaf/0.1/name", "firstname":"http://xmlns.com/foaf/0.1/firstname",
         "lastname":"http://xmlns.com/foaf/0.1/lastname"}

UTILS = Utils.Utils()

for key, value in texts.items():

    pr = UTILS.get_prefix(value, key)

    print (pr)