import pyRserve
conn = pyRserve.connect()
conn.r.ls()

#we are reading off the results from disk for simplicity. 
#In actual code, this will be copied from GPA module of SlicerMorph

import pandas as pd
mydata = pd.read_csv("/Users/amaga/pyRserve/LMs/2023-12-29_10_41_10/OutputData.csv")

# some manipulation to split the centroid size and Procrustes coordinates, and sample names etc.
# these need to be replaced by PANDA frames generated by SlicerMorph in the module.

coords= mydata.copy()
coords.drop(coords.columns[0:3],axis=1,inplace=True)
conn.r.coords=coords.to_numpy()

size=mydata.centeroid.to_numpy()
conn.r.size=size

conn.eval('require(geomorph)')

#arrayspecs is a geomorph until to convert 2D matrix to a 3D array that it expects
#no.LMs is hardcoded to 51 for this example
#in reality will come from GPA module.
#k is always 3. We donot work with 2D data.

conn.eval('arr=arrayspecs(coords,p=51,k=3)')

#only variable in this linear model is size against shape (i.e., LM coordinates)
#in reality these will be provided by the user inside the GPA module
#things such as Sex, Genotype, locomotion, ecology etc

conn.voidEval('gdf=geomorph.data.frame(Size=size,Coords=arr)')

#here is the linear model 
#in the actual GPA module, this will be a user input based on the covariates they created
#size is always an option. It is derived from LM coordinates. 
conn.voidEval('mod=as.formula(Coords~Size)')

#other example models
# conn.voidEval('mod=as.formula(Coords~Size*Sex+Genotype))



#that in R returns a two matrix, first row is the intercept, and the second is the coefs of size
#each subsequent variable in the formula will be other rows.
conn.voidEval('outlm=procD.lm(mod, data=gdf)')
model=conn.eval('outlm')
#conn.eval('remove(list=ls())')
conn.shutdown 
#to shutdown Rserve. Otherwise it will stay open and contain all variable from the current session).
