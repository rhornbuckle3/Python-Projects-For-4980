#fullstackClustering
import numpy as np
import pandas as pd
import math as mt
import random
import scipy.io
sampData=None
def loadData(dataFile):
    global sampData
    sampData=pd.read_csv(dataFile)
    sampData=sampData.T
    sampData=sampData.values
def clusterHOME(kInput):
    norman=np.array(np.zeros((sampData.shape[0],sampData.shape[1]-1)))
    for i in range(0,sampData.shape[1]-1):
        norman[:,i]=sampData[:,0]-sampData[:,i+1]
    normanNorms=np.array(np.zeros(norman.shape[1]))
    for i in range(0,norman.shape[1]):
        normanNorms[i]=np.linalg.norm(norman[:,i],2)
    norman=np.append(norman,normanNorms.reshape((1,-1)),axis=0)
    normSort=np.copy(norman[:,norman[norman.shape[0]-1,:].argsort()])
    #switch over to working exclusively with a vector of the sorted indices
    normDiff=np.array(np.zeros((normSort.shape[0]-1,normSort.shape[1]-1)))
    #^the vector for the difference between the differences, will be one smaller, remember to increment by one for matching in the future
    for i in range(0,normSort.shape[1]-1):
        normDiff[:,i]=normSort[0:normSort.shape[0]-1,i]-normSort[0:normSort.shape[0]-1,i+1]
    normAvg=np.array(np.zeros(normDiff.shape[1]-mt.floor(normDiff.shape[1]/(kInput+1))))
    #^the vector of average change in difference norm in groups of size n/(k+1)
    normsFin=np.array(np.zeros(normDiff.shape[1]))
    for i in range(0,normDiff.shape[1]):
        normsFin[i]=np.linalg.norm(normDiff[:,i],2)
    for i in range(0,normAvg.shape[0]):
        normAvg[i]=np.sum(normsFin[i:i+mt.floor(sampData.shape[1]/(kInput+1))])
    kOne=np.argmin(normAvg)
    kOneIndex=np.where(normanNorms==normSort[normSort.shape[0]-1,1+kOne+mt.floor(mt.floor(sampData.shape[1]/(kInput+1))/2)])
    kOneIndex=np.asscalar(kOneIndex[0])
    #need to make the following 20 lines of code scalable, shouldn't be too hard
    norman=np.array(np.zeros((sampData.shape[0],sampData.shape[1]-1)))
    for i in range(0,kOneIndex):
        norman[:,i]=sampData[:,kOneIndex]-sampData[:,i]
    for i in range(kOneIndex+1,sampData.shape[1]-1):
        norman[:,i]=sampData[:,kOneIndex]-sampData[:,i]
    for i in range(0,norman.shape[1]):
        normanNorms[i]=np.linalg.norm(norman[:,i],2)
    norman=np.append(norman,normanNorms.reshape((1,-1)),axis=0)
    normSort=np.copy(norman[:,norman[norman.shape[0]-1,:].argsort()])
    normDiff=np.array(np.zeros((normSort.shape[0]-1,normSort.shape[1]-1)))
    for i in range(0,normSort.shape[1]-1):
        normDiff[:,i]=normSort[0:normSort.shape[0]-1,i]-normSort[0:normSort.shape[0]-1,i+1]
    normAvg=np.array(np.zeros(normDiff.shape[1]-mt.floor(normDiff.shape[1]/(kInput+1))))
    for i in range(0,normDiff.shape[1]):
        normsFin[i]=np.linalg.norm(normDiff[:,i],2)
    for i in range(0,normAvg.shape[0]):
        normAvg[i]=np.sum(normsFin[i:i+mt.floor(sampData.shape[1]/(kInput+1))])
    kOne=np.argmin(normAvg[range(mt.floor(sampData.shape[1]/(kInput+1)),normAvg.shape[0])])
    kTwoIndex=np.where(normanNorms==normSort[normSort.shape[0]-1,1+kOne+mt.floor(mt.floor(sampData.shape[1]/(kInput+1))/2)])
    kTwoIndex=np.asscalar(kTwoIndex[0])
    kIndex=np.array((kOneIndex,kTwoIndex))
    return kIndex
def recFunctONE(i,iBeta,xSet):
    #this is the actual classifier
    np.seterr(over=None)
    xTemp=xSet[:,i].reshape((-1,1))
    try:
        ans=1/(1+mt.e**np.matmul(np.transpose(-iBeta),xTemp))
    except FloatingPointError:
        return 0
    return ans
    #numpy overflow settings
def gradientProb(iBeta,xSet,ySet):
    gradLProb=0
    for i in range(0,xSet.shape[1]):
        gradLProb=gradLProb+np.multiply(ySet[:,i]-recFunctONE(i,iBeta,xSet),xSet[:,i].reshape((-1,1)))
    return gradLProb
def gradientAscent(eta,tol,iBeta,xSet,ySet):
    itera=0
    while(True):
        grad=np.array(iBeta)
        #print (grad)
        np.add(iBeta,eta*gradientProb(iBeta,xSet,ySet),out=iBeta)
        #if((np.argmax(abs(iBeta-grad)))<tol):
        if(itera==1000):
            return iBeta
        itera=itera+1
