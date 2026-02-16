# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

import os
import matplotlib.pyplot as plt
import numpy as np
import cv2
import glob
import CalibUtils
from CalibTools import *

#Get Left and Right images
path = "/Users/asriel/TP_IAFA/M2_IAFA/TP_M2IAFA/TP_M2_VISION3D/TPCalibrage/Calib"
viewsLeft, image_namesLeft = getImages(os.path.join(path, '*_0.png'))
viewsRight, image_namesRight = getImages(os.path.join(path, '*_1.png'))

imgCalibLeft = []
imgPointsLeft = []
imgNameLeft = []

imgCalibRight = []
imgPointsRight = []
imgNameRight = []

objectPoints = []
idx=0

print(viewsLeft[1].shape[0:2])
imgSize = viewsLeft[1].shape[0:2];

#For each image pair
for view in viewsLeft:
    #print("Left: "+image_namesLeft[idx])
    #Detect calibration pattern in the left image
    patternFoundLeft, imgPointLeft = detectPattern(viewsLeft[idx], cols = 8, rows = 7)
    if patternFoundLeft:
        #print("Right: "+ image_namesRight[idx])
        #Detect calibration pattern in the right image only if it has been found in the left one
        patternFoundRight, imgPointRight = detectPattern(viewsRight[idx], cols = 8, rows = 7)
        if patternFoundRight:
            imgNameLeft.append(image_namesLeft[idx])
            imgNameRight.append(image_namesRight[idx])
            imgCalibLeft.append(view)
            imgCalibRight.append(viewsRight[idx])
            imgPointsLeft.append(imgPointLeft)
            imgPointsRight.append(imgPointRight)
            #Add corresponding object points
            objectPoints.append(asymmetricWorldPoints(cols = 8, rows = 7, patternSize_mm = 85.0))
    idx=idx+1

#Calibrate stereo bench
rms, mtxLeft, distLeft, mtxRight, distRight, R, T, rvecs, tvecs, pve = calibrateStereo(objectPoints, imgPointsLeft, imgPointsRight, imgSize)

print('\nRMS:', rms)
print('Left Camera matrix:\n', mtxLeft)
print('Left Distortion coefficients: ', distLeft.ravel())
print('Right Camera matrix:\n', mtxRight)
print('Right Distortion coefficients: ', distRight.ravel())
print('Rotation matrix: \n',R)
print('Translation matrix: \n',T)

plotRMS(pve, rms, imgNameLeft, figureName = 'RMS Plot')

mapxLeft, mapyLeft, mapxRight, mapyRight = computeCorrectionMapsStereo(imgSize, mtxLeft, distLeft, mtxRight, distRight, R, T, alpha = 1.0, xRatio = 1, yRatio = 1)
idx = 0
for view in viewsLeft:
    resultLeft = rectify(viewsLeft[idx], mapxLeft, mapyLeft);
    resultRight = rectify(viewsRight[idx], mapxRight, mapyRight);
    
    display = cv2.hconcat([resultLeft, resultRight])       
    for i in range(0, 20):
        display = cv2.line(display, (0, int(i*display.shape[1::-1][1]/20)), (display.shape[1::-1][0]-1, int(i*display.shape[1::-1][1]/20)), (0, 0, 200))
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.imshow(display)
    plt.show()
    idx = idx+1

#Load test stereo pair
path_1="/Users/asriel/TP_IAFA/M2_IAFA/TP_M2IAFA/TP_M2_VISION3D/TPCalibrage/Test"
imgLeft = cv2.imread(os.path.join(path_1,'left_2.png'), cv2.IMREAD_GRAYSCALE)
imgRight = cv2.imread(os.path.join(path_1,'right_2.png'), cv2.IMREAD_GRAYSCALE)
imgLeft = cv2.resize(imgLeft, (1024,1024))
imgRight = cv2.resize(imgRight, (1024,1024))
resultLeft = rectify(imgLeft, mapxLeft, mapyLeft);
resultRight = rectify(imgRight, mapxRight, mapyRight);
    
display = cv2.hconcat([resultLeft, resultRight])       
for i in range(0, 20):
    display = cv2.line(display, (0, int(i*display.shape[1::-1][1]/20)), (display.shape[1::-1][0]-1, int(i*display.shape[1::-1][1]/20)), (0, 0, 200))
fig = plt.figure()
ax = fig.add_subplot(111)
plt.imshow(display)
plt.show()

disparity = getDisparity(resultLeft, resultRight)
minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(disparity)
display = cv2.convertScaleAbs(disparity, alpha = (255.0 / maxVal - minVal))
display = cv2.cvtColor(display, cv2.COLOR_GRAY2BGR)
display = cv2.applyColorMap(display, cv2.COLORMAP_JET)

mask = np.copy(disparity)
mask[np.where(disparity <= [10])] = [0]
mask[np.where(disparity > [10])] = [1]             
mask = np.uint8(mask)
disparity = cv2.bitwise_and(display, display, mask = mask)

fig = plt.figure()
plt.title("Disparity map")
ax = fig.add_subplot(111)
plt.imshow(disparity)
plt.show()

