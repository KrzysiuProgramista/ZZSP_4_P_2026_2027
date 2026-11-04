import csv
from .model import Event,COLUMNS

def ingest(store,path):
    result={'read':0,'imported':0,'rejected':0,'duplicates':0,'errors':[]}
    with open(path,encoding='utf-8-sig',newline='') as f,store.connection:
        reader=csv.DictReader(f)
        if not reader.fieldnames or len(reader.fieldnames)!=len(COLUMNS) or set(reader.fieldnames)!=set(COLUMNS):
            raise ValueError('Invalid header. Expected: '+','.join(COLUMNS))
        for row in reader:
            result['read']+=1
            try:event=Event.parse(row)
            except (ValueError,OverflowError,TypeError) as exc:
                result['rejected']+=1
                result['errors'].append({'line':reader.line_num,'reason':str(exc)})
                continue
            result['imported' if store.append(event) else 'duplicates']+=1
    return result
