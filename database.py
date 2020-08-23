import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


class database():
    def __init__(self, key_file):
        # initializations 
        cred = credentials.Certificate(key_file)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def read(self, col_name, doc_name):
        try:        
            doc_ref = self.db.collection(col_name).document(doc_name)
            doc = doc_ref.get()
            return doc.to_dict()
        except Exception as ex:
            print(ex)

    def write(self, col_name, doc_name, **data):
        try:
            doc_ref = self.db.collection(col_name).document(doc_name)
            doc_ref.set(data)
        except Exception as ex:
            print(ex)
    
    def delete(self, col_name, doc_name):
        try:
            self.db.collection(col_name).document(doc_name).delete()
        except Exception as ex:
            print(ex)
        

if __name__ == '__main__':
    db = database('key.json')
    
    data = {'a':'a', 'b':'b'}    
    db.write('test', 'test', **data)
    db.write('test', 'test2', **data)

    # db.delete('test', '')
    # db.delete('test', 'test2')