# Paramètres intrinsèques
#Matrice de la caméra (Camera Matrix) :
# Gauche : 
# [[754.0972074    0.         507.99829806]
# [  0.         754.07062882  505.19696654]
# [  0.           0.           1.        ]]
# Droite :
# [[754.87269698   0.         505.00726322]
# [  0.         754.93238378  508.67744176]
# [  0.           0.           1.        ]]
# Interprétation :
# - fx, fy : focale en pixels (~754 px) valeurs typiques pour une caméra ~1024px de large, donc cohérentes
# - cx, cy : position du centre optique (~505-508 px) quasiment au centre de l’image (dimension 1024x1024), ce qui est logique et cohérent

# Coefficients de distorsion
#  - Cinq coefficients (k1, k2, p1, p2, k3) typiques du modèle Brown-Conrady d’OpenCV.
#  - Gauche : [-0.1726, 0.1251, -0.00011, -0.00012, -0.0286]
#  - Droite : [-0.1705, 0.1232, 0.00012, 0.00032, -0.0254]

# Interprétation :
#  - Les valeurs sont :
#    - k1, k2 : distorsion radiale (typiquement négatives, quelques dixièmes) → cohérent pour des petites distorsions sur capteur moderne.
#    - p1, p2 : distorsion tangentielle (proche de zéro) → normal si l’optique n’a pas de gros défaut.
#    - k3 : correction supplémentaire (également petite).
#
# Les valeurs sont petites, typiques d’objectifs standards avec faible distorsion — tout à fait cohérent.

# Distorsion radiale: Cressemble à un effet “fisheye” plus ou moins prononcé.
#
# - Effet : Les points deviennent "courbés" vers le centre ou repoussés vers l’extérieur, comme si l’image était déformée par une lentille sphérique.
# - Cause : La plupart des objectifs (surtout grand angle) ne forment pas un plan parfait, mais produisent une image "bombée" ou "creusée"

# Distorsion tangentielle : ressemble à un glissement/décalage non homogène de tout ou partie de l’image.
#
# - Effet : Un défaut de parallélisme entre le capteur et la lentille déforme l’image, de sorte que certains points sont “tirés” ou “compensés” latéralement.
# - Cause : La lentille n’est pas parfaitement alignée avec le capteur ; du coup, la projection est “glissée” dans une direction.
# Visualisation :
# Une grille de points devient “décalée” ou “étirée” latéralement, sans symétrie radiale : les points sont déplacés horizontalement ou verticalement de façon irrégulière selon leur position dans l’image.

# Cohérence globale

# Matrice intrinsèque et distorsion : cohérentes pour une caméra de 1024x1024 px avec optique classique.
# Matrice extrinsèque : dépend de ton montage réel, mais cohérente en structure.
# RMS : trop élevé → calibration imparfaite, probablement liée à la qualité/préparation des points.


# RMS: 33.96979852163397
# Left Camera matrix: 
#  [[754.0972074    0.              507.99829806]
#  [  0.           754.07062882     505.19696654]
#  [  0.           0.               1. ]]
# Left Distortion coefficients:  [-1.72575494e-01  1.25089042e-01 -1.09982648e-04 -1.23484787e-04 -2.85509062e-02]
# Right Camera matrix: 
#  [[754.87269698   0.           505.00726322]
#  [ 0.             754.93238378 508.67744176]
#  [ 0.             0.           1. ]]
# Right Distortion coefficients: [-1.70527943e-01 1.23157980e-01 1.24893138e-04 3.20323382e-04 -2.53642737e-02]
# Rotation matrix: 
#     [[0.99582418  0.00373281 -0.09121553]
#      [0.01888789 0.96912045 0.24586336]
#      [0.0893166 -0.24655955 0.96500307]]
# Translation matrix: 
#      [[-289.04720639][-526.32680288][  96.87972328]]

# 2 quoi correspond l’image "Disparity map" ? Que représentent ses valeurs ?

# Définition : Une disparity map (carte de disparité) est une image dont chaque pixel indique 
#              le décalage horizontal (en pixels) entre la position du même point dans l’image gauche 
#               et l’image droite d’un système stéréo.

# Cette disparité est calculée à partir de la correspondance des pixels entre les deux images rectifiées.

# Valeurs :
# - Petite disparité (petite valeur) = point éloigné dans la scène.
# - Grande disparité (grande valeur) = point proche de la caméra.

# Les couleurs sur la carte sont un code visuel : 
# - chaque couleur correspond à un niveau de disparité (souvent une LUT colorée type jet).

# En résumé :L’image représente la profondeur relative : plus la couleur est "chaude" (rouge/jaune), plus le point est proche.

# Comment obtenir une carte de profondeur à partir d’une image de disparité ?
# Formule :
# Z=f⋅B / d
# où :
#   Z = profondeur (distance du point à la caméra)
#   f = distance focale (en pixels, obtenue lors de la calibration)
#   B = distance (baseline) entre les deux centres des caméras (en mm ou m)
#   d = disparité (valeur lue sur la carte pour chaque pixel)

# depth_map = (focal_length * baseline) / (disparity + 1e-6)
# points_3D = cv2.reprojectImageTo3D(disparity, Q)
# mask = disparity > min_disparity  # filtre pour points valides
# points_3D = points_3D[mask]
