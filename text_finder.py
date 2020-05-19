# import the necessary packages
from imutils.object_detection import non_max_suppression
import numpy as np
import argparse
import requests
from io import BytesIO
import time
import cv2
from PIL import Image

def unoion_coord_of_text_rect(parts):
	pass_coef = 0.1
	new_list = []
	temp = []
	for i in range(len(parts)):
		for j in reversed(range(i+1, len(parts))):
			#(startX, startY, endX, endY)
			if parts[i][1] * (1 - pass_coef) < parts[j][1] and\
				parts[i][3] * (1 + pass_coef) > parts[j][3]:

				minX = min([parts[i][0], parts[j][0]])
				minY = min([parts[i][1], parts[j][1]])
				maxX = max([parts[i][2], parts[j][2]])
				maxY = max([parts[i][3], parts[j][3]])
				temp = []
				for el in new_list:
					add_to_list = True
					if el[1] * (1 - pass_coef) < minY and\
						el[3] * (1 + pass_coef) > maxY:

						if el[1] < minY:
							add_to_list = False
							minY = el[1]
							if el[3] > maxY:
								maxY=el[3]
						else:
							if el[3] > maxY:
								add_to_list = False
								maxY = el[3]

						if el[0] < minX:
							add_to_list = False
							minX = el[0]
							if el[2] > maxX:
								maxX = el[2]
						else:
							if el[2] > maxX:
								add_to_list = False
								maxX = el[2]
					if add_to_list:
						temp.append(el)

				new_list.clear()
				new_list = temp
				new_list.append((minX, minY, maxX, maxY))
			'''
			if parts[j][1] <= parts[i][3] and parts[j][3] >= parts[i][1]:
				minX = min([parts[i][0], parts[j][0]])
				minY = min([parts[i][1], parts[j][1]])
				maxX = max([parts[i][2], parts[j][2]])
				maxY = max([parts[i][3], parts[j][3]])
				new_list.append((minX, minY, maxX, maxY))
				h_cur = (minY, maxY, minX, maxX)
				break
			'''

		
	return new_list

def sortFV(val):
	return val[1] 

def get_list_of_text_coords(img_path, min_coef=0.3, web=False):
	try:
		#image = cv2.Image
		if web:
			img_array = np.array(bytearray(requests.get(img_path).content), dtype=np.uint8)
			image = cv2.imdecode(img_array, -1)
		else:
			image = cv2.imread(img_path)
		orig = image.copy()
		(H, W) = image.shape[:2]
		(newW, newH) = (320, 320)
		rW = W / float(newW)
		rH = H / float(newH)
		image = cv2.resize(image, (newW, newH))
		(H, W) = image.shape[:2]

		# define the two output layer names for the EAST detector model that
		# we are interested -- the first is the output probabilities and the
		# second can be used to derive the bounding box coordinates of text
		layerNames = [
			"feature_fusion/Conv_7/Sigmoid",
			"feature_fusion/concat_3"]

		net = cv2.dnn.readNet("frozen_east_text_detection.pb")

		# construct a blob from the image and then perform a forward pass of
		# the model to obtain the two output layer sets
		blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
			(123.68, 116.78, 103.94), swapRB=True, crop=False)
		net.setInput(blob)
		(scores, geometry) = net.forward(layerNames)

		# grab the number of rows and columns from the scores volume, then
		# initialize our set of bounding box rectangles and corresponding
		# confidence scores
		(numRows, numCols) = scores.shape[2:4]
		rects = []
		confidences = []
		# loop over the number of rows
		for y in range(0, numRows):
			# extract the scores (probabilities), followed by the geometrical
			# data used to derive potential bounding box coordinates that
			# surround text
			scoresData = scores[0, 0, y]
			xData0 = geometry[0, 0, y]
			xData1 = geometry[0, 1, y]
			xData2 = geometry[0, 2, y]
			xData3 = geometry[0, 3, y]
			anglesData = geometry[0, 4, y]

		# loop over the number of columns
			for x in range(0, numCols):
				if scoresData[x] < min_coef:
					continue

				(offsetX, offsetY) = (x * 4.0, y * 4.0)
				# extract the rotation angle for the prediction and then
				# compute the sin and cosine
				angle = anglesData[x]
				cos = np.cos(angle)
				sin = np.sin(angle)
				# use the geometry volume to derive the width and height of
				# the bounding box
				h = xData0[x] + xData2[x]
				w = xData1[x] + xData3[x]
				# compute both the starting and ending (x, y)-coordinates for
				# the text prediction bounding box
				endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
				endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
				startX = int(endX - w)
				startY = int(endY - h)
				# add the bounding box coordinates and probability score to
				# our respective lists
				rects.append((startX, startY, endX, endY))
				confidences.append(scoresData[x])

		# apply non-maxima suppression to suppress weak, overlapping bounding
		# boxes
		boxes = non_max_suppression(np.array(rects), probs=confidences)
		# loop over the bounding boxes
		croped = []
		if web:
			response = requests.get(img_path)
			orig_img = Image.open(BytesIO(response.content))
		else:
			orig_img = Image.open(img_path)
		orig_img = orig_img.copy()
		for (startX, startY, endX, endY) in boxes:
			# scale the bounding box coordinates based on the respective
			# ratios
			startX = int(startX * rW)
			startY = int(startY * rH)
			endX = int(endX * rW)
			endY = int(endY * rH)
			croped.append((startX, startY, endX, endY))
		croped.sort(key=sortFV)
		#print(croped)

		return unoion_coord_of_text_rect(croped)
	except Exception:
		return []

def construct_arg_parser():
	# construct the argument parser and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-if", "--imgf", type=str,
		help="path to input from image")
	ap.add_argument("-it", "--imgt", type=str,
		help="path to input to image")
	return vars(ap.parse_args())

def transfer_text(img_from, coords_from, img_to, coords_to):
	croped =  []
	for coord in coords_from:
		croped.append(img_from.crop((coord[0], coord[1], coord[2], coord[3])))

	i = 0
	for coord in coords_to:
		if i != len(croped):
			img_to.paste(croped[i].resize((coord[2]-coord[0], coord[3]-coord[1])), (coord))
			i += 1
	return img_to
		


if __name__ == '__main__':
	args = construct_arg_parser()
	
	path_from = args["imgf"]
	path_to = args["imgt"]

	img_from=Image.open(path_from)
	img_to=Image.open(path_to)

	image_from = cv2.imread(path_from)
	coords_from=get_list_of_text_coords(path_from)
	image_to = cv2.imread(path_to)
	coords_to=get_list_of_text_coords(path_to)
	
	image_to_cv = cv2.imread(path_to)
	'''
	for c in coords_to:
		#img_to.crop((c[0], c[1], c[2],c[3])).show()
		cv2.rectangle(image_to_cv, (c[0], c[1]), (c[2], c[3]), (0, 255, 0), 2)
	cv2.imshow("Text Detection", image_to_cv)
	cv2.waitKey(0)
	'''
	transfer_text(img_from=img_from, coords_from=coords_from, img_to=img_to, coords_to=coords_to).show()
