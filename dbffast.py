from struct import unpack

class dbf():
	def __init__(self,f,enc="cp850"):
		self.file=f
		f.seek(0)
		self.fields={}
		self.header=dict(zip(['dbversion', 'year', 'month', 'day', 'numrecords', 'headerlen', 'recordlen'],unpack('<BBBBLHH20x',f.read(32))))
		offs=0
		self.enc=enc
		while True:
			recdata=f.read(1)
			if len(recdata)==0:
				exit(0)
			if recdata != b'\r':
				recdata+=f.read(31)
				if len(recdata)<32:
					raise RuntimeError("Record Length")

				name=recdata[:11]
				if 0 in name:
					name=name[:name.find(0)]
				field=dict(zip(['type', 'address', 'len', 'deccnt'],unpack('<cLBBH12x',recdata[11:])))
				field['offs']=offs
				self.fields[name.decode(self.enc).upper()]=field
				offs+=field['len']
			else:
				if f.read(1)==b'\x00':
					break
				else:
					raise RuntimeError("File Header")

	def __getitem__(self, key):
		key=key.upper()
		if key not in self.fields:
			return "No Field"
		if key in self.fielddecoded:
			return self.fielddecoded[key]
		field=self.fields[key]
		return self.fielddecoded[key]:=self._fielddecode(self.recordbin[field['offs']+1:field['offs']+field['len']+1],field)

	def binfield(self,key):
		key=key.upper()
		if key not in self.fields:
			return "No Field"
		field=self.fields[key]
		return self.recordbin[field['offs']+1:field['offs']+field['len']+1]

	def _fielddecode(self,flddata,field):
		if field['type']==b'N': #Number
			try:
				return float(flddata) if field['deccnt']!=0 else int(flddata)
			except:
				return None
		elif field['type']==b'L': #Boolean
			return True if flddata in b'TtYy' else False if flddata in b'FfNn' else None
		elif field['type']==b'D': #Date
			try:
				return (int(flddata[6:]),int(flddata[4:6]),int(flddata[:4]))
			except:
				return None
		elif field['type']==b'C': #Char
			return flddata.decode(self.enc)
		elif field['type']==b'M': #Memo
			return flddata
		return None

	def recordread(self,deleted=False):
		self.fielddecoded={}
		while True:
			self.recordbin=self.file.read(self.header['recordlen'])
			if len(self.recordbin)!=self.header['recordlen']:
				return False
			if self.recordbin[0]==0x2a:
				if deleted:
					self.deleted=True
					return True
				else:
					continue
			self.deleted=False
			return True

	def recorddecode(self):
		for k,v in self.fields.items():
			self.fielddecoded[k]=self._fielddecode(self.recordbin[v['offs']+1:v['offs']+v['len']+1],self.fields[k])
		return self.fielddecoded
