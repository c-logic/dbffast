# dbffast

A complete recorddecode is only with recordecode performed.
The field-access is buffered.
```
with open(path+"/AUF/00001/FSCHRIFT.DBF","rb",buffering=262144) as f:
  dbfs=dbf(f)
  while dbfs.recordread():
    if dbfs["AUFNR"].startswith(tosearch):
      print(dbfp.recorddecode())
  f.close()
```
