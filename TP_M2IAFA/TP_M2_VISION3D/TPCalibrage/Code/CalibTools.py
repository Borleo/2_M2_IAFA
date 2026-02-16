# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

import os
import matplotlib.pyplot as plt
import numpy as np
import cv2
import glob
import CalibUtils



# RMS_Plot.jpg affiche les erreurs RMS (Root Mean Square error) par image pour la calibration de ta caméra 
# c’est un indicateur de la qualité globale du processus de calibration sur ton jeu d’images !
# Ce qu’il montre :
#  - Points bleus ("Per image RMS") : chaque point représente l’erreur RMS de reprojection pour chaque image utilisée.
#  - Ligne pointillée bleue ("Mean RMS") : la moyenne des RMS sur toutes les images testées.
#  - Axe X ("Image ID") : identifiant ou nom des images utilisées pour la calibration.

# Interprétation :
# Des valeurs RMS faibles (< 0.03-0.05 pixel) sont synonymes d’une bonne calibration et d’une bonne détection du motif.
# Images avec un RMS plus élevé (jusqu’à ~0.06) : souvent lié à un motif déformé, flou, ou partiellement caché ou une mauvaise détection.
# La distribution ici varie : la plupart des images sont sous la moyenne, mais quelques-unes dévient nettement (à droite du graphique).
# Ce que l'on peut améliorer selon le graphique :
# Envisager de retirer les images ayant des RMS nettement supérieurs à la moyenne pour renforcer la qualité du calibrage.
# Vérifier si ces images comportent des défauts (flous, ombres, motif partiel/déformé).
# Pour une calibration optimale, favoriser les images avec motif bien net, bien exposé et complet.
# En résumé :
# La calibration est globalement bonne si la moyenne RMS est faible (< 0.04 pixel), mais on peut améliorer la précision 
# en supprimant les "outliers" ou en améliorant la qualité des images source.
# Cette visualisation t’aide à sélectionner les meilleures images de calibration et à diagnostiquer les éventuels problèmes image par image.
# Si tu veux un script pour détecter/retirer les images "à problème", ou un commentaire sur la sélection optimale, n’hésite pas à demander !



def getImages(root_path):
    image_names = sorted(glob.glob(root_path))
    views = []
    for image_name in image_names:
        views.append(cv2.imread(image_name))
    return views, image_names

def detectPattern(frame, cols, rows):
    patternFound = False
    imgPoints = []

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 1.1.1.2 - Implémenter la fonction findChessboardCorners ou findCircleGrid en fonction du type de mire utilisé
    # C'est à vous de jouer!!!
    patternFound, imgPoints = cv2.findCirclesGrid(gray, (cols,rows), flags=cv2.CALIB_CB_SYMMETRIC_GRID)
    if patternFound:
        result = cv2.drawChessboardCorners(frame.copy(), (cols, rows), imgPoints, patternFound)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.imshow(result)
        plt.show()
    else:
        pass
        #print("Image non valable pour affichage !")
    
    return patternFound, imgPoints

def asymmetricWorldPoints(cols, rows, patternSize_mm = 1.0):
    patternPoints = []
    
    #1.1.2.1 - Créer une liste de points 3D correspondant à chaque point de la mire
    # C'est à vous de jouer!!!
    # 
    #
    for y in range(rows):
        for x in range(cols):          
            patternPoints.append([x, y, 0]) 
    #print(f'---------------------------le nombre de points {len(patternPoints)}')         
    return np.array(patternPoints).astype('float32') * patternSize_mm



def calibrateMono(objpoints, imgpoints, imgSize):
    retval = 0
    cameraMatrix = []
    distCoeffs = []
    rvecs = []
    tvecs = []
    pve = []

    #1.1.2.2 - Implémenter la fonction calibrateCameraExtended
    # objectPoints : Liste des points 3D (type float32) de la mire pour chaque image.
    # imagePoints : Liste des points détectés sur les images (en 2D).
    # imageSize : Taille (largeur, hauteur) des images.
    # cameraMatrix : Matrice intrinsèque (peut être initialisée ou laissée vide).
    # distCoeffs : Coefficients de distorsion ([k1, k2, p1, p2, k3]).
    # rvecs, tvecs : Vecteurs rotation et translation extrinsèques pour chaque vue.
    # stdDeviationsIntrinsics : Déviations standards des paramètres intrinsèques (incertitude).
    # stdDeviationsExtrinsics : Déviations standards pour extrinsèques (incertitude par vue).
    # perViewErrors : Erreur de reprojection pour chaque image.
    # flags, criteria : Options pour ajuster la calibration.  
 
    retval, cameraMatrix, distCoeffs, rvecs, tvecs, stdIntr, stdExtr, pve  = cv2.calibrateCameraExtended(objpoints,imgpoints,imgSize,None,None)
    return retval, cameraMatrix, distCoeffs, rvecs, tvecs, pve