#construct the model for deploying log regression, details on whiteboard
def fullModel():
    clusterCenter=clusterHOME(2)
    clusterOne=clusterCenter[0]
    clusterTwo=clusterCenter[1]
    kDiff=np.linalg.norm(sampData[:,clusterCenter[0]]-sampData[:,clusterCenter[1]],2)
    #assigning labels for training data with the next 3 'for' loops
    #would need to use a interfacing 'for' loop with j=k+1 to make this bit scalable
    for i in range(0,np.argmin(clusterCenter)):
        euDistOne=np.linalg.norm(sampData[:,i]-sampData[:,clusterCenter[0]],2)
        euDistTwo=np.linalg.norm(sampData[:,i]-sampData[:,clusterCenter[1]],2)
        if((euDistOne>kDiff)and(euDistOne>euDistTwo)):
            clusterTwo=np.append(clusterTwo,i)
        if((euDistTwo>kDiff)and(euDistOne<euDistTwo)):
            clusterOne=np.append(clusterOne,i)
    for i in range(np.argmin(clusterCenter)+1,np.argmax(clusterCenter)):
        euDistOne=np.linalg.norm(sampData[:,i]-sampData[:,clusterCenter[0]],2)
        euDistTwo=np.linalg.norm(sampData[:,i]-sampData[:,clusterCenter[1]],2)
        if((euDistOne>kDiff)and(euDistOne>euDistTwo)):
            clusterTwo=np.append(clusterTwo,i)
        if((euDistTwo>kDiff)and(euDistOne<euDistTwo)):
            clusterOne=np.append(clusterOne,i)
    for i in range(np.argmax(clusterCenter)+1,sampData.shape[1]):
        euDistOne=np.linalg.norm(sampData[:,i]-sampData[:,clusterCenter[0]],2)
        euDistTwo=np.linalg.norm(sampData[:,i]-sampData[:,clusterCenter[1]],2)
        if((euDistOne>kDiff)and(euDistOne>euDistTwo)):
            clusterTwo=np.append(clusterTwo,i)
        if((euDistTwo>kDiff)and(euDistOne<euDistTwo)):
            clusterOne=np.append(clusterOne,i)
    threshOne=0.1
    threshTwo=0.9
    #^Setting thresholds for classifying
    while(True):
        print(sampData.shape[1]-clusterOne.shape[0]-clusterTwo.shape[0])
        clusterOneSize=clusterOne.shape[0]
        clusterTwoSize=clusterTwo.shape[0]
        trainSetX=np.append(sampData[:,clusterOne],sampData[:,clusterTwo],axis=1)
        trainSetY=np.array(np.zeros(clusterTwo.shape[0]))
        trainSetY.fill(1)
        trainSetY=np.append(np.array(np.zeros(clusterOne.shape[0])),trainSetY)
        trainSetY=trainSetY.reshape((1,-1))
        iBeta=np.array(np.zeros(sampData.shape[0]))
        iBeta=iBeta.reshape((-1,1))
        iBeta=gradientAscent(1e-4,1e-6,iBeta,trainSetX,trainSetY)
        #^acquiring Beta, could/should mess with mu and eta to increase accuracy
        scoreLab=np.array(np.zeros(sampData.shape[1]-clusterOne.shape[0]-clusterTwo.shape[0]))
        scoreLab.fill(-1)
        #print(scoreLab)
        l=0
        for i in range(0,sampData.shape[1]):
            if(not(((np.any(clusterOne==i))or(np.any(clusterTwo==i))))):
                scoreLab[l]=recFunctONE(i,iBeta,sampData)
                if(scoreLab[l]>threshTwo):
                    scoreLab[l]=-1
                    clusterTwo=np.append(clusterTwo,i)
                else:
                    if(scoreLab[l]<threshOne):
                        scoreLab[l]=-1
                        clusterOne=np.append(clusterOne,i)
                if(not(scoreLab[l]==-1)):
                    l=l+1
        #^classifying
        if(clusterOne.shape[0]+clusterTwo.shape[0]==sampData.shape[1]):
            #create and return labels vector here that matches original positions
            labels=np.array(np.zeros(sampData.shape[1]))
            for i in range(0,clusterOne.shape[0]):
                labels[clusterOne[i]]=0
            for i in range(0,clusterTwo.shape[0]):
                labels[clusterTwo[i]]=1
            return labels
        if((clusterOneSize==clusterOne.shape[0])and(clusterTwoSize==clusterTwo.shape[0])):
            threshOne=threshOne-0.2*(threshOne-np.average(scoreLab[np.any((scoreLab<0.5)and(scoreLab>-0.1))]))
            threshTwo=threshTwo-0.2*(threshTwo-np.average(scoreLab[np.any(scoreLab>0.5)]))
            #change 0.5 to higher value to perhaps increase accuracy
def error(labels,truthFile):
    truthData=pd.read_csv(truthFile)
    truthData=truthData.T
    truthData=truthData.values
    iterate=0
    for i in range(0,truthData.shape[1]):
        if(not(labels[i]==truthData[0,i])):
            iterate=iterate+1
    errorONE=(iterate/truthData.shape[1])*100
    iterate=0
    for i in range(0,labels.shape[0]):
        if(labels[i]==0):
            labels[i]=1
        else:
             if(labels[i]==1):
                labels[i]=0
    for i in range(0,truthData.shape[1]):
        if(labels[i]!=truthData[0,i]):
            iterate=iterate+1
    errorTwo=(iterate/truthData.shape[1])*100
    if(errorONE>errorTwo):
         return errorTwo
    else:
        return errorOne
loadData("K_Means_Data.csv")
print(error(fullModel(),"K_Means_Truth.csv"))
#Accuracy ideas:
#line 157
#increase the power of the logistic regression (more conservative training step)