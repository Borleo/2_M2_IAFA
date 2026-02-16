# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

import os
import matplotlib.pyplot as plt
import numpy as np
import cv2
import glob
import CalibUtils
from CalibTools import *


def calibrate(path):
    #Get list of images
    views, image_names = getImages(path);

    imgCalib = []
    objectPoints = []
    imgPoints = []
    imgName = []
    idx=0

    
    imgSize = views[1].shape[0:2];
    print(imgSize)

    #For each image
    for view in views:
        #Detect calibration pattern
        patternFound, corners = detectPattern(view, cols = 8, rows = 7)
        if patternFound :
            imgName.append(image_names[idx])
            idx=idx+1
            imgCalib.append(view)
            imgPoints.append(corners)
            #Add corresponding object points
            objectPoints.append(asymmetricWorldPoints(cols = 8, rows = 7, patternSize_mm = 85.0))
    
    #Calibrate camera
    rms, mtx, dist, rvecs, tvecs, pve = calibrateMono(objectPoints, imgPoints, imgSize)

    # Les variables rvecs et tvecs sont des paramètres essentiels du processus de calibration de caméra en vision 3D :
    #    - rvecs (rotation vectors) : 
    #      ce sont les vecteurs de rotation (ou paramètres de rotation, souvent en représentation de Rodrigues) 
    #      pour chaque image où le motif de calibration a été détecté.
    #      Ils décrivent l’orientation du motif de calibration (checkerboard ou cercle) dans l’espace 3D par rapport au repère de la caméra.
    #    - tvecs (translation vectors) : 
    #      ce sont les vecteurs de translation qui donnent la position du motif dans l’espace 3D, toujours par rapport au repère de la caméra.

    # Concrètement, pour chaque image utilisée lors de la calibration :
    #   - rvecs[i] donne comment le motif est "tourné" (roll/pitch/yaw) dans l’image i.
    #   - tvecs[i] donne où le centre du motif est situé en X, Y, Z dans le repère caméra pour l’image i.

    # La fonction visualizeBoards(mtx, rvecs, tvecs, ...) 
    #  - utilise ces deux variables pour reconstruire et afficher la pose du motif pour chaque vue par rapport à la caméra : 
    #  - transforme le "board" du référentiel du motif au référentiel de la caméra, affiche le motif dans un environnement 
    #   virtuel, et souvent superpose l’axe de la caméra ou l’orientation des axes.
    # Cele permet de vérifier visuellement si la calibration est cohérente : tous les motifs doivent être "devant" 
    # la caméra et positionnés avec une géométrie plausible.

    #Show pattern pose with respect to camera
    visualizeBoards(mtx, rvecs, tvecs, cols = 8, rows = 7, patternSize_mm = 85.0, cameraWidth = 0.1, cameraHeight = 0.05)

    print('\nRMS:', rms)
    print('Camera matrix:\n', mtx)
    print('Distortion coefficients: ', dist.ravel())

    #Compute correction maps
    mapx, mapy = computeCorrectionMapsMono(imgSize, mtx, dist, alpha = 1.0, xRatio = 1, yRatio = 1)

    for view in views:
    # Rectify it
        result = rectify(view, mapx, mapy)
        # Securing display
        if result is not None and hasattr(result, 'size') and result.size > 0:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            plt.imshow(result)
            plt.show()
        else:
            pass
            #print("Image rectifiée vide ou invalide, affichage ignoré.")

   
    #Plot RMS for each image
    plotRMS(pve, rms, imgName, figureName = 'RMS Plot')


path = "/Users/asriel/TP_IAFA/M2_IAFA/TP_M2IAFA/TP_M2_VISION3D/TPCalibrage/Calib"

#import glob
#image_paths = glob.glob(os.path.join(path, '*_0.png'))
#print(image_paths)

#Calibration Gauche
calibrate(os.path.join(path, '*_0.png'))


#Calibration Droite
calibrate(os.path.join(path, '*_1.png'))