# alpha = 1.0 : garde tout le champ de vision dans la correction, quitte à avoir des pixels non valides sur les bords.
# xRatio = 1, yRatio = 1 : map calculée à la taille d’origine de l’image (pas de redimensionnement).
def computeCorrectionMapsMono(imageSize, mtx, dist, alpha = 1.0, xRatio = 1, yRatio = 1):
    mapx = []
    mapy = []
    newImageSize = (int(imageSize[0] / xRatio), int(imageSize[1] / yRatio))

    h,  w = imageSize[:2]
    # Returns the new camera intrinsic matrix based on the free scaling parameter.
    # roi = Region Of Interest 
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
    # 1.1.3.1 - Implement initUndistortRectifyMap here
    cameraMatrix = mtx
    distCoeffs = dist
    R = np.eye(3) # identité pour calibration mono
    size = (w,h)
    m1type = cv2.CV_16SC2 # Can be CV_32FC1, CV_32FC2 or CV_16SC2, 
    newCameraMatrix = newcameramtx
    # Dans OpenCV, la fonction cv.initUndistortRectifyMap sert à créer des maps de correction 
    # pour redresser ou "rectifier" une image de caméra, en utilisant sa matrice intrinsèque (cameraMatrix), 
    # ses coefficients de distorsion (distCoeffs), et éventuellement une matrice de rectification (R) 
    # et une nouvelle matrice de projection (newCameraMatrix).
    mapx, mapy = cv2.initUndistortRectifyMap(cameraMatrix,distCoeffs,R,newCameraMatrix,size,m1type)
    #
    return mapx, mapy

# Que constatez vous sur les images résultat? A quoi cela est-il du?
# il me semble que les contours de la mire semble redréssés
# c'est peut du à l'interpolation linéaire entre l'image initiale et la maps de correction
# effectuée par initUndistortRectifyMap
def rectify(frame, mapx, mapy):
    dst = []
    # 1.1.3.2 - Implement remap here
    # First, find a mapping function from the distorted image to the undistorted image. 
    dst = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)
    ## crop the image
    # x, y, w, h = roi
    # dst = dst[y:y+h, x:x+w]
    # cv.imwrite('calibresult.png', dst)
    return dst

def calibrateStereo(objpoints, imgpointsLeft, imgPointsRight, imgSize):
    ret = 0
    retvalL = 0
    retvalR = 0
    cameraMatrixLeft = []
    distCoeffsLeft = []
    cameraMatrixRight = []
    distCoeffsRight = []
    R = np.eye(3, dtype=np.float64)   # Matrice identité pour la rotation initiale
    T = np.zeros((3, 1), dtype=np.float64)   # Vecteur nul pour la translation initiale
    rvecs = []
    tvecs = []
    pve = []

    #2.1.1 - Implémenter la fonction calibrateCameraExtended    
    retvalL, cameraMatrixLeft, distCoeffsLeft, rvecs, tvecs, pve = calibrateMono(objpoints, imgpointsLeft, imgSize)
    retvalR, cameraMatrixRight, distCoeffsRight, rvecs, tvecs, pve = calibrateMono(objpoints, imgPointsRight, imgSize)
    
    #2.1.1 - Implémenter la fonction stereoCalibrateExtended
    ret, cameraMatrixLeft, distCoeffsLeft, cameraMatrixRight, distCoeffsRight, R, T, E, F, rvecs, tvecs, pve = cv2.stereoCalibrateExtended(
                                objpoints, imgpointsLeft, imgPointsRight, 
                                cameraMatrixLeft, distCoeffsLeft, 
                                cameraMatrixRight, distCoeffsRight, 
                                imgSize,R,T) 
    
    
    return ret, cameraMatrixLeft, distCoeffsLeft, cameraMatrixRight, distCoeffsRight, R, T, rvecs, tvecs, pve


def computeCorrectionMapsStereo(imageSize, mtxLeft, distLeft, mtxRight, distRight, R, T, alpha = 1.0, xRatio = 1, yRatio = 1):
    newImageSize = (int(imageSize[0] / xRatio), int(imageSize[1] / yRatio))
    h,  w = imageSize[:2]
    # 2.2.1 - Implement stereoRectify here
    R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(
                    mtxLeft, distLeft, mtxRight, distRight,
                    imageSize, R, T,
                    None, None, None, None, None,
                    cv2.CALIB_ZERO_DISPARITY, alpha, newImageSize
                    )
    # 2.2.2 - Implement initUndistortRectifyMap here
    mapxLeft, mapyLeft = computeCorrectionMapsMono(imageSize, mtxLeft, distLeft, alpha, xRatio, yRatio) 
    mapxRight, mapyRight = computeCorrectionMapsMono(imageSize, mtxRight, distRight, alpha, xRatio, yRatio)  

    return mapxLeft, mapyLeft, mapxRight, mapyRight


