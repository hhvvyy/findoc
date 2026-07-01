
def chunk_text(page_text):
    full_text=[]
    start=0
    while start< len(page_text):
        chunk=page_text[start:start+1000]
        #print(len(chunk))
        start+=900
        full_text.append(chunk)
    #print(full_text)
    
    return full_text