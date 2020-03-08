import os 
import math
import shutil
import json
from graphics import Image, Point



def distErr(data1,data2):
	maxDis = math.sqrt(3*((255)**2))
	r = (data2['RAVG']-data1['RAVG'])**2
	g = (data2['GAVG']-data1['GAVG'])**2
	b = (data2['BAVG']-data1['BAVG'])**2
	dis = math.sqrt(r+g+b)
	return (1 - (dis)/maxDis)


def nodeVal(model1,model2):
	mName = Model(model2).modelName
	data1 = Data(Model(model1).jsonPath).getAllData()
	data2 = Data(Model(model2).jsonPath).getAllData()
	avgSum = 0
	n = len(data1['grids'])
	for i in range(n):
		avgSum += distErr(data1['grids'][i],data2['grids'][i])
	return { 'modelName':mName, 'value':round(avgSum/n,2) }

def test(inputNode):
	prediction = { 'modelName':'X', 'value': 0}
	sets = [i for i in os.listdir(f'{os.getcwd()}/Sets') if i != inputNode]
	for model in sets:
		nv = nodeVal(inputNode,model)
		print(nv['modelName'], nv['value'])
		if nv['value'] > prediction['value']:
			prediction = nv
	print(f"\n\nPrediction: {prediction['modelName']} \nNodal Average: {prediction['value']} ")




class Data():
	def __init__(self,jsonPath):
		self.file = jsonPath
		self.defaultGrid = { 'RAVG': 0, 'GAVG': 0, 'BAVG': 0, 'N': 0}

	def getAllData(self):
		with open(self.file) as infile:
			return json.load(infile)

	def setAllData(self,data):
		with open(self.file,'w') as outfile:
			json.dump(data,outfile)

	def emptyData(self,sliceIntervals):
		data = {}
		data['grids'] = [self.defaultGrid for i in range(sliceIntervals**2)]
		self.setAllData(data)		

	def getGridData(self,index):
		return self.getAllData()['grids'][index]

	def averageGrid(self,data1,data2):
		rSum = data1['RAVG'] + data2['RAVG']
		gSum = data1['GAVG'] + data2['GAVG']
		bSum = data1['BAVG'] + data2['BAVG']
		n = data1['N'] + data2['N']
		return { 'RAVG': rSum/n, 'GAVG': gSum/n, 'BAVG': bSum/n, 'N': n }

	def setGridData(self,index,data):
		jsonData = self.getAllData()
		jsonData['grids'][index] = self.averageGrid(data,self.getGridData(index))
		self.setAllData(jsonData) 




class ImageScanner():
	def __init__(self,imagePath,sliceIntervals):
		self.image = self.getImage(imagePath)
		self.sliceIntvls = sliceIntervals
		self.gridH = self.image.getHeight()/sliceIntervals
		self.gridW = self.image.getWidth()/sliceIntervals

	def getImage(self,path):
		return Image(Point(0,0),path) 

	def scanImage(self,dataObject):
		for y in range(self.sliceIntvls):
			for x in range(self.sliceIntvls):
				xs = int(self.gridW*x)
				xe = int((self.gridW*x)+self.gridW)
				ys = int(self.gridH*y)
				ye = int((self.gridH*y)+self.gridH)
				idx = x + y*self.sliceIntvls
				gdata = self.scanGrid(xs,ys,xe,ye)
				dataObject.setGridData(idx,gdata)


	def scanGrid(self,xs,ys,xe,ye):
		pxTot = (ye-ys)*(xe-xs)
		rSum = 0
		gSum = 0
		bSum = 0
		for y in range(ys,ye):
			for x in range(xs,xe):
				rgb = self.image.getPixel(x,y)
				rSum += rgb[0]
				gSum += rgb[1]
				bSum += rgb[2]
		return { 'RAVG': rSum/pxTot, 'GAVG': gSum/pxTot, 'BAVG': bSum/pxTot, 'N': 1}




class Model():
	def __init__(self,modelName,sliceIntervals = 16):
		self.modelName = modelName
		self.sliceInts = sliceIntervals
		self.basePath = f'{os.getcwd()}/Sets/{modelName}'
		self.jsonPath = f'{os.getcwd()}/Sets/{modelName}/{modelName.lower()}.json'
		if not os.path.isdir(self.basePath):
			self.createModel()

	def extractImages(self):
		return [f'{self.basePath}/{i}' for i in os.listdir(self.basePath) if i[-4:] == "gif"]

	def trainModel(self):
		for imagePath in extractImages():
			ImageScanner(imagePath,self.sliceInts).scanImage(Data(self.jsonPath)) 

	def clearModelData(self):
		Data(self.jsonPath).emptyData(self.sliceInts)


	def createModel(self):
		os.mkdir(self.basePath)
		Data(self.jsonPath).emptyData(self.sliceInts)

	def removeModel(self):
		shutil.rmtree(self.basePath)

	def renameModel(self,newName):
		newBasePath = f'{os.getcwd()}/Sets/{newName}'
		newJsonPath = f'{os.getcwd()}/Sets/{newName}/{newName.lower()}.json'
		os.rename(self.basePath,newBasePath)
		os.rename(self.basePath,newJsonPath)
		self.basePath = newBasePath
		self.jsonPath = newJsonPath