def visualizeBoards(mtx, rvecs, tvecs, rows, cols, patternSize_mm, cameraWidth = 0.1, cameraHeight = 0.05):       
    figureName = 'Calibration boards visualization in camera frame'
    
    # Plot settings
    fig = plt.figure(figureName)
    #ax = fig.gca(projection='3d')
    # 111 signifie : 1 ligne, 1 colonne, 1ère sous-figure
    # Cela donne directement l’objet axe 3D
    # toujours utiliser add_subplot pour créer un axe 3D 
    ax = fig.add_subplot(111, projection='3d')

    ax.set_title(figureName)
    ax.set_xlabel('x')
    ax.set_ylabel('z')
    ax.set_zorder('-y')
    
    CalibUtils.plot_camera_frame(ax, rvecs, tvecs, mtx, cameraWidth, cameraHeight)
    CalibUtils.plot_board_frames(ax, rvecs, tvecs, cols, rows, patternSize_mm)
    CalibUtils.set_axes_equal(ax) 
    plt.show()

"""
Ce graphique représente le "RMS Plot" en fin de calibration caméra (mono), généré par la fonction plotRMS() dans ton script :
 - Axe Y ("RMS") : montre la valeur de l’erreur RMS (Root Mean Square) pour chaque image utilisée dans la calibration. 
 - C’est une mesure de la qualité de l’ajustement entre les points trouvés par le modèle et leur position réelle.
 - Axe X ("Image ID") : représente chaque image utilisée, généralement identifiée par son nom ou son index.

Points bleus ("Per image RMS") : chaque point montre l’erreur RMS d’une image spécifique. Une valeur basse (<0.03) 
 - indique que l’image est bien utilisée pour la calibration, une valeur haute montre qu’elle contribue moins bien.

Ligne bleue pointillée ("Mean RMS") : c’est la moyenne des erreurs RMS sur l’ensemble des images traitées. Elle donne une idée de la qualité générale de ta calibration.

Utilité :
 - Visualiser facilement les images qui posent problème (valeurs RMS hautes).
 - Évaluer la qualité globale et la cohérence de la calibration. Un RMS moyen bas indique une calibration précise.

À surveiller :
 - Si certains points sont beaucoup plus hauts que la moyenne, ces images sont peut-être mal cadrées, floues, ou le motif n’est pas bien détecté. 
 - Il est conseillé de les vérifier/retirer pour améliorer la précision globale.

En résumé :
 - Ce plot t’aide à analyser la qualité de chaque image dans la calibration, à identifier des images problématiques et à juger la précision finale du modèle de caméra obtenu.
"""

# Habituellement, dans la calibration OpenCV (avec la variante "extended"), 
# pve ("perViewErrors" ou "per-view errors") contient les erreurs de reprojection pour chaque image.
# Les erreurs RMS sur chaque axe (X, Y, et parfois la norme ou le Z si en 3D)
# Ou diverses composantes de l’erreur de calibration étendue

def plotRMS(pve, rms, imgNames, figureName = 'RMS Plot'):
    # Plot settings
    plt.figure(figureName)
    plt.title(figureName)
    plt.xlabel('Image ID')
    plt.ylabel('RMS')
    
    x = [os.path.splitext(os.path.basename(image))[0] for image in imgNames]

    # Choisis la partie souhaitée des RMS
    if len(pve[1]) == 2:
    # Affiche la RMS de gauche et de droite séparément
        plt.scatter(x, [rms[0] for rms in pve], label='Per image RMS (Left)', marker='o')
        plt.scatter(x, [rms[1] for rms in pve], label='Per image RMS (Right)', marker='o')
    else:
        plt.scatter(x, pve, label='Per image RMS', marker='o')

    plt.plot(x, [rms]*len(imgNames), label='Mean RMS', linestyle='--')
    plt.legend(loc='upper right')
    plt.show()



def getDisparity(left, right):
    stereo = cv2.StereoSGBM_create(
        minDisparity=1,
        numDisparities=256, 
        blockSize=15,
        uniquenessRatio=5,
        speckleWindowSize=5,
        speckleRange=5,
        disp12MaxDiff=2)
    
    disparity = stereo.compute(left,right)

    return disparity