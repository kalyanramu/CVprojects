from collections import OrderedDict
import numpy as np
import scipy.spatial.distance as dist

class CentroidTracker:
	def __init__(self, maxDisappeared = 50):
		self.nextObjectID = 0
		self.objects = OrderedDict()
		self.disappeared = OrderedDict()
		self.maxDisappeared = maxDisappeared


	def update(self,rects):

		#Situation 1 : Some Existing Objects and no  Input Objects
		#check to see if list of input rectangles is empty
		if len(rects) == 0:
			#loop over any existing objects and move them to disappeared list
			#what happened to update on existing objects list?? ans: No need to remove from existing list, just add new item to
			#disappeared list

			for objectID in self.disappeared.keys():
				self.disappeared[objectID] +=1

				#if max number of frames disappeared exceeds limit for an object, unregister the object
				if self.disappeared[objectID] >= self.maxDisappeared:
					self.unregister(objectID)

				#return early as there are no centroids or tracking info to update
				return self.objects


		# Situation 2: No Existing Objects and some Input Objects
		if len(self.objects) == 0:
			for rect in rects:
				#Calulate centroid (Since this common to situation 2 and situation 3, move it to upper level)
				centroid = (int((rect[0]+rect[2])/2.0), int((rect[1]+rect[3])/2.0))
				#Add centroid to objects list
				self.register(centroid)

		# Situation 3: Some Existing Objects and Some Input Objects
		else:

			#inputcentroids
			inputCentroids = np.zeros((len(rects),2), dtype = "int")

			for i, rect in enumerate(rects):
				inputCentroids[i] = (int((rect[0]+rect[2])/2.0), int((rect[1]+rect[3])/2.0))

			#grab the set of current object IDs and corresponding centroids
			objectIDs = list(self.objects.keys())
			objectCentroids = list(self.objects.values())

			#compute the distance between current objectCentroids and input Centroids

			D = dist.cdist(np.array(objectCentroids),inputCentroids)
			print("D :", D)

			#Find minimum value in each sort and get indices for column sort
			rows = D.min(axis=1).argsort()
			print("rows :", rows)
		
			#Find min col index of each row
			cols = D.argmin(axis=1)[rows]
			print("cols :", cols)

			#inorder to determine if we need to update, register or unregister
			#we need to keep track of which of the rows and column indexes we have already examined
			
			#Case: Number of existing object centroids <= Number of input centroids
			usedRows = set()
			usedCols = set()

			#loop over combination of (row, column) index tuples
			for (row,col) in zip(rows,cols):
				# print("row : {} , col : {}".format(row,col))
				#if we have already examined either the row or column value before, ignore it
				if row in usedRows or col in usedCols:
					continue
				# otherwise, grab the objectID for the current row,
				# set its new centroid and reset the disappeared counter
				objectID = objectIDs[row]
				self.objects[objectID] = inputCentroids[col]
				self.disappeared[objectID] = 0

				# indicate that we have examined each of the 
				# row and column indexes respectively
				usedRows.add(row)
				usedCols.add(col)

			#compute both row and column index we have NOT yet examined
			unusedRows = set(range(0, D.shape[0])).difference(usedRows)
			unusedCols = set(range(0, D.shape[1])).difference(usedCols)


			# Case: Number of exisiting object centroids >= Number of input centroids
			if D.shape[0] >= D.shape[1]:
				#loop over unused row indexes
				for row in unusedRows:
					#grab the object ID for the corresponding row
					#index and increment the disappeared counter

					objectID = objectIDs[row]
					self.disappeared[objectID] +=1

					#check to see if the number of consecutive frames
					#the object has been marked "disappeared"
					#for warrabnts deregistering the object
					if self.disappeared[objectID] > self.maxDisappeared:
						self.unregister(objectID)
			else:
				for col in unusedCols:
					self.register(inputCentroids[col])

		return self.objects

	def register(self, objectInfo):
		#key is objectID, value is objectInfo (centroid)
		self.objects[self.nextObjectID] = objectInfo
		self.disappeared[self.nextObjectID] = 0
		self.nextObjectID += 1  

	def unregister(self, objectID):
		del self.objects[objectID]
		del self.disappeared[objectID]


