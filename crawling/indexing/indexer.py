import lucene
from java.nio.file import Paths

# from org.apache.lucene.store import FSDirectory
# from org.apache.lucene.analysis.standard import StandardAnalyzer
# from org.apache.lucene.index import IndexWriter, IndexWriterConfig
# from org.apache.lucene.document import Document, Field, TextField, StringField, StoredField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.analysis.standard import StandardAnalyzer
from java.nio.file import Paths
from org.apache.lucene.document import Document, Field, FieldType, TextField, StringField


import json

def create_doc(page):
    metaType = FieldType()
    metaType.setStored(True) #original value saved inside index
    metaType.setTokenized(False) #avoid tokenizing url

    doc = Document()
    doc.add(Field("title", str(page.get("title")), metaType))
    doc.add(Field("body", str(page.get("body")), metaType))
    doc.add(Field("url", str(page.get("url")), metaType))
    return doc

def build_index():
    lucene.initVM()
    store = SimpleFSDirectory(Paths.get(dir))
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
    writer = IndexWriter(store, config)

    with open("output.json") as f:
        pages = json.load(f)

    print(f"Indexing ${len(pages)} files: ")

    for page in pages:
        doc = create_doc(page)
        writer.addDocument(doc)
        print(f"Indexed: {page}")

    writer.commit()
    writer.close()


if __name__ == "__main__":
    build_index()